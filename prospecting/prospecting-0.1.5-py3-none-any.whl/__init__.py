from prospecting.version import __version__
from prospecting.api import GoogleApi, SheetsApi
from prospecting.api_wip import DriveApi, AnalyticsApi, SearchConsoleApi
from prospecting import utils
from prospecting.env import (PROJECTNAME,
                             PROJECTDIR,
                             CREDSDIR,
                             CERTSDIR,
                             CLIENT_SECRET_FILE,
                             DATADIR,
                             SOURCE_FILE,
                             SOURCE_CSV
                             )


import logging.config
logging.config.dictConfig(utils.log_config_dict)
