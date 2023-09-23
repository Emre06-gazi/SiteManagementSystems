# -*- coding: utf-8 -*-

__all__ = ("Database",)

import sqlite3
import json
from sqlite3.dbapi2 import Connection
from json import dumps, loads, JSONDecodeError
from traceback import print_exc
from typing import Any

import bcrypt
from flask import session

from project.modules import modules

dbName = "test.db"
usersTableName = "users"
devicesTableName = "devices"
systemsTableName = "systems"
sitesTableName = "sites"

cnx: Connection = sqlite3.connect(dbName, check_same_thread=False)
cnx.execute("PRAGMA encoding = 'UTF-8';")
handleErrors = (
    (KeyboardInterrupt, SystemExit),
    (Exception,)
)

DEBUG = False


class handledProcessData:
    __slots__ = ("success", "desc", "data")

    def __init__(self, success=False, desc="", data=None):
        self.success = success
        self.desc = desc
        self.data = data

    def __getitem__(self, item):
        return getattr(self, item)

    def __str__(self, indent=2):
        return self.render(indent=indent)

    def render(self, indent=None):
        return dumps(dict(success=self.success, desc=self.desc, data=self.data), ensure_ascii=False, indent=indent)


def handleCursor(funct):
    def __inner(*args, **_kwargs):
        _close = False
        if _kwargs.get("_cursor", None) is None:
            _cursor = cnx.cursor()
            _kwargs.update({"_cursor": _cursor})
            _close = True

        try:
            return funct(*args, **_kwargs)
        finally:
            cnx.commit()
            if _close:
                _kwargs["_cursor"].close()

    return __inner


def handleProcess(funct):
    def __inner(*args, **kwargs):
        try:
            return handledProcessData(success=True, desc="Success", data=funct(*args, **kwargs))
        except (KeyboardInterrupt, SystemExit):
            return handledProcessData(success=False, desc="Server closed", data=None)
        except (Exception,) as E:
            if DEBUG:
                print_exc()
            return handledProcessData(success=False, desc=str(E), data=None)

    return __inner


