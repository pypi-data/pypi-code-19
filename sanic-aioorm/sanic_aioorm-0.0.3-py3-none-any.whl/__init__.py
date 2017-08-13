__all__=['AioModel','AioOrm']

from .core import Core
from .set_config_mixin import SetConfigMixin
from .regist_mixin import RegistMixin
from .aiomodel import Model as AioModel

class AioOrm(Core,SetConfigMixin,RegistMixin):
    pass
