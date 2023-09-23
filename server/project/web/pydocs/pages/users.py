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

    def dispatch_request(self, user_id="*"):
        action = request.form.get('action')
        deleteAction = request.form.get('delete')
        update = request.form.get('update')
        updatePass = request.form.get('changePass')

        if action == 'add':
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            username = request.form.get('username')
            tagname = request.form.get('tagname')
            password = request.form.get('password')
            sites = request.form.get('sites')
            level = request.form.get('level')

            if firstname and lastname and username and tagname and password:
                if not level:
                    print("Level default 3 yapiliyor")
                    level = '3'
                if not sites:
                    print("Sites empty")
                    sites = []
                result = modules.database.users.add(firstname, lastname, username, tagname, password, sites, level)
                if result.success:
                    return "Successfully added a new user"
                else:
                    return "Failed to add new user"
            else:
                return "Please fill in all the required fields"

        elif deleteAction:

            user_id = deleteAction
            if user_id:
                result = modules.database.users.delete(["id", int(user_id.split('_')[1])])
                if result.success:
                    return "Successfully deleted the user"

                else:
                    return "Failed to delete the user"
            else:
                return "User ID is required"

        if user_id == "*":
            users = modules.database.users.getAll("id,firstname,lastname,tagname,username,sites,level")
            print(users.data, users.success, users.desc)
            if users.success:
                users = users.data

            if update:
                firstname = request.form.get('firstname')
                lastname = request.form.get('lastname')
                username = request.form.get('username')
                tagname = request.form.get('tagname')
                sites = request.form.get('sites')
                level = request.form.get('level')
                idn = request.form.get('idn')

                result = modules.database.users.update(["id", idn], {
                    "firstname": firstname,
                    "lastname": lastname,
                    "username": username,
                    "tagname": tagname,
                    "sites": sites,
                    "level": level
                })
                print(result)
                if result.success:
                    return "Successfully updated"
                else:
                    return "Failed"

            if updatePass:
                idn = request.form.get('idn')
                new_password = request.form.get('password')
                result = modules.database.users.changePassword(idn, new_password)
                if result.success:
                    return "Sifre Degistirildi..."

            return render_template(f'{self.fileName}.html', users=users)

        else:
            users = modules.database.users.get(["id", user_id], "*")

            if users.success:
                if users.data is not None:
                    users = [users.data]

            return render_template(f'{self.fileName}-singlePage.html', users=users)


modules.app.add_url_rule(f"/{page.fileName}/<string:user_id>", methods=['GET', 'POST'], view_func=page.as_view(name=page.fileName + "id"))
modules.app.add_url_rule(f"/{page.fileName}/", methods=['GET', 'POST'], view_func=page.as_view(name=page.fileName + "withoutId"))