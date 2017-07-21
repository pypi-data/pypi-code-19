from . import config
import app


class Delete:

    def GET(self, username):
        if app.session.loggedin is True:
            #username = app.session.username
            privilege = app.session.privilege
            if  privilege == 0:
                return self.GET_DELETE(username)
            elif privilege == 1:
                raise config.web.seeother('/guess')
        else:
            raise config.web.seeother('/login')

    def POST(self, username):
        if app.session.loggedin is True:
            #username = app.session.username
            privilege = app.session.privilege
            if  privilege == 0:
                return self.POST_DELETE(username)
            elif privilege == 1:
                raise config.web.seeother('/guess')
        else:
            raise config.web.seeother('/login')

    def GET_DELETE(self, username):
        result = config.model.get_users(username)
        return config.render.delete(result)

    def POST_DELETE(self, username):
        form = config.web.input()
        config.model.delete_users(form['username'])
        raise config.web.seeother('/users')
