__all__ = ("PinSystem",)


class PinSystem:
    __slots__ = ("system", "_changed", "pins", "configs",
                 "changePinLock", "currentPinLock",
                 "_currentPins", "_changedPins", "_tempChangedPins",
                 "activeProfiles")

    def __init__(self, system):
        from machine import Pin
        from _thread import allocate_lock as Lock
        import dht  # noqa

        self.system = system
        self.configs = self.system.configs
        self._changed = False
        self.pins: dict[int, Pin | dht.DHT11 | dht.DHT22] = {}
        self.changePinLock: Lock = Lock()
        self.currentPinLock: Lock = Lock()
        self._changedPins: dict[str, dict[str, int | list | str | float]] = {}
        self._currentPins: dict[str, dict[str, int | list | str | float]] = {}
        self._tempChangedPins: dict[str, dict[str, int | list | str | float]] = {}
        self.activeProfiles: set = set()
        self.setupPins()

    @property
    def changed(self):
        return self._changed

    @changed.setter
    def changed(self, _newStatus):
        self._changed = _newStatus
        if not _newStatus:
            self._tempChangedPins = {}
            self.activeProfiles.clear()

    @property
    def currentPins(self):
        with self.currentPinLock:
            return self._currentPins

    @currentPins.setter
    def currentPins(self, _newChanged: dict):
        with self.currentPinLock:
            self._currentPins.update(_newChanged)

    @property
    def changedPins(self):
        with self.changePinLock:
            return self._changedPins

    @changedPins.setter
    def changedPins(self, _newChanged: dict):
        with self.changePinLock:
            if not _newChanged:
                self._changedPins.clear()
                return
            self.currentPins = _newChanged
            self._changedPins.update(_newChanged)

    def closeAllPins(self):
        for pinInf in self.configs.pins:
            pinTyp = pinInf.get("mode", "RELAY")
            if pinTyp == "RELAY":
                pinNumber = pinInf["num"]
                self.pins[pinNumber].off()

    def setCurrent(self):
        self.changedPins = self._tempChangedPins

    def getMeasure(self, pinNo):
        """
            return [humidity, temperature]
        :param pinNo:
        :return:
        """

        pinInf = [x for x in self.configs.pins if x["num"] == pinNo]

        if not pinInf:
            self._tempChangedPins[pinNo]["value"] = [200, 200]
            return [200, 200]
        pinInf = pinInf[0]
        pinTyp = pinInf.get("mode", "RELAY")

        if pinTyp in ["DHT11", "DHT22"] \
                and int(pinNo) in self.configs.gpio["outputs"] \
                and int(pinNo) in self.configs.gpio["inputs"]:
            try:
                measureObj = self.pins[pinNo]
                measureObj.measure()
                measure = [measureObj.humidity(), measureObj.temperature()]
            except (OSError, AttributeError, NameError):
                measure = [200, 200]
        else:
            measure = [200, 200]

        if self.currentPins[pinNo].get("value", None) != measure:
            self.changed = True
            self._tempChangedPins.setdefault(pinNo, {})
            self._tempChangedPins[pinNo]["value"] = measure

        return measure

    def setValue(self, pinNo, value):

        if not self.system.hydrate:
            return

        pinInf = [x for x in self.configs.pins if x["num"] == pinNo]

        if not pinInf:
            return
        pinInf = pinInf[0]
        pinTyp = pinInf.get("mode", "RELAY")

        if pinTyp == "RELAY" and int(pinNo) in self.configs.gpio["outputs"]:
            newVal = 1 if value else 0
            if self.currentPins[pinNo].get("value", None) != newVal:
                self.changed = True
                self.pins[pinNo].value(newVal)
                self._tempChangedPins.setdefault(pinNo, {})
                self._tempChangedPins[pinNo]["value"] = newVal

    def setupPins(self):
        import dht  # noqa
        from utime import sleep
        from machine import Pin

        isThereDht: bool = False
        inputs = self.configs.gpio["inputs"]
        outputs = self.configs.gpio["outputs"]

        for pinInf in self.configs.pins:
            pinNumber = pinInf["num"]
            self._tempChangedPins.setdefault(pinNumber, {})

            pinTyp = pinInf.get("mode", "RELAY")
            if pinTyp == "DHT11":
                if pinNumber in inputs and pinNumber in outputs:
                    self.pins[pinNumber] = dht.DHT11(Pin(pinNumber))
                    self._tempChangedPins[pinNumber]["value"] = [200, 200]
                    isThereDht = True

            elif pinTyp == "DHT22":
                if pinNumber in inputs and pinNumber in outputs:
                    self.pins[pinNumber] = dht.DHT22(Pin(pinNumber))
                    self._tempChangedPins[pinNumber]["value"] = [200, 200]
                    isThereDht = True

            else:
                if pinNumber in outputs:
                    pin = Pin(pinNumber, Pin.OUT, drive=Pin.DRIVE_0)  # type: ignore[call-arg]
                    pin.off()
                    self.pins[pinNumber] = pin
                    self._tempChangedPins[pinNumber]["value"] = 0

        self.changedPins = self._tempChangedPins

        if isThereDht:
            sleep(3)

    def shutdown(self):
        self.closeAllPins()
