from json import loads

from project.modules import modules
from flask import session, jsonify, request
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

    def post(self, id=None, firstname=None, lastname=None, tagname=None, username=None):
        data = loads(request.data.decode("UTF-8"))
        print(data["firstname"])

        userUpdate = modules.database.users.updateUserLogin(id, firstname, lastname, tagname, username)
        if userUpdate.success and userUpdate.data:
            session["id"] = id
            session["firstname"] = firstname
            session["lastname"] = lastname
            session["tagname"] = tagname
            session["username"] = username

            print(userUpdate.data)
            return jsonify(ret="POSTLANDI")
        else:
            return jsonify(ret="HATALI-ISLEM")

    def patch(self, username=None, password=None):
        print("patch", username, password)
        return jsonify(ret="PATCHLENDİ")

    def delete(self, username=None, password=None):
        print("delete", username, password)
        return jsonify(ret="SİLİNDİ")

modules.app.add_url_rule("/api/users/<string:id>/<string:firstname>/<string:lastname>/<string:tagname>/<string:username>", view_func=SystemAPI.as_view("api1111"))

