from configfactory.utils import settings_val

CONFIG_BACKEND = settings_val('CONFIG_BACKEND', {
    'class': 'configfactory.configmanager.backends.memory.'
})
