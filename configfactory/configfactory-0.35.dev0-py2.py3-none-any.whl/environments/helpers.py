from configfactory.environments import settings


def get_environment_alias(environment=None):
    if environment is None:
        return settings.BASE_ENVIRONMENT
    return environment
