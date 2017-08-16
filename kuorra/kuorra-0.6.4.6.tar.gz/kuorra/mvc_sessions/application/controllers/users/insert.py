from . import config
import hashlib
import app


class Insert():

    def __init__(self):
        pass

    def GET(self):
        if app.session.loggedin is True:
            #username = app.session.username
            privilege = app.session.privilege
            if  privilege == 0:
                return self.GET_INSERT()
            elif privilege == 1:
                raise config.web.seeother('/guess')
        else:
            raise config.web.seeother('/login')

    def POST(self):
        if app.session.loggedin is True:
            #username = app.session.username
            privilege = app.session.privilege
            if  privilege == 0:
                return self.POST_INSERT()
            elif privilege == 1:
                raise config.web.seeother('/guess')
        else:
            raise config.web.seeother('/login')

    def GET_INSERT(self):
        return config.render.insert()

    def POST_INSERT(self):
        form = config.web.input()
        pwdhash = hashlib.md5(form.password).hexdigest()

        config.model.insert_users(
            form['username'],
            pwdhash,
            form['privilege']
        )
        raise config.web.seeother('/users')
