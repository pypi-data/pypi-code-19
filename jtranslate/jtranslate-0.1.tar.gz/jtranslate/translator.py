import functools
import glob
import logging
import os

import jinja2

from jtranslate.locale import Locale, DeleteItem

log = logging.getLogger(__name__)

JINJA_LOCALES_KEY = 'LOCALES'
JINJA_LOCALE_KEY = 'LOCALE'
JINJA_TRANSLATOR_KEY = 'TRANSLATOR'
JINJA_GETTEXT_KEY = '_'
JINJA_META_KEY = 'META'


class Translator:
    """
    Base translator object
    """

    def __init__(self, path, default_locale, jinja_env=None):
        if jinja_env is None:
            jinja_env = jinja2.Environment()

        self.path = path
        self.default_locale = default_locale
        self.jinja_env = jinja_env

        self._locales = {}

        if default_locale:
            self.get_locale(default_locale)
        self.jinja_env.globals[JINJA_LOCALES_KEY] = self.locales
        self.jinja_env.globals[JINJA_TRANSLATOR_KEY] = self

        self._used_texts = set()

    @property
    def locales(self):
        """
        Get locales list
        :return: 
        """
        return list(self._locales.keys())

    def load_all(self):
        """
        Scan path and load all locales
        """
        files = glob.glob(os.path.join(self.path, '*.yaml'))
        for file in files:
            _, filename = os.path.split(file)
            language_code, _, __ = filename.partition('.')
            self.get_locale(language_code)
        return self

    def reload_all(self):
        """
        Update all loaded locales
        """
        log.info(f"Reloading locales")
        for locale in self._locales.values():
            locale.update()

    def save_all(self):
        """
        Save all records
        :return: 
        """
        log.info(f"Triggered save all")
        for locale in self._locales.values():
            locale.save(True)

    def get_locale(self, locale_name):
        """
        Get locale from loaded or disk
        :param locale_name: 
        :return: 
        """
        if locale_name is None:
            locale_name = self.default_locale
        if locale_name is None:
            return Locale(None, {}, {}, {})

        path = os.path.join(self.path, locale_name + '.yaml')

        if locale_name in self._locales:
            locale = self._locales[locale_name]
        elif os.path.isfile(path):
            locale = self._locales[locale_name] = Locale.from_file(path)
        else:
            locale = self._locales[locale_name] = Locale.new_locale(path)
        return locale

    def get_text(self, text, locale=None, context=None, formatted=True):
        """
        Get text from dictionary

        :param text: original text
        :param locale: str or Locale
        :param context: dict
        :param formatted: render jinja2 template
        :return: str
        """
        self._used_texts.add(text)

        if not isinstance(locale, Locale):
            locale = self.get_locale(locale)

        # Generate context
        if context is None:
            context = {}
        context[JINJA_META_KEY] = locale.get_meta()
        context[JINJA_GETTEXT_KEY] = functools.partial(self.get_text, locale=locale)
        context[JINJA_LOCALE_KEY] = locale

        # Get text
        result = locale.get_text(text)

        # If need render jinja2 template
        if formatted:
            template: jinja2.Template = self.jinja_env.from_string(result, globals=locale.get_consts())
            # By default in context stored META, LOCALE and get_text as _
            result = template.render(context)
        return result

    def merge(self, save=True, clean=False):
        """
        Merge keys in all loaded dictionaries

        :param save: save on complete 
        :param clean: remove unused keys
        :return: 
        """
        log.info(f"The merger of dictionaries was started...")
        keys = set()
        for locale in self._locales.values():
            for item in locale.start_merge():
                keys.add(item)

        if clean:
            not_used = set(item for item in keys if item not in self._used_texts)
            keys = set(item for item in keys if item not in not_used)
        else:
            not_used = set()

        for locale in self._locales.values():
            for key in keys:
                locale.merge(key)
            if clean:
                for key in not_used:
                    locale.merge(key, DeleteItem())
            if save:
                locale.save()
        log.info(f"The merge of dictionaries is completed.")

    def update_globals(self, *d, **kwargs):
        """
        Update jinja2 environment globals

        :param d: 
        :param kwargs: 
        :return: 
        """
        self.jinja_env.globals.update(*d, **kwargs)

    def __str__(self):
        return '<Translator(' + ', '.join(self.locales) + ')>'

    def __getitem__(self, locale):
        return TranslatorContext(self, locale)

    __call__ = get_text


class TranslatorContext:
    def __init__(self, translator, locale):
        if not isinstance(locale, Locale):
            locale = translator.get_locale(locale)
        self.locale: Locale = locale
        self._translator: Translator = translator

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_text(self, text, context=None, formatted=True):
        return self._translator.get_text(text, self.locale, context, formatted)

    __call__ = get_text
