__all__ = ["Core"]
from aioorm import AioDbFactory


class Core:
    def __init__(self, app=None):
        self.sqldatabases = {}
        if app:
            self.init_app(app)
        else:
            pass

    def init_app(self, app):
        if app.config.SQLDBURLS and isinstance(app.config.SQLDBURLS, dict):
            self.SQLDBURLS = app.config.SQLDBURLS
            self.app = app
            for dbname, dburl in app.config.SQLDBURLS.items():
                db = AioDbFactory(dburl)
                self.sqldatabases[dbname] = db
        else:
            raise ValueError(
                "nonstandard sanic config SQLDBURLS,SQLDBURLS must be a Dict[dbname,dburl]")

        @app.listener('before_server_start')
        async def setup_db(app, loop):
            for name, db in self.sqldatabases.items():
                tempdb = await db.connect(loop)
                print(name, "successfully connected!")

        @app.listener('after_server_start')
        async def notify_server_started(app, loop):
            print('Databases successfully connected!')

        @app.listener('before_server_stop')
        async def notify_server_stopping(app, loop):
            print('Databases disconnecting')

        @app.listener('after_server_stop')
        async def close_db(app, loop):
            for name, db in self.sqldatabases.items():
                await db.close()
                print(name, 'disconnected')

        if "extensions" not in app.__dir__():
            app.extensions = {}
        app.extensions['SanicAioOrm'] = self

    def init_proxys(self, **kwargs):
        """初始化peewee的代理数据库对象
        """
        for name, proxy in kwargs.items():
            try:
                proxy.initialize(self.sqldatabases[name])
            except:
                print("unknown Databases {}".format(name))
