from configfactory.utils import settings_val

BASE_ENVIRONMENT = settings_val('BASE_ENVIRONMENT', 'base')

ENVIRONMENTS = settings_val('ENVIRONMENTS', [{
    'name': 'Development',
    'alias': 'development'
}])
