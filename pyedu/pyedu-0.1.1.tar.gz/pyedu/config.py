import os
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
from dateutil.parser import parse
from datetime import datetime as dt

# define the base Path
APPBASEDIR = os.path.abspath(os.path.dirname(__file__))


class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

# define Configurations
class BaseConfig:
    DEFAULT_KEYFILE = os.path.join(APPBASEDIR, '../enc/remote.key')
    DEFAULT_ENCFILE = os.path.join(APPBASEDIR, '../enc/remote.enc')
    SECRET_KEY = 'please change me'

    @ClassProperty
    @classmethod
    def _SECRET_KEY(cls):
        return Random.new().read(64).hex()

    @staticmethod
    def init_app(app):
        pass


class DevLocalConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////%s/development.db' % APPBASEDIR
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    EXPLAIN_TEMPLATE_LOADING = True


class ProductionConfig(BaseConfig):
    @ClassProperty
    @classmethod
    def SQLALCHEMY_DATABASE_URI(cls):
        keyfile = get_key_file(cls)

        if not os.path.exists(keyfile):
            print('No .key file found for remote.enc')
            return 'sqlite:////%s/pyedu.db' % APPBASEDIR

        encfile = get_enc_file(cls)
        if not os.path.exists(encfile):
            raise RuntimeError('The encrypted database connection was not found: %s' % encfile)

        # open the key-file
        with open(keyfile, 'rb') as f:
            key = f.read()

        # read the connection
        with open(encfile, 'rb') as enc:
            iv = enc.read(AES.block_size)
            aes = AES.new(key, AES.MODE_CFB, iv)
            ftext = aes.decrypt(enc.read())

            try:
                valid, pwcheck, conn = ftext.split(b'\n')

                # validity datum
                if parse(valid.decode()) < dt.now():
                    print('Your key is expired.')
                    return 'sqlite:////%s/pyedu.db' % APPBASEDIR

                # passphrase is only there when it was correct
                assert SHA256.new(pwcheck).digest() == key

                # no error occured, return the connection
                print('Found key, using remote connection...')
                return conn.decode()

            except (IndexError, AssertionError, Exception):
                print('Your .key file is corrupted (Maybe the passphrase changed?).')
                return 'sqlite:////%s/pyedu.db' % APPBASEDIR


class DevProductionConfig(ProductionConfig):
    DEBUG = True
    EXPLAIN_TEMPLATE_LOADING = True

def get_enc_file(cls):
    if os.environ.get('PYEDU_ENCFILE') is not None:
        return os.environ.get('PYEDU_ENCFILE')
    elif hasattr(cls, 'ENCFILE'):
        return cls.ENCFILE
    else:
        return cls.DEFAULT_ENCFILE

def get_key_file(cls):
    if os.environ.get('PYEDU_KEYFILE') is not None:
        return os.environ.get('PYEDU_KEYFILE')
    elif hasattr(cls, 'KEYFILE'):
        return cls.KEYFILE
    else:
        return cls.DEFAULT_KEYFILE


# configuration registry
config = dict(
    local_dev=DevLocalConfig,
    production=ProductionConfig,
    production_dev=DevProductionConfig,
    default=ProductionConfig
)