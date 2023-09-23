__all__ = ("Reader", "Writer", "DeviceClient", "DeviceDataConvertor", "commFlags")

from datetime import datetime
from json import dumps, loads, decoder
from math import log, ceil
from os import environ
from time import time
from typing import Optional
from asyncio import StreamReader, StreamWriter, Lock, AbstractEventLoop, wait_for, exceptions, ensure_future, gather, run_coroutine_threadsafe
import logging
from traceback import print_exc
from project.modules import modules, public


class commFlags:
    __slots__ = ()
    close = 0
    register = 1
    rtc = 2
    configs_to_server = 3
    system_update = 4
    last_pin_status = 5
    last_diff_pin_status = 6
    configs_from_server = 7
    order_from_server = 8
    lock = 99
    reset = 100


class incomingMsg:
    __slots__ = ("pid", "mType", "msg", "reason")

    def __init__(self, pid=0, mType=None, msg=b""):
        self.pid: int = pid
        self.mType: int = mType
        self.msg: bytes = msg
        self.reason = ""


class outgoingMsg:
    __slots__ = ("pid", "mType", "header", "body")

    def __init__(self, pid=0, mType=None, header=b"", body=b""):
        self.pid: int = pid
        self.mType: int = mType
        self.header: bytes = header
        self.body: bytes = body


def pid_gen(pid=0):
    while True:
        pid = pid + 1 if pid < 65535 else 1
        yield pid


class Registrator:
    __slots__ = ("client", "registered", "reason")

    def __init__(self, client):
        self.client = client
        self.registered = False
        self.reason = ""

    async def readClientInfo(self):
        msg: incomingMsg = await self.client.reader.readMsg()
        if msg.mType == commFlags.register:
            try:
                m = loads(msg.msg.decode("UTF-8"))
            except decoder.JSONDecodeError:
                return False
            else:
                self.client.setIfItHas(**m)
                await self.client.clearPins()
                return await self.client.addDatabase()
        return False

    async def sendRtc(self):
        await self.client.sendRtc()
        msg: incomingMsg = await self.client.reader.readMsg(10)
        ok = await self.client.responseRtc(msg)
        return ok

    async def readDeviceConfigs(self):
        msg: incomingMsg = await self.client.reader.readMsg(10)
        if msg.mType == commFlags.configs_to_server:
            try:
                m = loads(msg.msg.decode("UTF-8"))
            except decoder.JSONDecodeError:
                return False
            else:
                return await self.client.updateDatabase(**m)
        return False

    async def readLastStatus(self):
        msg: incomingMsg = await self.client.reader.readMsg(10)
        if msg.mType == commFlags.last_pin_status:
            try:
                m = loads(msg.msg.decode("UTF-8"))
            except decoder.JSONDecodeError:
                return False
            else:
                await self.client.updatePins(m)
                return True
        return False

    async def register(self):
        ok = await self.readClientInfo()
        if not ok:
            self.reason = "readClientInfo hatası"
            return False

        ok = await self.sendRtc()
        if not ok:
            self.reason = "sendRtc hatası"
            return False

        ok = await self.readDeviceConfigs()
        if not ok:
            self.reason = "readDeviceConfigs hatası"
            return False

        ok = await self.readLastStatus()
        if not ok:
            self.reason = "readLastStatus hatası"
            return False
        return True


class Base:
    __slots__ = ()

    DEBUG = True
    RETRY_BLOCK_TIME = 0.01
    secKey = b"\x31\x31"


class ioMsgHandler(Base):
    __slots__ = ()

    @classmethod
    async def writeMsg(cls, _writer, comType, data):
        oMsg: outgoingMsg = cls.prepareMsg(_writer, comType, data)
        for msg in [oMsg.header, oMsg.body]:
            _writer.write(msg)
        await _writer.drain()
        return oMsg

    @classmethod
    async def readMsg(cls, _reader) -> incomingMsg:
        secKey = await _reader.read(2)

        if secKey != cls.secKey:
            raise OSError("Bilinmeyen secKey")

        msg = incomingMsg()
        msg.mType = int.from_bytes(await _reader.read(1), "big", signed=False)
        msg.pid = int.from_bytes(await _reader.read(2), "big", signed=False)
        dataLongLongI = int.from_bytes(await _reader.read(1), "big", signed=False)
        dataLongB = await _reader.read(dataLongLongI)

        msg.msg = await _reader.read(int.from_bytes(dataLongB, "big", signed=False))

        dataLongB2 = await _reader.read(dataLongLongI)

        if dataLongB2 != dataLongB:
            raise OSError("Uzunluklar uyuşmuyor")

        return msg

    @classmethod
    def prepareMsg(cls, _writer, comType, data):
        outMsg = outgoingMsg()
        outMsg.mType = comType
        outMsg.pid = _writer.newPid
        outMsg.header = cls.createHeader(comType, outMsg.pid)
        outMsg.body = cls.createBody(data)
        return outMsg

    @classmethod
    def createHeader(cls, commType: int | bytes, pid):
        if isinstance(commType, int):
            commType = commType.to_bytes(1, "big", signed=False)
        return cls.secKey + commType + pid.to_bytes(2, "big", signed=False)

    @staticmethod
    def prepareData(data):
        if isinstance(data, dict) or isinstance(data, list):
            data = dumps(data)

        if isinstance(data, str):
            data = data.encode("UTF-8")

        elif isinstance(data, int):
            _temp = ceil(log(data, 256))
            data = data.to_bytes(_temp, "big", signed=False)

        return data

    @classmethod
    def createBody(cls, data):
        data = cls.prepareData(data)
        dataL = len(data)

        d = ceil(log(dataL, 256))

        dataLL = d.to_bytes(1, "big", signed=False)

        dataLB = dataL.to_bytes(d, "big", signed=False)

        return dataLL + dataLB + data + dataLB


