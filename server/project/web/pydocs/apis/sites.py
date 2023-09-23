from flask import session
from flask.views import MethodView
from project.modules import modules
from json import dumps


class SystemAPI(MethodView):
    init_every_request = False

    def __init__(self):
        ...

    def get(self, site=None, area=None):
        if "counter" not in session:
            session["counter"] = 0

        print("get", site, area)

        izin = True if session["counter"] > 2 else False

        if izin:
            return dict(ret="GETİRİLDİ")
        session["counter"] += 1
        return dict(ret="GETİRİLEMEDİ")

    def post(self, site=None, area=None):
        print("post", site, area)
        return dict(ret="POSTLANDI")

    def patch(self, site=None, area=None):
        print("patch", site, area)
        return dict(ret="PATCHLENDİ")

    def delete(self, site=None, area=None):
        print("delete", site, area)
        return dict(ret="SİLİNDİ")


modules.app.add_url_rule(f"/api/sites/<string:site>/<string:area>", view_func=SystemAPI.as_view("api11"))
modules.app.add_url_rule(f"/api/sites/<string:site>/", view_func=SystemAPI.as_view("api22"))
