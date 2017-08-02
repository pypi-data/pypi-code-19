import asyncio

import peewee
from muffin import plugins
from muffin.utils import MuffinException
from muffin.utils import Struct

import peewee_async
from peewee_migrate import Router
from playhouse.csv_utils import dump_csv
from playhouse.csv_utils import load_csv
from playhouse.db_url import connect
from playhouse.db_url import register_database


@asyncio.coroutine
def peewee_middleware_factory(app, handler):
    database = app.ps.peewee_async.database

    @asyncio.coroutine
    def middleware(request):
        yield from database.connect_async(loop=app.loop)
        try:
            return (yield from handler(request))
        except Exception:
            yield from database.close_async()
            raise

    return middleware


class Plugin(plugins.BasePlugin):
    name = 'peewee_async'
    defaults = {
        'connection': '',
        'connection_params': {},
        'migrations_path': 'migrations',
    }

    def __init__(self, app=None, **options):
        self.database = peewee.Proxy()
        self.models = Struct()
        self.router = None
        self.manager = None
        super().__init__(app, **options)

    def setup(self, app):
        super().setup(app)

        self.database.initialize(connect(self.cfg.connection, **self.cfg.connection_params))
        if not isinstance(self.database.obj, peewee_async.AsyncDatabase):
            raise plugins.PluginException(
                'Plugin `{}` requires for database schema using aiopg'.format(self.name))

        self.database.set_allow_sync(False)
        self.manager = peewee_async.Manager(self.database, loop=app.loop)
        self.router = Router(self.database, migrate_dir=self.cfg.migrations_path)

        def pw_migrate(name: str=None, fake: bool=False):
            with self.manager.allow_sync():
                return self.router.run(name, fake=fake)

        self.app.manage.command(pw_migrate)

        def pw_rollback(name: str):
            with self.manager.allow_sync():
                self.router.rollback(name)

        self.app.manage.command(pw_rollback)

        def pw_create(name: str='auto', auto: bool=False):
            with self.manager.allow_sync():
                if auto:
                    auto = list(self.models.values())
                return self.router.create(name, auto)

        self.app.manage.command(pw_create)

        def pw_list():
            with self.manager.allow_sync():
                self.router.logger.info('Migrations are done:')
                self.router.logger.info('\n'.join(self.router.done))
                self.router.logger.info('')
                self.router.logger.info('Migrations are undone:')
                self.router.logger.info('\n'.join(self.router.diff))

        self.app.manage.command(pw_list)

        @self.app.manage.command
        def pw_merge():
            with self.manager.allow_sync():
                self.router.merge()

        self.app.manage.command(pw_merge)

        def pw_dump(table: str, path: str='dump.csv'):
            with self.manager.allow_sync():
                model = self.models.get(table)
                if model is None:
                    raise MuffinException('Unknown db table: %s' % table)

                with open(path, 'w') as fh:
                    dump_csv(model.select().order_by(model._meta.primary_key), fh)
                    self.app.logger.info('Dumped to %s' % path)

        self.app.manage.command(pw_dump)

        def pw_load(table: str, path: str='dump.csv', pk_in_csv: bool=False):
            with self.manager.allow_sync():
                model = self.models.get(table)
                if model is None:
                    raise MuffinException('Unknown db table: %s' % table)

                load_csv(model, path)
                self.app.logger.info('Loaded from %s' % path)

        self.app.manage.command(pw_load)

    def start(self, app):
        app.middlewares.insert(0, peewee_middleware_factory)

    def finish(self, app):
        if hasattr(self.database.obj, 'close_all'):
            with self.manager.allow_sync():
                self.database.close_all()

    def register(self, model):
        self.models[model._meta.db_table] = model
        model._meta.database = self.database
        return model


register_database(peewee_async.PostgresqlDatabase, 'postgres+aiopg', 'postgresql+aiopg')
register_database(peewee_async.PooledPostgresqlDatabase, 'postgres+aiopg+pool', 'postgresql+aiopg+pool')
