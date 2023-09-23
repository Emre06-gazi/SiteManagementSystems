__all__ = ("dataFromYaml", "nothing", "IP")

from yaml import load
from typing import Any
from sys import __excepthook__

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def dataFromYaml(_path) -> dict:
    with open(_path, mode="r", encoding="UTF-8") as document:
        return load(document.read(), Loader=Loader)


def excepthook(exc_type, exc_value, exc_traceback) -> None:  # noqa
    if issubclass(exc_type, KeyboardInterrupt):
        __excepthook__(exc_type, exc_value, exc_traceback)
        return
    from traceback import format_exception
    tb = "".join(format_exception(exc_type, exc_value, exc_traceback))
    print(tb)


def nothing(*_args, **_kwargs) -> Any:
    """
        Anything for Anything
    :param _args:
    :param _kwargs:
    :return:
    """
    pass


def fixPrint() -> None:
    """
        Fixes print function for frozen
    :return:
    """
    import faulthandler
    import sys
    noConsole = False
    try:
        print(end="")
    except AttributeError:
        noConsole = True

    if sys.stderr is None or sys.stdout is None or sys.stdin is None or noConsole:
        import builtins

        builtins.print = nothing
        faulthandler.enable = nothing

    sys.excepthook = excepthook  # noqa
    faulthandler.enable()


def init() -> None:
    """ idk
    :return:
    """
    from platform import uname
    from os.path import dirname, abspath
    from os import environ, getcwd
    import sys

    built = True if getattr(sys, 'frozen', False) else False

    if built:
        mainPath = dirname(sys.executable)
    else:
        try:
            mainPath = dirname(abspath(str(sys.modules['__main__'].__file__)))
        except NameError:
            mainPath = getcwd()

    # mainPath = dirname(sys.executable) if built else dirname(abspath(str(sys.modules['__main__'].__file__)))

    environ['PWD'] = f"{mainPath}/"
    environ['built'] = str(built).lower()
    dName = uname()
    system, release, version = dName.system, dName.release, dName.version
    environ['system'], environ['release'], environ['version'] = system, release, version


def getIP() -> str:
    """
    :return: Ip address in str format
    """
    from socket import socket, AF_INET, SOCK_DGRAM
    s = socket(AF_INET, SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        ret = s.getsockname()[0]
    except (OSError, TimeoutError):
        ret = '127.0.0.1'
    finally:
        s.close()
    return ret


fixPrint()
init()
IP = getIP()
del fixPrint
del init
del getIP
