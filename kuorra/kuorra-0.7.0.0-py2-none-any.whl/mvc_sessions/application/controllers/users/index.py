from . import config
import app


class Index:

    def GET(self):
        if app.session.loggedin is True:
            #username = app.session.username
            privilege = app.session.privilege
            if  privilege == 0:
                return self.GET_INDEX()
            elif privilege == 1:
                raise config.web.seeother('/guess')
        else:
            raise config.web.seeother('/login')

    def GET_INDEX(self):
        result = config.model.get_all_users()
        return config.render.index(result)