class Base:
    _convertPythonToSql = {
        int: 'INTEGER DEFAULT None',
        float: 'FLOAT DEFAULT None',
        str: 'TEXT DEFAULT "undefined"',
        list: 'JSON DEFAULT "[]"',
        dict: 'JSON DEFAULT "[]"',
        tuple: 'JSON DEFAULT "[]"',
        set: 'JSON DEFAULT "[]"'
    }
    _convertSqlToPython = {
        "JSON": loads,
        "INTEGER": int,
        "TEXT": str,
        "VARCHAR": str,
        "FLOAT": float,
        "BLOB": str
    }
    _tableName = ""
    _tablePragma = ""

    def __init__(self):
        self._createSelfTable()

    @handleCursor
    def _createSelfTable(self, _cursor=None) -> None:
        """
            _tableName ve _tablePragma kullanarak kendi tablosunu oluşturur
        :param _cursor:
        :return:
        """

        _cursor.execute(f"CREATE TABLE IF NOT EXISTS {self._tableName} ({self._tablePragma});")

    @handleCursor
    def _getInList(self, _whereSelectors: list[Any, list], _dataSelector: str | list[str] = "*", _convert=True, _cursor=None) -> list[dict]:
        """
            desc:       _getInList([column_name, [equal_to]], "column name(s)")
            example 1:  _getInList(["id", [1,2,3,5]], "*")
            example 2:  _getInList(["id", [1,2,3,5]], "username, password")
            example 3:  _getInList(["id", [1,2,3,5]], ["username", "password"])
            example 4:  _getInList(["device_id", ["b8d61ab24ee8", "c8f09e9e2088", "skd5465"]], "*")
            example 5:  _getInList(["device_id", ["b8d61ab24ee8", "c8f09e9e2088", "skd5465"]], "site_id, system_id")
            example 6:  _getInList(["device_id", ["b8d61ab24ee8", "c8f09e9e2088", "skd5465"]], ["site_id", "system_id"])
            ** raise on any Exception **
        """
        if type(_whereSelectors) in [list, dict, tuple, set]:
            _whereSelectors = list(_whereSelectors)
            if len(_whereSelectors) < 2:
                raise SyntaxError("_whereSelectors eksik parametre")
            else:
                if type(_whereSelectors[1]) in [list, dict, tuple, set]:
                    _whereSelectors[1] = list(_whereSelectors[1])
                else:
                    raise SyntaxError("_whereSelectors[1] liste gibi olmalıdır")
        else:
            raise SyntaxError("_whereSelectors liste gibi olmalıdır")
        _headers = {data[1]: data for data in self._getColumns(_cursor=_cursor)}

        if _dataSelector != "*":

            if isinstance(_dataSelector, str):
                _dataSelector = _dataSelector.split(",")
            _headers = {x: y for x, y in _headers.items() if x in _dataSelector}
            if not _headers:
                return []
            _dataSelector = ",".join(list(_headers.keys()))
        if not _dataSelector:
            return []

        gotData = _cursor.execute(f'SELECT {_dataSelector} FROM {self._tableName} WHERE {_whereSelectors[0]} IN ({",".join(["?"] * len(_whereSelectors[1]))})', _whereSelectors[1]).fetchall()
        if not gotData:
            gotData = []
        else:

            if _convert:
                newData = []
                for idx in range(len(gotData)):
                    newData2 = []

                    for idx2, convertData in enumerate(_headers.values()):
                        newData2.append(self._convertSqlToPython[convertData[2]](gotData[idx][idx2]))
                    newData.append(newData2)
                gotData = newData

        return [dict(zip(_headers, x)) for x in list(gotData)]

    @handleProcess
    def getInList(self, _whereSelectors: list[Any, list], _dataSelector: str | list[str] = "*", _convert=True) -> handledProcessData:
        """
            desc:       getInList([column_name, equal_to], "column name(s)")
            example 1:  getInList(["id", 5], "*")
            example 2:  getInList(["id", 5], "username, password")
            example 3:  getInList(["id", 5], ["username", "password"])
            example 4:  getInList(["device_id", "skd5465"], "*")
            example 5:  getInList(["device_id", "skd5465"], "site_id, system_id")
            example 6:  getInList(["device_id", "skd5465"], ["site_id", "system_id"])
        """
        return self._getInList(_whereSelectors, _dataSelector, _convert)

    @handleCursor
    def _getAll(self, _dataSelector: str | list[str] = "*", _convert=True, _cursor=None) -> list[dict]:
        """
            returns [] if no data or wrong dataSelector, else list[dict]
        :param _dataSelector:
        :param _convert:
        :param _cursor:
        :return:
        """

        _headers = {data[1]: data for data in self._getColumns(_cursor=_cursor)}

        if _dataSelector != "*":

            if isinstance(_dataSelector, str):
                _dataSelector = _dataSelector.split(",")
            _headers = {x: y for x, y in _headers.items() if x in _dataSelector}
            if not _headers:
                return []
            _dataSelector = ",".join([x.strip() for x in _headers.keys()])
        if not _dataSelector:
            return []

        gotData = _cursor.execute(f'SELECT {_dataSelector} FROM {self._tableName}').fetchall()
        if not gotData:
            gotData = []
        else:

            if _convert:
                newData = []
                for idx in range(len(gotData)):
                    newData2 = []

                    for idx2, convertData in enumerate(_headers.values()):
                        newData2.append(self._convertSqlToPython[convertData[2]](gotData[idx][idx2]))
                    newData.append(newData2)

                gotData = newData

        return [dict(zip(_headers, x)) for x in list(gotData)]

    @handleProcess
    def getAll(self, _dataSelector: str | list[str] = "*", _convert=True) -> handledProcessData:
        return self._getAll(_dataSelector, _convert)

    @handleCursor
    def _get(self, _whereSelectors: list[int | str, Any], _dataSelector: str | list[str] = "*", _convert=True, _cursor=None) -> dict:
        """
            desc:       _get([column_name, equal_to], "column name(s)")
            example 1:  _get(["id", 5], "*")
            example 2:  _get(["id", 5], "username, password")
            example 3:  _get(["id", 5], ["username", "password"])
            example 4:  _get(["device_id", "skd5465"], "*")
            example 5:  _get(["device_id", "skd5465"], "site_id, system_id")
            example 6:  _get(["device_id", "skd5465"], ["site_id", "system_id"])
            ** raise on any Exception **
        """
        if type(_whereSelectors) in [list, dict, tuple, set]:
            _whereSelectors = list(_whereSelectors)

        else:
            raise SyntaxError("_whereSelectors liste gibi olmalıdır")
        _headers = {data[1]: data for data in self._getColumns(_cursor=_cursor)}

        if _dataSelector != "*":

            if isinstance(_dataSelector, str):
                _dataSelector = _dataSelector.split(",")
            _headers = {x: y for x, y in _headers.items() if x in _dataSelector}
            if not _headers:
                return {}
            _dataSelector = ",".join([x.strip() for x in _headers.keys()])
        if not _dataSelector:
            return {}
        gotData = _cursor.execute(f'SELECT {_dataSelector} FROM {self._tableName} WHERE {_whereSelectors[0]} = ?;', (_whereSelectors[1],)).fetchone()
        if not gotData:
            gotData = [None] * len(_headers)
        else:
            if _convert:
                newData = []
                for idx, convertData in enumerate(_headers.values()):
                    newData.append(self._convertSqlToPython[convertData[2]](gotData[idx]))
                gotData = newData

        return dict(zip(
            list(_headers.keys()),
            gotData
        ))

    @handleProcess
    def get(self, _whereSelectors: list[int | str, Any], _dataSelector: str | list[str] = "*", _convert=True) -> handledProcessData:
        """
            desc:       get([column_name, equal_to], "column name(s)")
            example 1:  get(["id", 5], "*")
            example 2:  get(["id", 5], "username, password")
            example 3:  get(["id", 5], ["username", "password"])
            example 4:  get(["device_id", "skd5465"], "*")
            example 5:  get(["device_id", "skd5465"], "site_id, system_id")
            example 6:  get(["device_id", "skd5465"], ["site_id", "system_id"])
        """
        return self._get(_whereSelectors, _dataSelector, _convert)

    @handleCursor
    def _createTable(self, _name: str, _type, _cursor=None) -> None:
        _cursor.execute(f"ALTER TABLE {self._tableName} ADD {_name} {self._convertPythonToSql[_type]}")

    @handleCursor
    def _update(self, _whereSelectors: list[int | str, Any], _datas, createNew=False, _cursor=None) -> None:
        """
            desc:       _update([column_name, equal_to], {"column_name": "data")
            example 1:  _update(["id", 5], {"column_1": "data_1", "column_2": "data_2"})
            example 2:  _update(["device_id", "skd5465"], {"column_1": "data_1", "column_2": "data_2"})
            ** raise on any Exception **
        """
        if type(_whereSelectors) in [list, dict, tuple, set]:
            _whereSelectors = list(_whereSelectors)
        else:
            raise SyntaxError("_whereSelectors liste gibi olmalıdır")
        _dbDatas = self._get(_whereSelectors, _cursor=_cursor, _convert=False)
        _diffNames = list(set(_datas.keys()) - set(_dbDatas.keys()))  # _dataNames - _columnNames
        _keys = list(_datas.keys())
        for _key in _keys:
            _data = _datas[_key]
            _type = type(_data)
            if _key in _diffNames:
                if not createNew:
                    _datas.pop(_key, None)
                    continue
                self._createTable(_key, _type, _cursor=_cursor)
            if _type in [list, dict, tuple, set]:
                _data = dumps(_data, ensure_ascii=False)
            _datas[_key] = _data
        _deviceDatas = set(_dbDatas.items())
        _datas = set(_datas.items())
        _diffDatas = dict(_datas - _deviceDatas)

        if _diffDatas:
            updData = ",".join([f"{x}='{y}'" if isinstance(y, str) else f"{x}={y}" for x, y in _diffDatas.items()])
            _cursor.execute(f'UPDATE {self._tableName} SET {updData} WHERE {_whereSelectors[0]} = ?;', (_whereSelectors[1],))

    @handleProcess
    def update(self, _whereSelectors: list[int | str, Any], _datas, createNew=False) -> handledProcessData:
        """
            desc:       _update([column_name, equal_to], {"column_name": "data")
            example 1:  _update(["id", 5], {"column_1": "data_1", "column_2": "data_2"})
            example 2:  _update(["device_id", "skd5465"], {"column_1": "data_1", "column_2": "data_2"})
        """
        return self._update(_whereSelectors, _datas, createNew)

    @handleCursor
    def _add(self, _whereSelector: str | dict, _cursor=None) -> None:
        """
            desc:       _add({"column_1": "data_1", "column_2": "data_2"})
            example 1:  _add({"column_1": "data_1", "column_2": "data_2"})
            example 2:  _add('{"column_1": "data_1", "column_2": "data_2"}') <- String
            ** raise on any Exception **
        """
        if isinstance(_whereSelector, str):
            try:
                loads(_whereSelector)
            except JSONDecodeError:
                raise SyntaxError("Dönüştürülemez json strsi")

        for _key, _data in _whereSelector.items():
            _type = type(_data)
            if _type in [list, dict, tuple, set]:
                _data = dumps(_data, ensure_ascii=False)
            _whereSelector[_key] = _data

        _cursor.execute(f"INSERT OR IGNORE INTO {self._tableName} ({','.join(list(_whereSelector.keys()))}) VALUES ({','.join(['?'] * len(_whereSelector))});", tuple(_whereSelector.values()))

    @handleProcess
    def add(self, _whereSelector: str | dict) -> handledProcessData:
        """
            desc:       _add({"column_1": "data_1", "column_2": "data_2"})
            example 1:  _add({"column_1": "data_1", "column_2": "data_2"})
            example 2:  _add('{"column_1": "data_1", "column_2": "data_2"}') <- String
        """
        return self._add(_whereSelector)

    @handleCursor
    def _delete(self, _whereSelectors: list[int | str, Any], _cursor=None) -> None:
        """
            desc:       _delete([column_name, equal_to])
            example 1:  _delete(["id", 5])
            example 2:  _delete(["device_id", "skd5465"])
            ** raise on any Exception **
        """
        _cursor.execute(f"DELETE FROM {self._tableName} WHERE {_whereSelectors[0]} = ?;", (_whereSelectors[1],))

    @handleProcess
    def delete(self, _whereSelectors: list[int | str, Any]) -> handledProcessData:
        """
            desc:       _delete([column_name, equal_to])
            example 1:  _delete(["id", 5])
            example 2:  _delete(["device_id", "skd5465"])
        """
        return self._delete(_whereSelectors)

    @handleCursor
    def _getColumns(self, _cursor=None) -> tuple:
        """
            return: [(indexNo, columnName, columnType, notNull, defaultValue, keyId)]
        """
        return _cursor.execute(f"PRAGMA table_info({self._tableName});").fetchall()


