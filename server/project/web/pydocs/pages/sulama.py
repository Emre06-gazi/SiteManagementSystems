__all__ = ["page"]

from os.path import splitext, basename
from json import dumps

from flask import render_template, request
from flask.views import View

from project.modules import modules


class page(View):
    init_every_request = False
    fileName = splitext(basename(__file__))[0]

    def __init__(self):
        super().__init__()

    def dispatch_request(self, device_id=None, scenarios=None, groups=None):
        device_id = "b8d61ab24ee8" # manuel eklendi degisekecek.
        scenarios_data = modules.database.devices.getInList(["device_id", [device_id]], "scenarios")
        if scenarios_data.success:
            scenarios = scenarios_data.data
        groups_data = modules.database.devices.getInList(["device_id", [device_id]], "groups")
        if groups_data.success:
            groups = groups_data.data

        print(scenarios)
        print(groups)

        return render_template(f"{self.fileName}.html", device_id=device_id, groups=groups, scenarios=scenarios)


modules.app.add_url_rule(f"/{page.fileName}", methods=['POST', 'GET'], view_func=page.as_view(name=page.fileName))
