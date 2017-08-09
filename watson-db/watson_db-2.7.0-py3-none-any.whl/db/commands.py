# -*- coding: utf-8 -*-
import codecs
import collections
import enum
import json
import os
import sys
from datetime import datetime

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlacodegen import codegen
from sqlalchemy import create_engine, inspect, schema
from sqlalchemy.ext.declarative.clsregistry import _ModuleMarker

from watson.common import imports
from watson.console import ConsoleError, command
from watson.console.decorators import arg
from watson.db import engine, fixtures, session
from watson.di import ContainerAware


class Config(AlembicConfig):
    def get_template_directory(self):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, 'alembic', 'templates')


class BaseDatabaseCommand(ContainerAware):
    __ioc_definition__ = {
        'init': {
            'config': lambda container: container.get('application.config')['db']
        }
    }

    def __init__(self, config):
        self.config = config


class Database(command.Base, BaseDatabaseCommand):
    """Database commands.
    """
    name = 'db'

    @property
    def metadata(self):
        metadatas = {}
        for name, options in self.config['connections'].items():
            metadatas[name] = self._load_metadata(options['metadata'])
        return metadatas

    @property
    def connections(self):
        connections = {}
        for name, options in self.config['connections'].items():
            connections[name] = options['connection_string']
        return connections

    @property
    def sessions(self):
        return self._session_or_engine('session')

    @property
    def engines(self):
        return self._session_or_engine('engine')

    def _load_metadata(self, metadata):
        if isinstance(metadata, str):
            try:
                return imports.load_definition_from_string(metadata)
            except Exception as e:
                raise ConsoleError(
                    'Missing connection metadata for {} ({})'.format(
                        metadata, e))

    def _session_or_engine(self, type_):
        """Retrieves all the sessions or engines from the container.
        """
        results = {}
        for name in self.config['connections']:
            obj_name = getattr(globals()[type_], 'NAME').format(name)
            results[name] = self.container.get(obj_name)
        return results

    @arg('drop', action='store_true', default=False, optional=True)
    def create(self, drop):
        """Create the relevant databases.
        """
        engines = self.engines
        for database, model_base in self.metadata.items():
            self.write('Creating database {}...'.format(database))
            engine.create_db(engines[database], model_base, drop=drop)
        self.write('Created the databases.')
        return True

    @arg()
    def populate(self):
        """Add data from fixtures to the database(s).
        """
        if 'fixtures' not in self.config:
            self.write('No fixtures to add.')
            return False
        self.write('Adding fixtures...')
        sessions = self.sessions
        total = fixtures.populate_all(sessions, self.config['fixtures'])
        self.write('Added {} fixtures to {} database(s).'.format(
            total, len(sessions)))
        return True

    def _get_models_in_session(self, name, model):
        results = []
        if isinstance(model, _ModuleMarker):
            return None
        inst = inspect(model)
        attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
        for obj in self.sessions[name].query(model):
            fields = {}
            new_obj = collections.OrderedDict()
            new_obj['class'] = imports.get_qualified_name(model)
            attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
            for column in attr_names:
                value = getattr(obj, column)
                if isinstance(value, enum.Enum):
                    value = value.value
                elif isinstance(value, datetime):
                    value = str(value)
                elif isinstance(value, bytes):
                    value = value.decode('utf-8')
                fields[column] = value
            new_obj['fields'] = collections.OrderedDict(
                sorted(fields.items(), key=lambda k: k[0]))
            results.append(new_obj)
        return results

    @arg('models', optional=True)
    @arg('output_to_stdout', default=False, optional=True)
    def generate_fixtures(self, models, output_to_stdout):
        """Generate fixture data in json format.

        Args:
            models (string): A comma separated list of models to output
            output_to_stdout (boolean): Whether or not to output to the stdout
        """
        if models:
            models = models.split(',')
        for name, options in self.config['connections'].items():
            metadata = self._load_metadata(options['metadata'])
            for model in metadata._decl_class_registry.values():
                model_name = imports.get_qualified_name(model)
                if models and model_name not in models:
                    continue
                records = self._get_models_in_session(name, model)
                if not records:
                    continue
                records = json.dumps(records, indent=4)
                if output_to_stdout:
                    self.write(records)
                else:
                    model_name, path = fixtures.save(
                        model, records, self.config['fixtures'])
                    self.write(
                        'Created fixture for {} at {}'.format(model_name, path))

    @arg()
    def dump(self):
        """Print the Schema of the database.
        """
        def dump_sql(sql, *multiparams, **params):
            self.write(str(sql))

        connections = self.connections
        for database, model_base in self.metadata.items():
            self.write('Schema for "{}" from metadata {}...'.format(
                database, repr(model_base)))
            self.write()
            _engine = create_engine(
                connections[database], strategy='mock', executor=dump_sql)
            model_base.metadata.create_all(_engine, checkfirst=False)
        return True

    @arg('outfile', action='store_true', default=False, optional=True)
    @arg('tables', action='store_true', default=None, optional=True)
    @arg('connection_string', optional=True)
    def generate_models(self, connection_string=None, tables=None, outfile=None):
        """Generate models from an existing database schema.

        Args:
            connection_string (string): The database to connect to
            tables (string): Tables to process (comma-separated, default: all)
            outfile (string): File to write output to (default: stdout)
        """
        tables = tables.split(',') if tables else None
        outfile = codecs.open(outfile, 'w', encoding='utf-8') if outfile else sys.stdout
        connections = self.connections
        databases = {database: connections[database] for database, _ in self.metadata.items()}
        if connection_string:
            databases = {connection_string.split('/')[-1]: connection_string}
        for database, connection in databases.items():
            self.write('SqlAlchemy model classes for "{}"'.format(database))
            self.write()
            _engine = create_engine(connection)
            metadata = schema.MetaData(_engine)
            metadata.reflect(_engine, only=tables)
            generator = codegen.CodeGenerator(metadata)
            generator.render(outfile)


