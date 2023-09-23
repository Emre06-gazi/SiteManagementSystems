__all__ = ("Broker",)

import logging
import ssl
from asyncio import start_server
from collections import deque
from json import loads

from project.modules.broker.libs import (Reader, Writer, DeviceClient)
from traceback import print_exc
from project.modules import modules, public
from project.modules.broker.libs.adapters import DeviceDataConvertor, commFlags
from gc import collect


class BrokerException(Exception):
    pass


class Broker:

    def __init__(self):
        modules.broker = self

        self._loop = modules.loop

        self.logger = logging.getLogger(__name__)

        self.config = {}
        self.updateConf()

        self._server = None

    def updateConf(self):
        from pathlib import Path
        from project.libs.utils import dataFromYaml
        currFolder = Path(__file__).parent

        self.config = dataFromYaml((currFolder / "brokerConfig.yaml").resolve())
        self.config.get("listener", {}).update({"ip": public.IP})

    async def start(self) -> None:
        self.logger.debug("Broker starting")

        # await self.plugins_manager.fire_event(EVENT_BROKER_PRE_START)
        try:
            # Start network listeners

            # SSL Context
            sc = None

            # accept string "on" / "off" or boolean
            ssl_active = self.config["listener"].get("ssl", False)
            if isinstance(ssl_active, str):
                ssl_active = ssl_active.upper() == "ON"

            if ssl_active:
                try:
                    sc = ssl.create_default_context(
                        ssl.Purpose.CLIENT_AUTH,
                        cafile=self.config["listener"].get("cafile"),
                        capath=self.config["listener"].get("capath"),
                        cadata=self.config["listener"].get("cadata"),
                    )
                    sc.load_cert_chain(self.config["listener"]["certfile"], self.config["listener"]["keyfile"])
                    sc.verify_mode = ssl.CERT_OPTIONAL
                except KeyError as ke:
                    raise BrokerException(
                        "'certfile' or 'keyfile' configuration parameter missing: %s"
                        % ke
                    )
                except FileNotFoundError as fnfe:
                    raise BrokerException(
                        "Can't read cert files '%s' or '%s' : %s"
                        % (self.config["listener"]["certfile"], self.config["listener"]["keyfile"], fnfe)
                    )

            address = self.config["listener"]["ip"]
            s_port = self.config["listener"].get("port", 500 if sc is None else 502)
            try:
                port = int(s_port)
            except ValueError:
                raise BrokerException(
                    "Invalid port value in bind value: %s" % self.config["listener"]["port"]
                )
            _headers = [x.lstrip("_") for x in DeviceDataConvertor.__slots__]
            self.logger.debug("Veritabanında kayıtlı cihazlar önbelleğe alınıyor")

            # noinspection PyProtectedMember
            previousDevicesDatas = modules.database.devices._getAll(_headers)
            previousDevices = {}

            for data in previousDevicesDatas:
                previousDev = DeviceClient()
                previousDev.setIfItHas(**data)
                previousDev.connected = False
                previousDevices.update({previousDev.device_id: previousDev})

            public.deviceClients.update(previousDevices)
            self.logger.debug("Önbelleğe alınan cihaz sayısı: %d" % len(previousDevices))

            self._server = await start_server(
                self.stream_connected,
                address,
                port,
                reuse_address=True,
                ssl=sc,
            )

            self.logger.info(
                "Listener '%s' bind to %s"
                % ("broker", f"{address}:{port}")
            )

            # await self.plugins_manager.fire_event(EVENT_BROKER_POST_START)

            # Start broadcast loop

            self.logger.debug("Broker started")
        except Exception as e:
            self.logger.error("Broker startup failed: %s" % e)
            raise BrokerException("Broker instance can't be started: %s" % e)

    async def shutdown(self):
        """
        Stop broker instance.

        Closes all connected session, stop listening on network socket and free resources.
        """
        tasks = deque()

        for device in public.deviceClients.values():
            device.closeReason = "sistem kapanışı"
            tasks.append(
                await device.close()
            )
        while tasks and tasks[0].done():
            tasks.popleft()

        public.deviceClients = dict()

        # Fire broker_shutdown event to plugins
        # await self.plugins_manager.fire_event(EVENT_BROKER_PRE_SHUTDOWN)

        self.logger.debug("Broker closing")

        self._server.close()
        await self._server.wait_closed()

        self.logger.info("Broker closed")
        # await self.plugins_manager.fire_event(EVENT_BROKER_POST_SHUTDOWN)

    async def stream_connected(self, reader, writer):
        await self.client_connected(Reader(reader), Writer(writer))

    async def client_connected(self, reader: Reader, writer: Writer):

        remote_address, remote_port = writer.get_peer_info()
        self.logger.info(
            "Connection from %s:%d on listener broker"
            % (remote_address, remote_port)
        )

        # Wait for first packet and expect a CONNECT

        device = DeviceClient(writer=writer, reader=reader, loop=self._loop)

        try:
            registeredObj = await device.register()
            if not registeredObj.registered:
                self.logger.warning(f"{device.device_id} -> {remote_address}: {remote_port} ->  kayıt edilemedi -> {registeredObj.reason}")
                await device.close()
                self.logger.debug("Connection closed")
                return
        except (Exception,) as exc:
            self.logger.warning(
                "device_connected %s: ERROR: %s"
                % (f"{remote_address}:{remote_port}", exc)
            )
            print_exc()
            await device.close()
            self.logger.debug("Connection closed")
            return
        oldDevice = public.deviceClients.get(device.device_id, None)
        if oldDevice:
            _oldTopic = (oldDevice.site_id, oldDevice.block_id, oldDevice.system_id)
            _newTopic = (device.site_id, device.block_id, device.system_id)
            if _oldTopic != _newTopic:
                self.logger.debug("%s -> Cihazın topici değişti: %s -> %s" % (device.device_id, _oldTopic, _newTopic))
            if oldDevice.writer is None:
                self.logger.debug("%s -> Önbellek session, kapatılıyor" % device.device_id)
                oldDevice.closeReason = "Önbellek session"
            elif oldDevice.connected:
                self.logger.debug("%s -> Unutulmuş eski session, kapatılıyor" % device.device_id)
                oldDevice.closeReason = "Unutulmuş eski session"
            else:
                self.logger.debug("%s -> Eski session, replace ediliyor" % device.device_id)
                oldDevice.closeReason = "Eski session, replace"
            await oldDevice.close()
            self.logger.debug("%s -> kapatıldı" % device.device_id)

        if device.device_id in public.deviceDatas.keys():
            public.deviceDatas.pop(device.device_id, None)
        public.deviceClients.update({device.device_id: device})
        self.logger.debug("%s -> kayıt edildi" % device.device_id)

        self.logger.debug("%s -> dinlenemeye alınıyor" % device.device_id)
        modules.socketio.emit("deviceConnected", device.device_id, namespace=f"/canvas/{device.device_id}")
        modules.socketio.emit("deviceConnected", device.device_id, namespace=f"/index")
        collect()
        while device.connected:
            try:
                msg = await device.reader.readMsg(int(device.timeout))

                if msg.mType is None:
                    if not device.closeReason:
                        device.closeReason = msg.reason
                    device.connected = False
                    continue
                msg.msg = msg.msg.decode("UTF-8")
                print("in while", msg.mType, msg.msg)

                if msg.mType == commFlags.close:
                    device.closeReason = "Cihaz manuel kapatıldı"
                    device.connected = False
                elif msg.mType in [commFlags.last_diff_pin_status, commFlags.last_pin_status]:
                    modules.socketio.emit("deviceReceived", msg.msg, namespace=f"/canvas/{device.device_id}")

                    await device.updatePins(loads(msg.msg))
                elif msg.mType == commFlags.rtc:
                    await device.responseRtc(msg)

            except (Exception,) as E:
                print_exc()
                device.connected = False
                device.closeReason = str(E)

        reason = await device.close()
        self.logger.debug("%s -> '%s' sebebinden kapatıldı" % (device.device_id, reason))
        modules.socketio.emit("deviceDisconnected", device.device_id, namespace=f"/canvas/{device.device_id}")
        modules.socketio.emit("deviceDisconnected", device.device_id, namespace=f"/index")
