# This file is executed on every boot (including wake-boot from deepsleep)
from esp import osdebug  # noqa
import gc

osdebug(None)
gc.collect()


# import webrepl
# webrepl.start()





