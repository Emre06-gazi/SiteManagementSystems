__all__ = ("main",)

from project.libs.globals import rtc


def main(_system):
    from utime import time, sleep
    message_interval = 10

    while _system.continueRun:
        _changes = {}
        _system.pinSystem.changed = False

        _datetime = list(rtc.datetime()[3:6])
        for profile in _system.configs.profiles:
            print(profile[1], _datetime,  profile[2], profile[1] <= _datetime < profile[2])
            if profile[1] <= _datetime < profile[2]:
                _enabled = True

                for pinProfile in profile[3]:

                    measurePins = pinProfile[0]
                    humiditySum = 0
                    for measureNo in measurePins:
                        humidity, temperature = _system.pinSystem.getMeasure(measureNo)
                        humiditySum += humidity

                    measureAve = humiditySum / len(measurePins)
                    if measureAve < pinProfile[1]:  # maxHum
                        newStat = 1
                    else:
                        newStat = 0
                    for outputNo in pinProfile[2]:
                        print(outputNo, newStat)
                        _changes[outputNo] = newStat or _changes.get(outputNo, 0)
                        # _system.pinSystem.setValue(outputNo, newStat)
            else:
                _enabled = False

                for pinProfile in profile[3]:
                    measurePins = pinProfile[0]
                    for measureNo in measurePins:
                        _system.pinSystem.getMeasure(measureNo)
                    for outputNo in pinProfile[2]:
                        _changes.setdefault(outputNo, 0)
                        # _system.pinSystem.setValue(outputNo, 0)

            if _enabled:
                _system.pinSystem.activeProfiles.add(profile[0])
        print(_changes)
        for _outputNo, _newStat in _changes.items():
            _system.pinSystem.setValue(_outputNo, _newStat)

        if _system.pinSystem.changed:
            _system.pinSystem.setCurrent()
        # print(time(), message_interval - (time() % message_interval))
        sleep(message_interval - (time() % message_interval))
