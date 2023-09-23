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

    def dispatch_request(self, device_id=None, groups=None, scenarios=None):
        addScenario = request.form.get('action')
        addGroup = request.form.get('group')
        scenarios = modules.database.devices.getInList(["device_id", [device_id]], "scenarios")
        if scenarios.success:
            scenarios = scenarios.data
        groups = modules.database.devices.getInList(["device_id", [device_id]], "groups")
        if groups.success:
            groups = groups.data

        if addScenario:
            scenarioName = request.form.get('scenarioName')
            days = request.form.getlist('gunler[]')
            startTimes = request.form.getlist('startTime[]')
            endTimes = request.form.getlist('endTime[]')
            groups = request.form.getlist('groups[]')

            result = []

            time_result = []

            for start, end in zip(startTimes, endTimes):
                start_hour, start_minute = map(int, start.split(':'))
                end_hour, end_minute = map(int, end.split(':'))
                time_result.append([[start_hour, start_minute], [end_hour, end_minute]])


            result.append(list(map(int, days)))
            result.append(time_result)
            result.append(list(map(int, groups)))
            print(result)

            # Send To Device
            name = scenarioName
            data = result

            sendToDevice = modules.system.sendConfigToDevice(device_id, name, data)
            if sendToDevice:
                return "Senaryo cihaza başarıyla gönderildi"
            if not sendToDevice:
                return "Cihaza Gonderilemedi..."

        if addGroup =='getGroup':
            pins = request.form.getlist('pins[]')
            name = request.form.get('name')
            humidity = request.form.getlist('humidity[]')
            print(humidity)
            result = [name, pins]
            print(result)

            if pins and name:
                return "Grup Kaydedildi"

        return render_template(f'/yonetimPaneli/{device_id}.html', device_id=device_id, groups=groups, scenarios=scenarios)


modules.app.add_url_rule('/<string:device_id>', methods=["POST", "GET"], view_func=page.as_view(name=page.fileName))