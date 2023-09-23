__all__ = ("myFlask", "SocketIO")

from flask_socketio import SocketIO

from flask import Flask
from project.modules import modules, public


def set_globals():
    return dict(server_ip=f"{public.IP}:{public.port}")


class myFlask(Flask):
    def __init__(self):
        from os import environ
        from pathlib import Path
        import gevent
        from project.libs.utils import dataFromYaml

        currFolder = Path(__file__).parent

        flaskConfig = dataFromYaml((currFolder / "flaskConfig.yaml").resolve())

        appConfig: dict = flaskConfig["app"]

        super().__init__(__name__, root_path=environ["PWD"], **appConfig["init"])

        modules.app = self
        gevent.get_hub().NOT_ERROR += (KeyboardInterrupt,)
        modules.socketio = SocketIO(self, async_mode='gevent')
        public.port = appConfig.get("port", public.port)

        self.runConf = appConfig["run"]

        self.config.update(**appConfig["config"])

        self.context_processor(set_globals)

    def start(self):
        modules.socketio.run(**{"app": modules.app, "host": public.IP, "port": public.port, **self.runConf})
