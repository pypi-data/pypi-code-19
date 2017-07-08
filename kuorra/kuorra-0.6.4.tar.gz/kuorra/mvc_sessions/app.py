#Author : Salvador Hernandez Mendoza
#Email  : salvadorhm@gmail.com
#Twitter: @salvadorhm
import web
import application
import hashlib
import config

ssl = True #activate ssl certificate 

urls = (
    '/', 'application.controllers.main.index.Index',
    '/login', 'application.controllers.main.login.Login',
    '/logout', 'application.controllers.main.logout.Logout',
    '/guess', 'application.controllers.main.guess.Guess',
)

app = web.application(urls, globals())

if ssl == True:
    from web.wsgiserver import CherryPyWSGIServer
    CherryPyWSGIServer.ssl_certificate = "ssl/server.crt" 
    CherryPyWSGIServer.ssl_private_key = "ssl/server.key"

store = web.session.DiskStore('sessions')

if web.config.get('_session') is None:
    db = config.db
    store = web.session.DBStore(db, 'sessions')
    session = web.session.Session(
        app,
        store,
        initializer={
        'login': 0,
        'privilege': 0,
        'user':'anonymous',
        'loggedin':False,
        'count' : 0
        }
        )
    web.config._session = session
    web.config.session_parameters['cookie_name'] = 'kuorra'
    web.config.session_parameters['timeout'] = 10
    web.config.session_parameters['expired_message'] = 'Session expired'
    web.config.session_parameters['ignore_expiry'] = False
    web.config.session_parameters['ignore_change_ip'] = False
    web.config.session_parameters['secret_key'] = 'fLjUfxqXtfNoIldA0A0J'
else:
    session = web.config._session

class count:
    def GET(self):
        session.count += 1
        return str(session.count)

def internalerror():
    raise config.web.seeother('/')

def notfound():
    raise config.web.seeother('/')

if __name__ == "__main__":
    web.config.debug = False
    web.config.db_printing = False
    app.internalerror = internalerror
    app.notfound = notfound
    app.run()
