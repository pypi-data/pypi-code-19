from . import config
import app


class Delete:

    def GET(self, username, **k):
        if app.session.loggedin is True:
            #username = app.session.username
            privilege = app.session.privilege
            if  privilege == 0:
                return self.GET_DELETE(username)
            elif privilege == 1:
                raise config.web.seeother('/guess')
        else:
            raise config.web.seeother('/login')

    def POST(self, username, **k):
        if app.session.loggedin is True:
            #username = app.session.username
            privilege = app.session.privilege
            if  privilege == 0:
                return self.POST_DELETE(username)
            elif privilege == 1:
                raise config.web.seeother('/guess')
        else:
            raise config.web.seeother('/login')

    def GET_DELETE(self, username, **k):
        message = None
        result = config.model.get_users(username)
        return config.render.delete(result, message)

    def POST_DELETE(self, username, **k):
        form = config.web.input()
        e = config.model.delete_users(form['username'])
        if e is False:
            message = "Error al eliminar"
            result = config.model.get_users(form['username'])
            return config.render.delete(result, message)
        else:
            raise config.web.seeother('/users')
