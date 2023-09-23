__all__ = ("CacheData", )

from threading import Timer
from time import time

from expiringdict import ExpiringDict


class CacheData(ExpiringDict):
    def __init__(self, max_len, max_age_seconds, primaryKey="id", primaryKeyType=None, database=None):
        super().__init__(max_len, max_age_seconds)
        self._cacheTimer = Timer(self.max_age, self._cacheRemover)
        self._cacheTimer.daemon = True
        self._cacheTimer.start()
        self._primaryKey = primaryKey
        self._primaryKeyType = primaryKeyType
        self.database = database

    def clear(self) -> None:
        with self.lock:
            for key in self._safe_keys():
                try:
                    del self[key]
                except KeyError:
                    pass

    def __del__(self):
        with self.lock:
            self._cacheTimer.cancel()

    def _cacheRemover(self):
        with self.lock:
            for key in self._safe_keys():
                item = self.__getitem__(key, with_age=True)
                if time() - item[1] > self.max_age:
                    try:
                        del self[key]
                    except KeyError:
                        pass

            self._cacheTimer = Timer(self.max_age, self._cacheRemover)
            self._cacheTimer.daemon = True
            self._cacheTimer.start()

    def pop(self, key, default=None):
        """ Get item from the dict and remove it.

        Return default if expired or does not exist. Never raise KeyError.
        """
        with self.lock:
            if key in self._safe_keys():
                try:
                    del self[key]
                except KeyError:
                    pass

    def __contains__(self, key):
        """ Return True if the dict has a key, else return False. """
        with self.lock:
            if key in self._safe_keys():
                item = self.__getitem__(key)

                if time() - item[1] < self.max_age:
                    return True
                else:
                    try:
                        del self[key]
                    except KeyError:
                        pass
                    return False
            return False

    def __getitem__(self, _key, with_age=False):
        if isinstance(_key, list):
            _key = list(map(self._primaryKeyType, _key))
            _missing = set(_key) - set(self.keys())
            _has = set(self.keys()) & set(_key)
            if _missing:
                _data = self.database.getInList([self._primaryKey, _missing]).data
                if _data:
                    for x in _data:
                        self.__setitem__(x[self._primaryKey], x)
            else:
                _data = []
            for x in _has:
                _data.append(super().__getitem__(x, with_age))
            return _data
        return super().__getitem__(_key, with_age)

    def __missing__(self, _key):
        if _key == "*":
            _data = self.database.getAll().data
        else:
            _data = self.database.get([self._primaryKey, _key]).data
        if isinstance(_data, list):
            for x in _data:
                self.__setitem__(x[self._primaryKey], x)
        else:
            self.__setitem__(self._primaryKeyType(_key), _data)

        return _data, time()


"""
class DeviceDatas(CacheData):
    def __init__(self, max_len=100, max_age_seconds=600, primaryKey="id", database=None):
        super().__init__(max_len, max_age_seconds, primaryKey, database)


class SiteDatas(CacheData):
    def __init__(self, max_len=100, max_age_seconds=600, primaryKey="id", database=None):
        super().__init__(max_len, max_age_seconds, primaryKey, database)
"""
