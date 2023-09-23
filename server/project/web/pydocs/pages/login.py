__all__ = ["page"]

from os.path import splitext, basename

from flask import render_template
from flask.views import View

from project.modules import modules


class page(View):
    init_every_request = False
    fileName = splitext(basename(__file__))[0]

    def __init__(self):
        super().__init__()

    def dispatch_request(self):
        return render_template(f'{self.fileName}.html')


modules.app.add_url_rule(f"/{page.fileName}", view_func=page.as_view(name=page.fileName))
