import config
import app

class Guess:

    def GET(self):  
        if app.session.loggedin == True:
            username = app.session.username
            privilege = app.session.privilege
            return config.render.guess(username)
        else:
            raise config.web.seeother('/login')
