__all__ = ("Network",)


class Network:
    __slots__ = ("system", "networks", "sta", "ip")

    def __init__(self, system, networks):
        from network import WLAN, STA_IF  # noqa

        self.system = system
        self.networks: list[list[str, str]] = networks
        self.sta = WLAN(STA_IF)

        self.ip: str = ""

    def connect(self):
        from machine import Timer
        from utime import time

        self.system.commLedTimer.init(mode=Timer.PERIODIC, period=1000, callback=self.system.blinkCommLed)
        if self.sta.active():
            self.sta.active(False)
            while self.sta.active():
                continue

        self.sta.active(True)
        while not self.sta.active():
            continue

        self.system.commLedTimer.init(mode=Timer.PERIODIC, period=500, callback=self.system.blinkCommLed)

        while True:
            for ssid, password in self.networks:
                cTime = time() + 10
                self.sta.connect(ssid, password)
                while not self.sta.isconnected():
                    if cTime < time():
                        self.sta.disconnect()
                        break
                    continue
                break
            if self.sta.isconnected():
                break

        self.ip = self.sta.ifconfig()[0]
        print(self.sta.ifconfig())

    def disconnect(self):
        if self.sta.active():
            self.sta.active(False)
            while self.sta.active():
                continue