class Reader:
    __slots__ = ("logger", "_reader", "lock", "is_closed")

    def __init__(self, reader: StreamReader):
        self.logger = logging.getLogger(__name__)
        self._reader = reader
        self.lock = Lock()
        self.is_closed = False

    async def readMsg(self, timeout=0) -> incomingMsg:
        async with self.lock:
            if timeout:
                try:
                    return await wait_for(ioMsgHandler.readMsg(self), timeout)
                except (exceptions.TimeoutError, exceptions.IncompleteReadError, exceptions.CancelledError, OSError) as E:
                    m = incomingMsg()
                    m.reason = str(E)
                    return m
            else:
                try:
                    return await ioMsgHandler.readMsg(self)
                except (exceptions.TimeoutError, exceptions.IncompleteReadError, exceptions.CancelledError, OSError) as E:
                    m = incomingMsg()
                    m.reason = str(E)
                    print_exc()

                    return m

    async def read(self, n=-1) -> bytes:
        if n == -1:
            data = await self._reader.read(n)
        else:
            data = await self._reader.readexactly(n)
        return data

    def feed_eof(self):
        if not self.is_closed:
            self.is_closed = True
            return self._reader.feed_eof()


class Writer:
    __slots__ = ("logger", "_writer", "pid_gen", "lock", "is_closed")

    def __init__(self, writer: StreamWriter):
        self.logger = logging.getLogger(__name__)
        self._writer = writer
        self.pid_gen = pid_gen()
        self.lock = Lock()
        self.is_closed = False  # StreamWriter has no test for closed...we use our own

    async def writeMsg(self, comType, data):
        if not self.is_closed:
            async with self.lock:
                return await ioMsgHandler.writeMsg(self, comType, data)

    @property
    def newPid(self):
        return next(self.pid_gen)

    def write(self, msg):
        if not self.is_closed:
            self._writer.write(msg)

    async def drain(self):
        if not self.is_closed:
            await self._writer.drain()

    def get_peer_info(self):
        extra_info = self._writer.get_extra_info("peername")
        return extra_info[0], extra_info[1]

    async def close(self):
        if not self.is_closed:
            async with self.lock:
                self.is_closed = True  # we first mark this closed so yields below don't cause races with waiting writes
                await self._writer.drain()
                if self._writer.can_write_eof():
                    self._writer.write_eof()
                self._writer.close()
                try:
                    await self._writer.wait_closed()  # py37+
                except AttributeError:
                    pass


class DeviceDataConvertor:
    __slots__ = ("_device_id", "_timeout",
                 "_device_name", "_site_id", "_block_id", "_system_id")

    def __init__(self):
        self._device_id: str = ""
        self._timeout: int = 10
        self._device_name: str = self.device_id
        self._site_id: int = -1
        self._block_id: int = -1
        self._system_id: int = -1

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, _newVal):
        self._device_id = str(_newVal)

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, _newVal):
        self._timeout = int(_newVal)

    @property
    def device_name(self):
        return self._device_name

    @device_name.setter
    def device_name(self, _newVal):
        self._device_name = str(_newVal)

    @property
    def site_id(self):
        return self._site_id

    @site_id.setter
    def site_id(self, _newVal):
        self._site_id = int(_newVal)

    @property
    def block_id(self):
        return self._block_id

    @block_id.setter
    def block_id(self, _newVal):
        self._block_id = int(_newVal)

    @property
    def system_id(self):
        return self._system_id

    @system_id.setter
    def system_id(self, _newVal):
        self._system_id = int(_newVal)


