import config
import app

class Index:

    def GET(self):  
        if app.session.loggedin == True:
            username = app.session.username
            privilege = app.session.privilege
            if  privilege == 1:
                raise config.web.seeother('/guess')
            elif privilege == 0:
                return config.render.index(username)
        else:
            raise config.web.seeother('/login')
