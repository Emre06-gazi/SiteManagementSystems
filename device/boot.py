# This file is executed on every boot (including wake-boot from deepsleep)
from esp import osdebug  # noqa
from gc import collect

osdebug(None)
collect()


# import webrepl
# webrepl.start()





