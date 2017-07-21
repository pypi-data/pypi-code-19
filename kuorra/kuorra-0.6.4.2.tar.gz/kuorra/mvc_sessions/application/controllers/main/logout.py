import config
import app


class Logout:
    def GET(self):
        app.session.username = None
        app.session.privilege = 0
        app.session.kill()
        raise config.web.seeother('/login')