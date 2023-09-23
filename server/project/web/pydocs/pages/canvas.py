__all__ = ["page"]

from os.path import splitext, basename
from json import dumps

from flask import render_template, request
from flask.views import View

from project.modules import modules, public


class page(View):
    init_every_request = False
    fileName = splitext(basename(__file__))[0]

    def __init__(self):
        super().__init__()

    def dispatch_request(self, device_id=None):

        @modules.socketio.on("connect", namespace=f"/canvas/{device_id}")
        def connect(_msg=None):
            ...
            _dev = public.deviceClients.get(device_id, None)
            if _dev:
                modules.socketio.emit("lastStatus", dumps(dict(pins=_dev.pinStatus, activeProfiles=_dev.activeProfiles)), namespace=f"/canvas/{device_id}")

        @modules.socketio.on("disconnect", namespace=f"/canvas/{device_id}")
        def disconnect(_msg=None):
            ...

        return render_template(f'{self.fileName}.html', device_id=device_id)


modules.app.add_url_rule(f"/{page.fileName}/<string:device_id>", view_func=page.as_view(name=page.fileName))
