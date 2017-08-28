from django.conf import settings as django_settings


class Settings:
    SETTINGS = {
        # Tags to use for navigation
        'NAV_ELEMENTS': 'h2',
        # XML parser to use, see
        # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#specifying-the-parser-to-use
        # for more info. `None` means automatic detection.
        'XML_PARSER': None,
        'SET_ATTRS': {},
        'NAV_ELEMENTS_CLASS': 'local-navigation-item',
    }

    def __getattr__(self, name):
        """
        Return the setting `name` prefixed in the Django settings by
        CMS_LOCAL_NAVIGATION, or return `default` if it's not defined. So if
        your setting is named `NAV_ELEMENTS`, it will either return the value
        of the setting named `CMS_LOCAL_NAVIGATION_NAV_ELEMENTS`, or the value
        of the `default` argument if the setting is not set.
        """
        setting_key = 'CMS_LOCAL_NAVIGATION_' + name

        return (
            getattr(django_settings, setting_key)
            if hasattr(django_settings, setting_key)
            else self.SETTINGS[name]
        )


settings = Settings()
