import pytest
import mock
import json

import meinconf


class TestConfig(object):
    app_name = 'test_app'
    app_name_upper = app_name.upper()
    config_var = '%s_CONFIG' % app_name_upper
    envvars_prefix = app_name_upper
    environ = dict(
        APP_NAME=app_name,
        APP_ENV='dev',
        NOT_PREFIXED='Not in end result',
        TEST_APP_JSON_STRING='{"truth": true, "string": "Why hello"}',
        TEST_APP_STRING='world',
    )
    end_environ = dict(
        JSON_STRING=json.loads(environ['TEST_APP_JSON_STRING']),
        STRING=environ['TEST_APP_STRING'],
    )
    root_path = '.'

    def _factory(self):
        return meinconf.Config(self.app_name, root_path=self.root_path)

    @pytest.fixture(scope='function', autouse=True)
    def c(self):
        return self._factory()

    @mock.patch.dict('os.environ', environ, clear=True)
    def test_from_envvars(self, c):
        c.from_envvars(self.envvars_prefix)
        assert c.as_dict() == self.end_environ

    @mock.patch.dict('os.environ', {config_var: 'nonce'}, clear=True)
    @mock.patch.object(meinconf.Config, 'from_any')
    def test_from_envvar(self, mock_func, c):
        var = '%s_CONFIG' % self.app_name.upper()
        c.from_envvar(var)
        assert mock_func.called_once_with('nonce')

    @mock.patch.dict('os.environ', environ, clear=True)
    def test_configure(self, c):
        c.configure()
        assert c.as_dict() == self.end_environ


class TestFlaskConfig(object):
    def _flask_app_factory(self, app_name='flask_app', root_path='.', config={'CONFIG_TEST': 'yes'}):
        app = mock.MagicMock()
        app.name = app_name
        app.root_path = root_path
        app.config = config.copy()
        return app

    def test_init_with_flask_app(self):
        app = self._flask_app_factory()

        app_name = app.name
        root_path = app.root_path
        defaults = app.config

        config = meinconf.FlaskConfig(
            app=app,
        )

        assert config.app_name == app_name
        assert config.root_path == root_path
        assert config.defaults == defaults
        for k, v in defaults.items():
            assert getattr(config, k.upper()) == v
        assert config.as_dict() == defaults

    def test_init_with_flask_app_and_overrides(self):
        app = self._flask_app_factory()

        app_name = 'overridden_app_name'
        root_path = 'overridden_root_path'
        defaults = {'CONFIG_OVERRIDE': True}

        config = meinconf.FlaskConfig(
            app=app,
            app_name=app_name,
            root_path=root_path,
            defaults=defaults,
        )

        assert config.app_name == app_name
        assert config.root_path == root_path
        assert config.defaults == defaults
        for k, v in defaults.items():
            assert getattr(config, k.upper()) == v
        assert config.as_dict() == defaults

