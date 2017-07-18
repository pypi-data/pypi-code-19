from datetime import timedelta

from dj_core.config import Config as BaseConfig


class Config(BaseConfig):
    defaults_dict = BaseConfig.defaults_dict.copy()
    defaults_dict.simple.update({
        'DJCORE_ACCOUNT_AUTHENTICATION_METHOD': 'email',
        'DJCORE_ACCOUNT_EMAIL_REQUIRED': True,
        'DJCORE_ACCOUNT_EMAIL_VERIFICATION': 'none',
        'DJCORE_ACCOUNT_USER_MODEL_USERNAME_FIELD': None,
        'DJCORE_ACCOUNT_USERNAME_REQUIRED': False,
        'DJCORE_ACCOUNT_REGISTRATION': 'enabled',
        'DJCORE_REST_USE_JWT': True,
        'DJCORE_SWAGGER_SETTINGS': {'api_version': '1'},
        'DJCORE_JWT_AUTH': {
            'JWT_EXPIRATION_DELTA': timedelta(hours=24),
            'JWT_AUTH_HEADER_PREFIX': 'Token',
        }
    })

    def get_installed_apps(self, settings):
        return super(Config, self).get_installed_apps(settings) + [
            'dj_core_drf',
            'rest_framework',
            'rest_framework.authtoken',
            'rest_framework_swagger',
            'rest_auth',
            'allauth',
            'allauth.account',
            'rest_auth.registration',
            'revproxy',
            'django_filters',
        ]

    def get_drf_settings(self, settings):  # pylint: disable=unused-argument,no-self-use
        return {
            'DEFAULT_PERMISSION_CLASSES': [
                'rest_framework.permissions.IsAuthenticatedOrReadOnly'
            ],
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
                'rest_framework.authentication.BasicAuthentication',
                'rest_framework.authentication.SessionAuthentication',
            ],
            'DEFAULT_PAGINATION_CLASS': 'dj_core_drf.pagination.ThousandMaxLimitOffsetPagination',
            'DEFAULT_FILTER_BACKENDS': [
                'rest_framework_filters.backends.DjangoFilterBackend',
            ],
            'DEFAULT_METADATA_CLASS': 'dj_core_drf.metadata.ModelChoicesMetadata',
        }

    def get_rest_auth_serializers(self, settings):  # pylint: disable=unused-argument,no-self-use
        return {
            'USER_DETAILS_SERIALIZER': 'dj_core_drf.serializers.UserDetailsSerializer',
            'PASSWORD_RESET_SERIALIZER': 'dj_core_drf.serializers.PasswordResetSerializer',
            'LOGIN_SERIALIZER': 'dj_core_drf.serializers.LoginSerializer',
        }

    def get_settings(self):
        settings = super(Config, self).get_settings()
        settings.REST_FRAMEWORK = self.get_drf_settings(settings)
        settings.REST_AUTH_SERIALIZERS = self.get_rest_auth_serializers(settings)
        return settings