class Systems(Base):
    _tableName = systemsTableName
    _tablePragma = """
                "id"        INTEGER,
                "system_name"      VARCHAR NOT NULL,
                "tables"	JSON DEFAULT "[]",
                PRIMARY KEY("id" AUTOINCREMENT)
            """

    def __init__(self):
        super().__init__()


class Devices(Base):
    _tableName = devicesTableName
    _tablePragma = """
                    "device_id"	VARCHAR NOT NULL,
                    PRIMARY KEY("device_id")
                    """

    def __init__(self):
        super().__init__()


class Sites(Base):
    _tableName = sitesTableName
    _tablePragma = """
                    "id"	INTEGER,
                    "site_name"	TEXT DEFAULT "undefined",
                    "areas"	JSON,
                    PRIMARY KEY("id" AUTOINCREMENT)
                    """

    def __init__(self):
        super().__init__()

    @handleCursor
    def _add(self, site_name, areas, _cursor=None):
        _cursor.execute(f"SELECT MAX(id) FROM {self._tableName}")
        max_id = _cursor.fetchone()  # max_id = _cursor.fetchone()[0] ?????

        max_id = max_id[0] + 1 if max_id else 0

        # new_id = max_id + 1 if max_id is not None else 0 ???????? None dönmez. () döner ve 0. indexini alamazsın. 4 satır yukardaki yorum

        new_areas = []
        for i, area in enumerate(areas):
            new_area = {"id": i, **area}  # id değerini bölge nesnesinden ayırarak başa ekliyoruz
            new_areas.append(new_area)

        # _cursor.execute(f"INSERT INTO {self._tableName} (id, site_name, areas) VALUES (?, ?, ?)", (new_id, site_name, json.dumps(new_areas)))

        return super()._add({
            "id": max_id,
            "site_name": site_name,
            "areas": new_areas
        }, _cursor=_cursor)

        # print(f"INSERT INTO {self._tableName} (site_name, areas) VALUES ({self._whereSelector(site_name)}, '{dumps(areas)}')")
        # _cursor.execute(f"""INSERT INTO {self._tableName} (site_name, areas) VALUES ("{site_name}", '{dumps(areas)}')""")

        # return self._get(_cursor.lastrowid)

    @handleProcess
    def add(self, site_name, areas) -> handledProcessData:
        return self._add(site_name, areas)

    @handleCursor
    def _delete(self, site_id, _cursor=None):
        _cursor.execute(f"""
                UPDATE {usersTableName} as t
                    SET sites = json_remove(t.sites, j.fullkey)
                    FROM json_each(t.sites) AS j
                    WHERE j.value {f"IN ({','.join(site_id)})" if isinstance(site_id, list) else f"= {site_id}"}
                ;""")
        super()._delete(site_id, _cursor=_cursor)


