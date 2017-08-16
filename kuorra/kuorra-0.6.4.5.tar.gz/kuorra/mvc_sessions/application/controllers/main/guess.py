import config
import app


class Guess:

    def GET(self):
        if app.session.loggedin is True:
            username = app.session.username
            privilege = app.session.privilege
            params = {}
            params['username'] = username
            params['privilege'] = privilege
            return config.render.guess(params)
        else:
            raise config.web.seeother('/login')
