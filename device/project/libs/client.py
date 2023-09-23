__all__ = ("Client", "incomingMsg")

from utime import sleep
from ujson import dumps
from uos import remove, mkdir
from math import log, ceil
from gc import collect
from _thread import allocate_lock as Lock
from machine import Timer
from project.libs import utar
from usocket import socket, getaddrinfo

from project.libs.globals import updateRtc, commFlags, DEBUG


class incomingMsg:
    __slots__ = ("pid", "mType", "msg")

    def __init__(self, pid=0, mType=None, msg=b""):
        self.pid: int = pid
        self.mType: int = mType
        self.msg: bytes = msg


class outgoingMsg:
    __slots__ = ("pid", "mType", "header", "body", "success")

    def __init__(self, pid=0, mType=None, header=b"", body=b""):
        self.pid: int = pid
        self.mType: int = mType
        self.header: bytes = header
        self.body: bytes = body
        self.success: bool = False


def pid_gen(pid=0):
    while True:
        pid = pid + 1 if pid < 65535 else 1
        yield pid


pid_gen = pid_gen()
log256 = log(256)


def _saveUpdate(_reader):
    _takeByte = 256
    _reader.__recv(2)
    dataLongLongB = _reader.__recv(1)
    dataLongLongI = int.from_bytes(dataLongLongB, "big")

    dataLongB = _reader.__recv(dataLongLongI)
    dataLongI = int.from_bytes(dataLongB, "big")
    with open("update.tar", "wb") as updateFile:
        while True:
            if dataLongI - _takeByte > 0:
                data = _reader.__recv(_takeByte)
            else:
                data = _reader.__recv(dataLongI)
            dataLongI -= _takeByte
            updateFile.write(data)
            if dataLongI <= 0:
                break

    dataLongB2 = _reader.__recv(dataLongLongI)

    if dataLongB2 != dataLongB:
        raise OSError("Serverden bozuk veri geldi")


def saveUpdate(_reader):
    try:
        _saveUpdate(_reader)
    except OSError as E:
        print("Güncelleme başarısız:", E)
    else:
        t = utar.TarFile("update.tar")
        for i in t:
            if i.type == utar.DIRTYPE:
                mkdir(i.name)
            else:
                f = t.extractfile(i)
                with open(i.name, "wb") as of:
                    of.write(f.read())
    finally:
        try:
            remove("update.tar")
        except OSError:
            pass


class Base:
    __slots__ = ()
    RETRY_BLOCK_TIME = 0.01
    secKey = b"\x31\x31"


class Registrator:
    def __init__(self, client):
        self.client = client

    def sendClientInfo(self):
        return self.client.writer.send(
            commFlags.register,
            dict(timeout=self.client.keepalive, device_id=self.client.device_id)
        )

    def readRtc(self):
        msg: incomingMsg = self.client.reader.recv(60)
        if msg is not None:
            try:
                ok = updateRtc(msg)
                if not ok:
                    return outgoingMsg()

                return self.client.respondRtc(msg)

            except (Exception,) as E:
                if DEBUG:
                    print(E)
                return outgoingMsg()
        return outgoingMsg()

    def sendDeviceConfigs(self):
        return self.client.writer.send(
            commFlags.configs_to_server,
            {
                # "gpio": self.client.system.configs.gpio,
                "groups": self.client.system.configs.groups,
                # "network": self.client.system.configs.networks,
                "pins": self.client.system.configs.pins,
                "scenarios": self.client.system.configs.scenarios,
                # "server": self.client.system.configs.server,
                "site_id": self.client.system.configs.info[0],
                "block_id": self.client.system.configs.info[1],
                "system_id": self.client.system.configs.info[2],
                # "device_unique_id": self.client.system.configs.info[3],
                "device_name": self.client.system.configs.info[4],
                "system_version": self.client.system.configs.info[5]
            }
        )

    def sendLastStatus(self):
        return self.client.sendLastStatus()

    def register(self):

        if not self.sendClientInfo().success:
            if DEBUG:
                print("ClientInfo başarısız")
            return False

        if not self.readRtc().success:
            if DEBUG:
                print("readRtc başarısız")
            return False

        if not self.sendDeviceConfigs().success:
            if DEBUG:
                print("sendDeviceConfigs başarısız")
            return False

        if not self.sendLastStatus().success:
            if DEBUG:
                print("sendLastStatus başarısız")
            return False

        return True


