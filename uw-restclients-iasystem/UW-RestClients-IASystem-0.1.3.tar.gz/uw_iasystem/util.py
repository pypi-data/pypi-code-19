from restclients_core.util.decorators import use_mock
from dao import IASystem_UW_DAO, IASystem_UWB_DAO, IASystem_UWT_DAO

fdao_ias_override = use_mock(IASystem_UW_DAO(), IASystem_UWB_DAO(),
                             IASystem_UWT_DAO())
