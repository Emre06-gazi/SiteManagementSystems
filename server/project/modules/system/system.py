__all__ = ("System",)

import asyncio
import sys
import time
from asyncio import sleep
from json import dumps
from threading import Thread
from project.modules import modules, public
from traceback import print_exc


class System:
    __slots__ = ()

    def __init__(self, ):
        modules.system = self

    def startBroker(self):
        from project.modules import modules

        async def broker_coro():
            return await modules.broker.start()

        modules.loop.run_until_complete(broker_coro())

    # sendConfigToDevice("sadfasd", "gpio", {  "inputs": [2,4,5,12,13,14,15,16,17,18,19,21,22,23,25,26,27,32,33,34,35],  "outputs": [2,4,5,12,13,14,15,16,17,18,19,21,22,23,25,26,27,32,33]})
    @staticmethod
    def sendConfigToDevice(device_id, name, data):
        deviceClient = public.deviceClients.get(device_id, None)
        if deviceClient is not None:
            return deviceClient.sendConfig(name, data)

    @staticmethod
    def sendResetToDevice(device_id):
        deviceClient = public.deviceClients.get(device_id, None)
        if deviceClient is not None:
            return deviceClient.sendReset()

    @staticmethod
    def sendUpdateToDevice(device_id, name):
        deviceClient = public.deviceClients.get(device_id, None)
        if deviceClient is not None:
            return deviceClient.sendUpdate(name)

    # sendLockToDevice("sadfasd", True)
    @staticmethod
    def sendLockToDevice(device_id, _lockStatus):
        deviceClient = public.deviceClients.get(device_id, None)
        if deviceClient is not None:
            return deviceClient.sendLock(_lockStatus)

    @staticmethod
    def tester():
        time.sleep(10)
        modules.system.sendUpdateToDevice("c8f09e9e2088", "testUpdate")
        time.sleep(5)
        modules.system.sendResetToDevice("c8f09e9e2088")

    def start(self):
        from project.web.pydocs import initPages
        import gevent

        initPages()
        self.startBroker()

        loopThread = Thread(target=modules.loop.run_forever, daemon=True)
        # Thread(target=self.tester, daemon=True).start()
        loopThread.start()
        try:
            modules.app.start()
        except (KeyboardInterrupt, SystemExit):
            pass
        except (Exception,):
            print_exc()
        finally:

            self.stop()

            loopThread.join()
            gevent.wait()
            sys.exit(0)

    @staticmethod
    async def waitTasks(tasks):
        return await asyncio.gather(*asyncio.all_tasks(tasks))

    def stop(self):
        asyncio.ensure_future(modules.broker.shutdown(), loop=modules.loop).done()
        tasks = asyncio.all_tasks(modules.loop)

        for task in tasks:
            task.cancel()

        asyncio.ensure_future(self.waitTasks(tasks)).done()

        modules.loop.stop()
        while modules.loop.is_running():
            continue

        modules.loop.close()

        modules.database.close()