class Reader(Base):
    __slots__ = ("client", "sock")

    def __init__(self, client, sock):
        self.client = client
        self.sock = sock

    def __recv(self, n):
        """
        Private class method.

        :param n: Expected length of read bytes
        :type n: int
        :return:

        Notes:
        Current usocket implementation returns None on .read from
        non-blocking socket with no data. However, OSError
        EAGAIN is checked for in case this ever changes.
        """

        if n < 0:
            raise SyntaxError("Okuma uzunluğu belirtilmedi")

        msg = b''
        while len(msg) < n:
            try:
                rbytes = self.sock.read(n - len(msg))
            except OSError as e:
                if e.args[0] == 11:  # EAGAIN / EWOULDBLOCK
                    sleep(self.RETRY_BLOCK_TIME)
                    continue
                raise OSError(f"Okumada sorun oldu {e}")
            except AttributeError:
                raise OSError("Server bağlı değil")
            if rbytes == b'':
                raise OSError("Server kapatıldı")
            elif rbytes is None:
                return None
            else:
                msg += rbytes
        return msg

    def _recv(self, timeout):
        if not timeout:
            self.sock.setblocking(False)

        secKey = self.__recv(2)
        if secKey is None:
            return None

        if secKey != self.secKey:
            raise OSError("secKey uyuşmuyor")

        self.sock.setblocking(True)
        msg = incomingMsg()

        comType = self.__recv(1)
        msg.mType = int.from_bytes(comType, "big")

        if msg.mType == commFlags.system_update:
            saveUpdate(self)
            return incomingMsg()

        pid = self.__recv(2)
        msg.pid = int.from_bytes(pid, "big")
        dataLongLongB = self.__recv(1)
        dataLongLongI = int.from_bytes(dataLongLongB, "big")

        dataLongB = self.__recv(dataLongLongI)
        dataLongI = int.from_bytes(dataLongB, "big")

        data = self.__recv(dataLongI)
        msg.msg = data
        dataLongB2 = self.__recv(dataLongLongI)

        if dataLongB2 != dataLongB:
            raise OSError("Serverden bozuk veri geldi")

        return msg

    def recv(self, timeout=0):
        try:
            return self._recv(timeout)
        except OSError as E:
            if DEBUG:
                print(E)
            self.client.disconnect()


class Writer(Base):
    __slots__ = ("client", "sock")

    def __init__(self, client, sock):
        self.client = client
        self.sock = sock

    def __send(self, bytes_wr, force=False) -> None:
        while self.client.continueRun or force:
            try:
                out = self.sock.send(bytes_wr)
            except AttributeError:
                raise OSError("Server bağlı değil")
            except OSError as e:
                if e.args[0] == 11:  # EAGAIN / EWOULDBLOCK
                    sleep(self.RETRY_BLOCK_TIME)
                    continue
                else:
                    raise OSError(f"Yazmada sorun oldu {e}")
            else:
                if out != len(bytes_wr):
                    raise OSError(f"Servere tüm veri gönderilemedi")
                break

    def _send(self, msgObj: outgoingMsg) -> bool:
        try:
            self.sock.settimeout(60)
            self.sock.setblocking(True)
            for _data in [msgObj.header, msgObj.body]:
                self.__send(_data)
        except OSError as E:
            self.client.disconnect()
            if DEBUG:
                print(E)
            return False
        else:
            return True

    def send(self, msgType, msgData) -> outgoingMsg:
        msgObj = self.client.createOut(msgType, msgData)
        msgObj.success = self._send(msgObj)
        return msgObj


