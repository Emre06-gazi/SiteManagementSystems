__all__ = ("System",)

from ujson import loads, dumps
from utime import sleep
from uos import listdir, remove

from project.libs.client import incomingMsg
from project.libs.globals import commFlags, updateRtc


class System:
    def __init__(self):
        from project.libs.configs import Configs
        from project.libs.client import Client
        from project.libs.network import Network
        from project.libs.pinSystem import PinSystem
        from machine import Timer, Pin

        self.continueRun = True
        self._hydrate = False if "lock" in listdir() else True

        self.commLedTimer = Timer(0)
        self.commLed = Pin(0, Pin.OUT, drive=Pin.DRIVE_0)  # type: ignore[call-arg]
        self.commLed.off()

        self.configs = Configs()
        self.configs.loadConfigs()

        self.pinSystem = PinSystem(self)

        self.network = Network(self,
                               self.configs.networks)

        self.client = Client(self,
                             self.configs.device_id,
                             **self.configs.server
                             )

        self.client.fromServer = self.fromServer

    def canHydrate(self):
        if not self.hydrate:
            self.pinSystem.closeAllPins()
            return False
        return True

    @property
    def hydrate(self):
        return self._hydrate

    @hydrate.setter
    def hydrate(self, _lockStatus):
        if _lockStatus:
            with open("lock", "w+") as lockFile:
                lockFile.write("")
            self._hydrate = False
            print("Cihaz kilitlendi")
        else:
            try:
                remove("lock")
            except OSError:
                pass
            finally:
                self._hydrate = True
            print("Cihazın kilidi açıldı")

    def fromServer(self, msg: incomingMsg):
        if msg.mType == commFlags.configs_from_server:
            try:
                _msg = loads(msg.msg)
            except ValueError:
                return
            else:
                # noinspection PyProtectedMember
                self.configs._encryptConfig(_msg["name"], _msg["data"])
        elif msg.mType == commFlags.reset:
            from machine import reset
            self.client.continueRun = False
            self.client.disconnect()
            sleep(2)
            reset()
        elif msg.mType == commFlags.rtc:
            updateRtc(msg)
            self.client.respondRtc(msg)
        elif msg.mType == commFlags.lock:
            try:
                _msg = loads(msg.msg)
            except ValueError:
                return
            else:
                # noinspection PyProtectedMember
                self.hydrate = _msg["hydrate"]

    def start(self):
        from _thread import start_new_thread as Thread, stack_size
        self.continueRun = True
        self.network.connect()
        self.client.connect()
        # stack_size(40960)
        Thread(self.client.processio, ())

    def blinkCommLed(self, *_args):
        self.commLed.value(self.commLed.value() ^ 1)

    def putMsg(self, msgId, msg):
        self.client.createOut(msgId, msg)

    def shutdown(self):
        self.client.shutdown()
        self.network.disconnect()
        self.commLedTimer.deinit()
        self.commLed.off()