class DeviceClient(DeviceDataConvertor):
    __slots__ = ("writer", "reader",
                 "loop",
                 "connected",
                 "rtc_handle",
                 "changePinLock", "pinStatus", "activeProfiles",
                 "closeReason",
                 "rtcMsg"
                 )

    def __init__(self, **kwargs):
        super().__init__()
        self.writer: Optional[Writer] = None
        self.reader: Optional[Reader] = None
        self.loop: Optional[AbstractEventLoop] = None

        self.connected = False
        self.rtc_handle = None
        self.closeReason = None
        self.changePinLock: Lock = Lock()
        # self.messageLock: Lock = Lock()
        self.pinStatus: dict = {}
        self.activeProfiles: list = []
        # self.nextMsg: Optional[outgoingMsg] = None

        self.rtcMsg: Optional[outgoingMsg] = None

        self.setIfItHas(**kwargs)

    def setIfItHas(self, **datas):
        for key, data in datas.items():
            if hasattr(self, key):
                setattr(self, key, data)

    async def clearPins(self):
        async with self.changePinLock:
            self.pinStatus.clear()

    async def updatePins(self, data):
        async with self.changePinLock:
            self.pinStatus.update(data["pins"])
            self.activeProfiles = data["activeProfiles"]

    async def addDatabase(self):
        return modules.database.devices.add(dict(device_id=self.device_id)).success

    async def updateDatabase(self, **datas):
        self.setIfItHas(**datas)
        datas.update({"timeout": self.timeout})
        return modules.database.devices.update(["device_id", self.device_id], datas, createNew=True).success

    def sendingCommData(self, func, *args, timeout=10):
        if not self.connected:
            return outgoingMsg()
        _sendingTime = time()

        task = run_coroutine_threadsafe(
            func(*args),
            loop=modules.loop,
        )
        while not task.done():
            if _sendingTime + timeout < time():
                return outgoingMsg()
        return task.result()

    async def _sendReset(self) -> outgoingMsg:
        return await self.writer.writeMsg(commFlags.reset, {})

    def sendReset(self) -> outgoingMsg:
        return self.sendingCommData(self._sendReset)

    async def _sendConfig(self, name, data) -> outgoingMsg:
        if type(data) not in [bytes, str]:
            data = dumps(data)
        return await self.writer.writeMsg(commFlags.configs_from_server, dict(name=name, data=data))

    def sendConfig(self, name, data) -> outgoingMsg:
        return self.sendingCommData(self._sendConfig, name, data)

    async def _sendUpdate(self, data) -> outgoingMsg:
        return await self.writer.writeMsg(commFlags.system_update, data)


    def sendUpdate(self, name) -> outgoingMsg:
        with open(f"{environ['PWD']}/deviceUpdates/{name}.tar", mode="rb") as f:
            data = f.read()
        return self.sendingCommData(self._sendUpdate, data)

    async def _sendLock(self, data) -> outgoingMsg:
        return await self.writer.writeMsg(commFlags.lock, data)

    def sendLock(self, _status) -> outgoingMsg:
        return self.sendingCommData(self._sendLock, dict(hydrate=_status))



    async def responseRtc(self, msg: incomingMsg):
        if msg.mType == commFlags.rtc:
            try:
                if not isinstance(msg.msg, str):
                    msg.msg = msg.msg.decode("UTF-8")
                m = loads(msg.msg)
            except decoder.JSONDecodeError as E:
                self.connected = False
                return False
            else:
                if m["pid"] == self.rtcMsg.pid:
                    self.connected = True
                    self.rtc_handle = self.loop.call_later(int(self.timeout * 0.7), self.sendingCommData, self.sendRtc)
                    # self.rtc_handle = self.loop.call_later(10, self.sendingCommData, self.sendRtc)
                    return True
        self.connected = False
        return False

    async def sendRtc(self):
        if self.writer is None:
            return
        rtcNow = datetime.now().timetuple()
        rtcDate = f"{rtcNow.tm_year},{rtcNow.tm_mon},{rtcNow.tm_mday},{rtcNow.tm_wday},{rtcNow.tm_hour},{rtcNow.tm_min},{rtcNow.tm_sec},0"
        self.rtcMsg: outgoingMsg = await self.writer.writeMsg(commFlags.rtc, rtcDate)

    async def register(self) -> Registrator:
        registrator = Registrator(self)
        registrator.registered = await registrator.register()
        self.connected = registrator.registered
        return registrator

    async def close(self):
        self.connected = False
        if self.rtc_handle is not None:
            self.rtc_handle.cancel()
        try:
            await self.writer.close()
        except (OSError, AttributeError):
            pass
        try:
            self.reader.feed_eof()
        except (OSError, AttributeError):
            pass
        return self.closeReason