class Client(Base):
    __slots__ = ("system", "device_id", "sock",
                 "host", "port", "ssl", "ssl_params", "keepalive",
                 "msgLock", "changedPins", "currentPins",
                 "_serverConnected", "_serverConnecting", "_serverClosing",
                 "reader", "writer", "fromServer"
                 )

    def __init__(self, system, device_id, host, port=0, keepalive=86400, ssl=False, ssl_params=None):
        """
            Default constructor, initializes Client object.
            :param system: device system
            :type system: Any
            :param device_id:  Unique Device ID attached to client.
            :type device_id: str
            :param host: host address.
            :type host str
            :param port: port, typically 500. If unset, the port number will default to 500 of 502 base on ssl.
            :type port: int
            :param keepalive: The Keep Alive is a time interval measured in seconds since the last
                              correct control packet was received.
            :type keepalive: int
            :param ssl: Require SSL for the connection.
            :type ssl: bool
            :param ssl_params: Required SSL parameters. Kwargs from function ssl.wrap_socket.
                               See documentation: https://docs.micropython.org/en/latest/library/ssl.html#ssl.ssl.wrap_socket
                               For esp8266, please refer to the capabilities of the axTLS library applied to the micropython port.
                               https://axtls.sourceforge.net
            :type ssl_params: dict
        """

        self.system = system

        self.device_id: str = device_id

        self.sock: socket = None
        self.host: str = host

        self.port: int = 502 if ssl else 500 if not port else port

        self.ssl: bool = ssl
        self.ssl_params: dict = ssl_params if ssl_params else {}

        self.keepalive: int = keepalive

        self.msgLock: Lock = Lock()

        self._serverConnected: bool = False
        self._serverConnecting: bool = False
        self._serverClosing: bool = False

        self.reader: Reader | None = None
        self.writer: Writer | None = None

    @property
    def activeProfiles(self):
        return self.system.pinSystem.activeProfiles

    @property
    def currentPins(self):
        return self.system.pinSystem.currentPins

    @property
    def changedPins(self):
        return self.system.pinSystem.changedPins

    @changedPins.setter
    def changedPins(self, _newVal):
        self.system.pinSystem.changedPins = _newVal

    @property
    def continueRun(self) -> bool:
        return self.system.continueRun

    @continueRun.setter
    def continueRun(self, _status) -> None:
        self.system.continueRun = _status

    @property
    def serverConnected(self) -> bool:
        return self._serverConnected

    @serverConnected.setter
    def serverConnected(self, _status) -> None:
        self._serverConnected = _status

        if _status:
            self.system.commLedTimer.deinit()
            self.system.commLed.on()

    @property
    def serverConnecting(self) -> bool:
        return self._serverConnecting

    @serverConnecting.setter
    def serverConnecting(self, _status) -> None:
        self._serverConnecting = _status
        if _status:
            self.system.commLedTimer.init(mode=Timer.PERIODIC, period=100, callback=self.system.blinkCommLed)

    @property
    def serverClosing(self) -> bool:
        return self._serverClosing

    @serverClosing.setter
    def serverClosing(self, _status) -> None:
        self._serverClosing = _status
        if _status:
            self.system.commLedTimer.deinit()
            self.system.commLed.off()

    def respondRtc(self, rtcMsg) -> outgoingMsg:
        return self.writer.send(commFlags.rtc, dict(pid=rtcMsg.pid))

    def createHeader(self, commType: int | bytes, pid) -> bytes:
        if isinstance(commType, int):
            commType = commType.to_bytes(1, "big")
        return self.secKey + commType + pid.to_bytes(2, "big")

    @staticmethod
    def prepareData(data) -> bytes:
        if isinstance(data, dict) or isinstance(data, list):
            data = dumps(data)

        if isinstance(data, str):
            data = data.encode("UTF-8")

        elif isinstance(data, int):
            _temp = ceil(log(data) / log256)
            data = data.to_bytes(_temp, "big")

        return data

    def createBody(self, data) -> bytes:
        data = self.prepareData(data)
        dataL = len(data)

        d = ceil(log(dataL) / log256)

        dataLL = d.to_bytes(1, "big")

        dataLB = dataL.to_bytes(d, "big")

        return dataLL + dataLB + data + dataLB

    @property
    def newPid(self) -> int:
        return next(pid_gen)

    def createOut(self, comType: int, bodyData) -> outgoingMsg:
        outMsg = outgoingMsg()
        outMsg.mType = comType
        outMsg.pid = self.newPid
        outMsg.header = self.createHeader(comType, outMsg.pid)
        outMsg.body = self.createBody(bodyData)
        return outMsg

    def sendLastDiffStatus(self) -> None:
        with self.msgLock:
            if self.changedPins:
                ok = self.writer.send(commFlags.last_diff_pin_status, dict(activeProfiles=list(self.activeProfiles), pins=self.changedPins)).success
                if ok:
                    self.changedPins = {}

    def sendLastStatus(self) -> outgoingMsg:
        with self.msgLock:
            return self.writer.send(commFlags.last_pin_status, dict(activeProfiles=list(self.activeProfiles), pins=self.currentPins))

    def processio(self) -> None:
        try:
            while self.serverConnected:
                rec = self.reader.recv()
                if rec is not None:
                    self.fromServer(rec)
                self.sendLastDiffStatus()
                if self.sock is None and self.continueRun:
                    self.connect()
                collect()
                sleep(.1)
        except MemoryError:
            self.shutdown()

    def _connect(self, addr) -> bool:
        try:
            self.sock.connect(addr)
        except (AttributeError, OSError) as E:
            if DEBUG:
                print(E)
            return False
        else:
            if self.ssl:
                import ussl
                self.sock = ussl.wrap_socket(self.sock, **self.ssl_params)  # type: ignore[call-arg]
            self.writer = Writer(self, self.sock)
            self.reader = Reader(self, self.sock)
            return True

    def connect(self) -> None:

        self.serverConnecting = True

        while self.continueRun:
            self.disconnect()
            collect()
            ai = getaddrinfo(self.host, self.port)[0]
            self.sock = socket(ai[0], ai[1], ai[2])
            connected = self._connect(ai[-1])
            collect()

            if not connected:
                sleep(1)
                continue

            registrator = Registrator(self)
            if not registrator.register():
                sleep(1)
                if DEBUG:
                    print("registrator hatası")
                continue
            with self.msgLock:
                self.changedPins = {}

            self.serverConnected, self.serverConnecting = True, False
            if DEBUG:
                print("Servere bağlanıldı")
            collect()
            return

    def sendDisconnectMessage(self) -> outgoingMsg:
        with self.msgLock:
            msgObj = self.createOut(commFlags.close, dict(timeout=1, device_id=self.device_id))
            if self.sock is None:
                msgObj.success = False
                return msgObj
            while True:
                try:
                    self.sock.setblocking(True)
                    self.sock.settimeout(60)
                    for _data in [msgObj.header, msgObj.body]:
                        self.sock.send(_data)
                except AttributeError:
                    msgObj.success = False
                    break
                except OSError as E:
                    if E.args[0] == 11:  # EAGAIN / EWOULDBLOCK
                        sleep(self.RETRY_BLOCK_TIME)
                        continue
                    if DEBUG:
                        print(E)
                    msgObj.success = False
                    break
                else:
                    msgObj.success = True
                    break
            return msgObj

    def disconnect(self) -> None:
        if DEBUG:
            print("server kapatılıyor")
        if self.serverClosing:
            return

        self.serverConnected, self.serverClosing, self.serverConnecting = False, True, True

        if self.sock is None:
            self.serverClosing = False
            return
        self.sendDisconnectMessage()
        try:
            self.sock.close()
        except AttributeError:
            pass
        except OSError:
            pass

        self.sock, self.writer, self.reader, self.serverClosing = None, None, None, False

        collect()

    def shutdown(self) -> None:
        self.continueRun = False
        self.disconnect()

    def fromServer(self, msg: incomingMsg) -> None:
        print(msg.mType, msg.msg)
