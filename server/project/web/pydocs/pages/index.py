__all__ = ["page"]

from os.path import splitext, basename

from flask import render_template, request
from flask.views import View

from project.modules import modules


class page(View):
    init_every_request = False
    fileName = splitext(basename(__file__))[0]
    useSocket = True

    def __init__(self):
        super().__init__()
        if self.useSocket:
            @modules.socketio.on("connect", namespace=f"/{self.fileName}")
            def connect():
                ...

            @modules.socketio.on("disconnect", namespace=f"/{self.fileName}")
            def disconnect():
                ...

            self.socket_name = self.fileName
        else:
            self.socket_name = None

    def dispatch_request(self):

        return render_template(f'{self.fileName}.html', socket_name=None)


modules.app.add_url_rule("/", view_func=page.as_view(name="/"))
modules.app.add_url_rule(f"/{page.fileName}", view_func=page.as_view(name=page.fileName))
