from . import config
import app
import hashlib


class Login:
    
    def __init__(self):
        pass

    def GET(self, *a):
        message = None
        return config.render.login(message)

    def POST(self, *a):
        i = config.web.input()
        pwdhash = hashlib.md5(i.password).hexdigest()
        check = config.model.validate_user(i.username, pwdhash)
        if check:
            app.session.loggedin = True
            app.session.username = check['username']
            app.session.privilege = check['privilege']
            raise config.web.seeother('/')
        else:
            message = "User or Password are not correct!!!!"
            return config.render.login(message)