from . import config
import app


class View:

    def GET(self, username):
        if app.session.loggedin is True:
            #username = app.session.username
            privilege = app.session.privilege
            if  privilege == 0:
                return self.GET_VIEW(username)
            elif privilege == 1:
                raise config.web.seeother('/guess')
        else:
            raise config.web.seeother('/login')

    def GET_VIEW(self, username):
        username = username
        result = config.model.get_users(username)
        return config.render.view(result)
