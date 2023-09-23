__all__ = ("public", "modules")

import logging
from asyncio import AbstractEventLoop, get_event_loop, new_event_loop

from project.libs.utils import IP
from gc import collect

from project.modules.cacheControl import CacheData

try:
    from project.modules.broker.broker import Broker
    from project.modules.database.database import Database
    from project.modules.system.system import System
    from project.modules.broker.libs import DeviceClient
    from project.modules.flask.flask import myFlask as Flask, SocketIO
except ImportError:
    class Broker:
        ...


    class Database:
        ...


    class System:
        ...


    class Flask:
        ...


    class SocketIO:
        ...


    class DeviceClient:
        ...


class modules:
    try:
        loop: AbstractEventLoop = get_event_loop()
    except RuntimeError:
        loop: AbstractEventLoop = new_event_loop()
    database: Database = None
    broker: Broker = None
    app: Flask = None
    system: System = None
    socketio: SocketIO = None

    """
    def __missing__(self, _key):
        _data = modules.database.devices.get(["device_id", _key]).data
        self.__setitem__(_key, _data)
        return _data
    """


class public:
    IP: str = IP
    port: int = 80
    loggingLevel: int = logging.WARN
    loggingFormatter: str = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    deviceClients: dict[str, DeviceClient] = dict()
    deviceDatas: CacheData = None
    siteDatas: CacheData = None


def clearCache():
    if public.siteDatas is not None:
        public.siteDatas.clear()
    if public.deviceDatas is not None:
        public.deviceDatas.clear()
    collect()


def initModules():
    from project.modules.broker import createBroker
    from project.modules.database import createDatabase
    from project.modules.system import createSystem
    from project.modules.flask import createApp
    createDatabase()
    public.siteDatas = CacheData(max_len=100, max_age_seconds=600, primaryKey="id", primaryKeyType=int,  database=modules.database.sites)
    public.deviceDatas = CacheData(max_len=100, max_age_seconds=600, primaryKey="device_id", primaryKeyType=str, database=modules.database.devices)
    createBroker()
    createApp()
    createSystem()


logging.basicConfig(level=public.loggingLevel, format=public.loggingFormatter)

initModules()
del initModules
"""
# a = modules.database.sites.getInList(["id", [1]])
# print(a)

b = public.siteDatas["1"]
print(b)
print(public.siteDatas.keys())
print()

print(public.siteDatas[[1, "2"]])
print(public.siteDatas.keys())
print()

public.siteDatas.pop(1)
print(public.siteDatas.keys())
print(public.siteDatas.values())
print()
print(public.siteDatas["*"])
print(public.siteDatas.keys())

sleep(10)
print(public.siteDatas.keys())
print(public.siteDatas.values())
"""