from . import config
import app
import hashlib


class Login:

    def GET(self):
        form = config.form()
        return config.render.login(form)

    def POST(self):
        i = config.web.input()
        pwdhash = hashlib.md5(i.password).hexdigest()
        check = config.model.validate_user(i.username, pwdhash)
        username = check['username']
        privilege = check['privilege']
        if check:
            app.session.loggedin = True
            app.session.username = username
            app.session.privilege = privilege
            raise config.web.seeother('/')
        else:
            form = config.form()
            return config.render.login(form)