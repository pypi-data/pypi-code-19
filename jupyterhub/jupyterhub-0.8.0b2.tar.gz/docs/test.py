import os

from traitlets.config import Config, Configurable
from traitlets import Unicode


class A(Configurable):
    a = Unicode(config=True).tag(config_env='A')


class B(A):
    b = Unicode(config=True).tag(config_env='B')


def load_env_config(class_list):
    """Create a config object for any traits with `config_env` metadata"""
    config = Config()
    seen = set()
    for config_cls in class_list:
        for cls in config_cls.mro():
            if cls is Configurable:
                break
            if cls in seen:
                continue
            seen.add(cls)
            for name, trait in cls.class_own_traits(config=True).items():
                key = trait.metadata.get('config_env')
                if key and os.environ.get(key):
                    config[cls.__name__][name] = os.environ[key]
    return config

os.environ['A'] = 'hi'
os.environ['B'] = 'there'

cfg = load_env_config([A, B])
print(cfg)
a = A(config=cfg)
b = B(config=cfg)
print(a.a, b.b)


        