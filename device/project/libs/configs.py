__all__ = ("Configs",)


class Configs:
    __slots__ = ("confList", "confPath",
                 "gpio", "groups", "info",
                 "networks", "pins", "scenarios",
                 "server", "device_id", "profiles")

    def __init__(self):
        self.confList = ["gpio", "groups", "info", "networks", "pins", "scenarios", "server"]
        self.confPath = "/project/configs/%s"
        self.gpio: dict[str, list[int]] = {}
        self.groups: list[dict[str, list | int | str]] = []
        self.info: list[int | float | str] = []
        self.networks: list[list[str, str]] = []
        self.pins: list[dict[str, int | str]] = []
        self.scenarios: list[list] = []
        self.server: dict[str, str | int | bool | None] = {}
        self.device_id: str = ""

        self.profiles: list[list] = []

    def loadConfigs(self):
        self.gpio.clear()
        self.info.clear()
        self.networks.clear()
        self.pins.clear()
        self.scenarios.clear()
        self.server.clear()
        if not self._loadConfigs():
            print("Ayarlar yüklenemedi...")
        if not self._checkID():
            from usys import exit

            print("KOPYALANMIŞ CİHAZ!")
            self._clearSystem(passHk=False)
            exit()
        self.device_id = self.info[3]
        self._updateScenarios()

    def updateConfig(self, confName, data: str | bytes | bytearray = None):
        if data is None:
            return False

        self._encryptConfig(confName, data)
        return True

    def _clearSystem(self, target="/", passHk=True):
        from uos import listdir, remove, rmdir

        for d in listdir(target):
            if d.startswith("boot") or (d.endswith(".hk") and passHk):
                continue
            try:
                self._clearSystem(target + '/' + d)
            except OSError:
                remove(target + '/' + d)
        try:
            rmdir(target)
        except OSError:
            pass

    def _checkID(self):
        from machine import unique_id
        from ubinascii import hexlify
        from ujson import dumps

        device_id = hexlify(unique_id()).decode('utf-8')

        saved_device_id = self.info[3]

        if saved_device_id is None:
            self.info[3] = device_id
            self._encryptConfig("info", dumps(self.info))
            return True
        elif saved_device_id != device_id:
            return False
        return True

    def _loadConfigs(self):
        from uos import remove
        ok = True

        for conf in self.confList:
            confAttr = getattr(self, conf)  # globals()[f"{conf}Conf"]
            confData = self._encryptConfig(conf)
            if confData is None:
                confData = self._dencryptConfig(conf)
                if confData is None:
                    print(conf, "ayarı yüklenemedi")
                    ok = False
            else:
                remove(f"{self.confPath % conf}.json")

            confAttr.clear()
            if isinstance(confAttr, dict):
                confAttr.update(confData)
            elif isinstance(confAttr, list):
                confAttr.extend(confData)
        return ok

    def _updateScenarios(self):

        if not self.scenarios or not self.groups:
            return

        _tempGroups = {}
        for group in self.groups:
            _tempGroups[group["id"]] = group

        for scenario in self.scenarios:
            if not scenario[4]:
                continue
            for day in scenario[1]:
                for hourSchematic in scenario[2]:
                    start = hourSchematic[0].copy()
                    start.insert(0, day)
                    end = hourSchematic[1].copy()
                    end.insert(0, day)
                    p = []
                    for _pin in scenario[3]:
                        m = [_tempGroups[_pin]["measures"], _tempGroups[_pin]["max"], _tempGroups[_pin]["pins"]]
                        p.append(m)
                    self.profiles.append([scenario[0], start, end, p])

    def _encryptConfig(self, confName, data: str | bytes | bytearray = None):
        if confName not in self.confList:
            return None

        from ujson import dumps, loads

        path = self.confPath % confName

        try:
            if data is None:
                with open(f"{path}.json", mode="r", encoding="UTF-8") as infoFile:
                    datas = infoFile.read()
            else:
                datas = data.decode("UTF-8") if isinstance(data, bytes) else data

            try:
                datas = loads(datas)
            except ValueError as E:
                print(E)
                return None
        except OSError:
            return None
        else:

            datasByte = bytearray(dumps(datas).encode("UTF-8"))
            for idx, data in enumerate(datasByte):
                datasByte[idx] = 0xFF - data

            with open(f"{path}.hk", mode="wb") as infoFile:
                infoFile.write(datasByte)

            return datas

    def _dencryptConfig(self, confName):
        if confName not in self.confList:
            return None

        from ujson import loads

        path = self.confPath % confName

        try:
            with open(f"{path}.hk", mode="rb") as infoFile:
                datas = infoFile.read()
        except OSError:
            return None
        else:
            datasByte = bytearray(datas)
            for idx, data in enumerate(datasByte):
                datasByte[idx] = 0xFF - data

            try:
                datas = loads(datasByte.decode("UTF-8"))
            except ValueError as E:
                print(E)
                return None
            return datas
