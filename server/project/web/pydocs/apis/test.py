from json import dumps
from math import inf

from flask import session, request
from flask.views import MethodView
from project.modules import modules, public
from project.web.pydocs.libs.auth import login_required


class SystemAPI(MethodView):
    init_every_request = False

    def __init__(self):
        ...

    @login_required()
    def post(self):
        _request = request.json
        site_id = _request.get("site_id", None)
        print(_request)

        if session.get("level", inf) <= 2:
            _ret = public.siteDatas["*"]
        else:
            _userSites = session.get("sites", [])
            if _userSites:
                _ret = public.siteDatas[_userSites]
            else:
                _ret = []

        if site_id is None:
            return dumps([{y: z for y, z in x.items() if y in ["id", "site_name"]} for x in _ret])

        _ret = [x["areas"] for x in _ret if x["id"] == site_id]
        if _ret:
            _ret = _ret[0]

        block_id = _request.get("block_id", None)
        if block_id is None:
            return dumps([{y: z for y, z in x.items() if y in ["id", "name"]} for x in _ret])

        _ret = [x for x in _ret if x["id"] == block_id]
        if not _ret:
            return dumps([])
        _ret = _ret[0]

        system_id = _request.get("system_id", None)
        if system_id is None:
            return dumps(_ret["systems"])
        _devices = [{"device_id": x.device_id, "device_name": x.device_name, "connected": x.connected} for x in public.deviceClients.values() if x.site_id == site_id
                    and x.block_id == block_id and x.system_id == system_id]
        return dumps(_devices)


modules.app.add_url_rule(f"/api/test", view_func=SystemAPI.as_view("api111111"))
