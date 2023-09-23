from json import dumps

from project.modules import modules
from flask import session, jsonify
from flask.views import MethodView


class SystemAPI(MethodView):
    init_every_request = False

    def __init__(self):
        ...

    def get(self, username=None, password=None):
        if "counter" not in session:
            session["counter"] = 0

        print("get", username, password)

        izin = True if session["counter"] > 2 else False

        if izin:
            return jsonify(ret="GETİRİLDİ")
        session["counter"] += 1
        return jsonify(ret="GETİRİLEMEDİ")

    def post(self, username=None, password=None, firstname=None, lastname=None, tagname=None, sites=None, level=None):
        print("post", username, password)

        process = modules.database.users.checkUserLogin(username, password)
        if process.success and process.data:
            session.update(process.data)

        return dumps(dict(success=process.success, desc=process.desc))

    def patch(self, username=None, password=None):
        print("patch", username, password)
        return jsonify(ret="PATCHLENDİ")

    def delete(self, username=None, password=None):
        print("delete", username, password)
        return jsonify(ret="SİLİNDİ")


modules.app.add_url_rule("/api/login/<string:username>/<string:password>", view_func=SystemAPI.as_view("api111"))