class Migrate(command.Base, BaseDatabaseCommand):
    """Alembic integration with Watson.
    """
    name = 'db:migrate'

    def _check_migrations(self):
        if 'migrations' not in self.config:
            raise ConsoleError(
                'No migrations configuration can be found.')

    @property
    def database_names(self):
        names = []
        for name in self.config['connections']:
            names.append(name)
        return names

    @property
    def directory(self):
        self._check_migrations()
        return os.path.abspath(self.config['migrations']['path'])

    @property
    def alembic_config_file(self):
        return os.path.join(self.directory, 'alembic.ini')

    def alembic_config(self, with_ini=True, relative_script_location=True):
        self._check_migrations()
        directory = self.config['migrations']['path']
        args = []
        if with_ini:
            args.append(self.alembic_config_file)
        config = Config(*args)
        script_location = directory
        if not relative_script_location:
            script_location = os.path.abspath(directory)
        config.set_main_option('script_location', script_location)
        config.set_main_option('databases', ', '.join(self.database_names))
        config.watson = {
            'config': self.config,
            'container': self.container
        }
        return config

    @arg()
    def init(self):
        """Initializes Alembic migrations for the project.
        """
        config = self.alembic_config(with_ini=False)
        config.config_file_name = self.alembic_config_file
        alembic_command.init(config, config.get_main_option('script_location'), 'watson')
        return True

    @arg()
    def history(self, rev_range):
        """List changeset scripts in chronological order.

        Args:
            rev_range: Revision range in format [start]:[end]
        """
        config = self.alembic_config()
        alembic_command.history(config, rev_range)
        return True

    @arg()
    def current(self):
        """Display the current revision for each database.
        """
        config = self.alembic_config()
        alembic_command.current(config)
        return True

    @arg('sql', action='store_true', default=False, optional=True)
    @arg('autogenerate', action='store_true', default=False, optional=True)
    @arg('message', optional=True, default='Revision')
    def revision(self, sql=False, autogenerate=False, message=None):
        """Create a new revision file.

        Args:
            sql (bool): Don't emit SQL to database - dump to standard output instead
            autogenerate (bool): Populate revision script with andidate migration operatons, based on comparison of database to model
            message (string): Message string to use with 'revision'
        """
        config = self.alembic_config(relative_script_location=False)
        return alembic_command.revision(
            config, message, autogenerate=autogenerate, sql=sql)

    @arg('sql', action='store_true', default=False, optional=True)
    @arg('tag', default=None, optional=True)
    @arg('revision', default=None)
    def stamp(self, sql=False, tag=None, revision='head'):
        """'stamp' the revision table with the given revision; don't run any migrations.

        Args:
            sql (bool): Don't emit SQL to database - dump to standard output instead
            tag (string): Arbitrary 'tag' name - can be used by custom env.py scripts
            revision (string): Revision identifier
        """
        config = self.alembic_config()
        alembic_command.stamp(config, revision, tag=tag, sql=sql)
        return True

    @arg('sql', action='store_true', default=False, optional=True)
    @arg('tag', default=None, optional=True)
    @arg('revision', default='head', nargs='?')
    def upgrade(self, sql=False, tag=None, revision='head'):
        """Upgrade to a later version.

        Args:
            sql (bool): Don't emit SQL to database - dump to standard output instead
            tag (string): Arbitrary 'tag' name - can be used by custom env.py scripts
            revision (string): Revision identifier
        """
        config = self.alembic_config()
        alembic_command.upgrade(config, revision, tag=tag, sql=sql)
        return True

    @arg('sql', action='store_true', default=False, optional=True)
    @arg('tag', default=None, optional=True)
    @arg('revision', default='-1', nargs='?')
    def downgrade(self, sql=False, tag=None, revision='-1'):
        """Revert to a previous version.
        """
        config = self.alembic_config()
        alembic_command.downgrade(config, revision, tag=tag, sql=sql)
        return True

    @arg()
    def branches(self):
        """Show current un-spliced branch points.
        """
        config = self.alembic_config()
        alembic_command.branches(config)
        return True
