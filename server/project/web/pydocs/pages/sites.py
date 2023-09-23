from os.path import splitext, basename
from json import dumps
from flask import render_template, request
from flask.views import View
from project.modules import modules


class Page(View):
    init_every_request = False
    fileName = splitext(basename(__file__))[0]

    def __init__(self):
        super().__init__()

    def dispatch_request(self, site_id="*"):
        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'add':
                site_name = request.form.get('siteName')
                area_names = request.form.getlist('areaName[]')
                area_systems = request.form.getlist('areaSystems[]')

                areas = []
                for name, systems in zip(area_names, area_systems):
                    if not name:
                        continue
                    if systems:
                        system_list = [int(system.strip()) for system in systems.split(",")]
                    else:
                        system_list = []
                    area = {"name": name, "systems": system_list}
                    areas.append(area)

                if site_name:
                    result = modules.database.sites.add(site_name, areas)
                    if result.success:
                        return "Successfully added a new site"
                    else:
                        return "Failed to add new site"
                else:
                    return "Site name is required"

            else:
                site_id = request.form.get('deleteSiteId')
                if site_id:
                    result = modules.database.sites.delete(site_id)
                    if result.success:
                        return "Successfully deleted the site"
                    else:
                        return "Failed to delete the site"
                else:
                    return "Site ID is required"

        if site_id == "*":
            sites = modules.database.sites.getAll(_convert=True)
            if sites.success:
                sites = sites.data
            else:
                sites = []
            return render_template(f'{self.fileName}.html', sites=sites)
        else:
            sites = modules.database.sites.get(["id", site_id])
            if sites.success:
                sites = [sites.data]
            else:
                sites = []
            return render_template(f'{self.fileName}-singlePage.html', sites=sites)


modules.app.add_url_rule(f"/{Page.fileName}/<string:site_id>", methods=['GET', 'POST', 'DELETE'], view_func=Page.as_view(name=Page.fileName + "id"))
modules.app.add_url_rule(f"/{Page.fileName}/", methods=['GET', 'POST'], view_func=Page.as_view(name=Page.fileName + "withoutId"))
