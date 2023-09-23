__all__ = ("rtc", "updateRtc", "commFlags", "DEBUG")

from machine import RTC

DEBUG = False

rtc = RTC()


class commFlags:
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


def updateRtc(msg):
    if msg.mType == commFlags.rtc:
        _timeTuple = tuple(map(int, msg.msg.decode("UTF-8").split(",")))
        print(_timeTuple)
        rtc.datetime(_timeTuple)
        return True
    return False
