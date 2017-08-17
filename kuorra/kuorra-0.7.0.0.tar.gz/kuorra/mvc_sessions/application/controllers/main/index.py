from . import config
import app


class Index:

    def GET(self):
        if app.session.loggedin is True:
            username = app.session.username
            privilege = app.session.privilege
            if  privilege == 0:
                params = {}
                params['username'] = username
                params['privilege'] = privilege
                #return config.render.index(username)
                return config.render.index(params)
            elif privilege == 1:
                raise config.web.seeother('/guess')
        else:
            raise config.web.seeother('/login')
