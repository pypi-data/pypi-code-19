import os
import json
from logging import getLogger, basicConfig


basicConfig(format='%(asctime)s %(name)s:%(lineno)s %(levelname)s: %(message)s')
logger = getLogger('jct')


def _get_list(l):
    """Remove duplicates while preserving order"""
    seen = set()
    seen_add = seen.add
    return [i for i in l if not (i in seen or seen_add(i))]


def _merge_dict(d1, d2):
    """Merge two dictionaries maintaining values in nested dicts"""
    if isinstance(d2, dict):
        for k in d2.keys():
            if d1.get(k, None) and isinstance(d1[k], dict):
                if not isinstance(d2[k], dict):
                    # Assume default dict is correct here.
                    e = 'Expected {0} to be {1}'.format(type(d2[k]), dict)
                    raise ValueError(e)
                _merge_dict(d1[k], d2[k])
            else:
                d1[k] = d2[k]
        return d1
    else:
        return d1.update(d2)


def _create_dict(d, l, v):
    if (len(l) == 1):
        d.setdefault(l.pop(0), v)
        return d
    else:
        k = l.pop(0)
        d.setdefault(k, {})
        d[k].update(_create_dict(d[k], l, v))
        return d
    return _create_dict


def load_env_vars(prefix):
    prefix = '{}__'.format(prefix.rstrip('_')).lower()
    a_env = os.environ
    o = {}
    for key in [k.lower() for k in a_env.keys() if prefix.lower() in k.lower()]:
        l = key.lower().replace(prefix, '').split('__')
        o.update(_create_dict(o, l, a_env[key]))
    return o


def create_config(env_prefix='JCT'):
    """Loads config values from env vars as well as config values from
    env vars. Returns a Yact object with the found values"""
    home_path = os.path.join(os.path.expanduser('~'), '.jct')
    default_paths = '/etc/jct,{0}'.format(home_path)
    env = os.getenv('JCT_ENV', 'default')
    default_file = os.getenv('JCT_DEFAULT_FILE', 'default.json')
    config_paths = os.getenv('JCT_CONFIG_PATHS', default_paths).split(',')
    return Jct(env=env, default_file=default_file, config_paths=config_paths,
               **load_env_vars(env_prefix))


class Config(dict):
    """dict object that allows for period separated gets:
    a_config.get('some.key', default) ==
        a_config.get('some', {}).get('key', default)
    given:
        a_config == {"some": {"key": "some value"}}"""

    def get(self, key, default=None):
        keys = key.split('.')
        d = {}
        for key in self.keys():
            d[key] = self[key]
        for k in keys:
            if not isinstance(d, dict):
                return default
            else:
                d = d.get(k)
                if d is None:
                    return default
        return d


class Jct(Config):
    """Inherits Config class with the addition of loading JSON config files"""

    def __init__(self, env='default', default_file='default.json',
                 config_paths=[], **kw):
            _get_filename = lambda f: '{0}.json'.format(f.split('.')[0])
            _cf = lambda f, c: [os.path.join(p, f) for p in c
                                if os.path.isfile(os.path.join(p, f))]
            configs = [x for f in [default_file, env]
                       for x in _cf(_get_filename(f), config_paths)]
            # Build config dict
            obj = {}
            for c in _get_list(configs):
                obj = _merge_dict(obj, self._get_json_file(c))
            # Override with env vars
            obj = _merge_dict(obj, kw)
            # pass to dict super to create obj as dict
            super(Config, self).__init__(**obj)

    def _get_json_file(self, f):
        o = {}
        try:
            with open(f) as fp:
                o = json.load(fp)
        except Exception as e:
            logger.warning("{0}: {1} will be skipped.".format(e, f))
        finally:
            return o


def main(as_module=False):
    print(create_config())


if __name__ == "__main__":
    main()