class Users(Base):
    _tableName = usersTableName
    _tablePragma = """
                    "id"	INTEGER,
                    "firstname"	VARCHAR NOT NULL,
                    "lastname"	VARCHAR NOT NULL,
                    "tagname"	VARCHAR NOT NULL,
                    "username"	VARCHAR NOT NULL,
                    "password"	BLOB NOT NULL,
                    "sites"	JSON,
                    "level"	INTEGER DEFAULT 3,
                    PRIMARY KEY("id" AUTOINCREMENT)
                    """

    def __init__(self):
        super().__init__()
        # self.update(["id", 3], {"password": bcrypt.hashpw("123456".encode("UTF-8"), bcrypt.gensalt(10)).decode("UTF-8")})

    @handleCursor
    def _add(self, firstname, lastname, username, tagname, password, sites, level, _cursor=None):
        password_crypted = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        return super()._add({
            "firstname": firstname,
            "lastname": lastname,
            "username": username,
            "tagname": tagname,
            "password": password_crypted,
            "sites": sites,
            "level": level
        }, _cursor=_cursor)

    @handleProcess
    def add(self, firstname, lastname, username, tagname, password, sites, level) -> handledProcessData:
        return self._add(firstname, lastname, username, tagname, password, sites, level)

    @handleCursor
    def _changePassword(self, idn, new_password, _cursor=None):
        if not idn:
            raise SyntaxError("Id Gelmedi...")
        super()._update(["id", idn], {
            "password": bcrypt.hashpw(new_password.encode('UTF-8'), bcrypt.gensalt(10)).decode("UTF-8")
        }, _cursor=_cursor)

    @handleProcess
    def changePassword(self, idn, new_password) -> handledProcessData:
        return self._changePassword(idn, new_password)

    @handleCursor
    def findIdByNickName(self, _userName, _cursor=None):
        _id = _cursor.execute(f'SELECT id FROM {usersTableName} WHERE username = ?', (_userName,)).fetchone()
        if _id:
            return _id[0]
        return None

    @handleCursor
    def _checkUserLogin(self, _userName, _password, _cursor=None) -> None:
        _id = self.findIdByNickName(_userName, _cursor=_cursor)
        if _id is None:
            raise KeyError("Kullanıcı bulunamadı")
        # _dbPassword = _cursor.execute(f'SELECT id, password, firstname, lastname, tagname, sites, level FROM {usersTableName} WHERE username = ?', (_userName,)).fetchone()
        _userData = self._get(["id", _id], ["id", "username", "password", "firstname", "lastname", "tagname", "sites", "level"], _cursor=_cursor)
        if _userData:
            if bcrypt.checkpw(_password.encode("UTF-8"), _userData["password"].encode("UTF-8")):
                _userData.pop("password", None)
                # session.update(_userData)
                return _userData
        raise AttributeError("Şifre yanlış")

    @handleProcess
    def checkUserLogin(self, user, password) -> handledProcessData:
        return self._checkUserLogin(user, password, _cursor=None)

    @handleCursor
    def _updateUserLogin(self, _userId, _firstname, _lastname, _tagname, _username, _cursor=None) -> bool:
        super()._update(["id", _userId], {
            "firstname": _firstname,
            "lastname": _lastname,
            "tagname": _tagname,
            "username": _username,

        }, _cursor=_cursor)
        # execute işlemi başarılı veya başarısız döndürmez. cursor geri döndürür.
        # bu tarz işlemlerin başarılı olup olmadığını sadece .success ile kontrol edebilirsiniz.
        # aşağıdaki trueyi bırakıyorum onunla işlem yaptığını düşündüğüm için
        return True

    @handleProcess
    def updateUserLogin(self, userId, firstname, lastname, tagname, username) -> handledProcessData:
        return self._updateUserLogin(userId, firstname, lastname, tagname, username, _cursor=None)


class Database:
    __slots__ = ("cnx",
                 "devices", "systems", "sites", "users",
                 "_public", "_modules")

    def __init__(self):
        modules.database = self

        self.cnx = cnx
        self.devices = Devices()
        self.systems = Systems()
        self.sites = Sites()
        self.users = Users()

    @staticmethod
    def cursor(cursorClass=None):
        if cursorClass:
            return cnx.cursor(cursorClass)
        return cnx.cursor()

    @staticmethod
    def close():
        cnx.close()
