import logging
import os

import babel

from . import yaml

log = logging.getLogger(__name__)


class Locale:
    """
    Locale instance
    """

    version = 1

    def __init__(self, path, meta, strings, consts):
        # For minimizing IO operations
        self._changed = False

        # Data
        self._path = path
        self._strings = strings
        self._consts = consts
        self._meta, others = self._check_meta(meta)

        # Move all trash from Meta to consts
        if others:
            self._consts.update(others)
            self._set_changed()

        # Trigger update locale from Meta
        self.locale = True

        # Save changes
        self.save()

    @property
    def locale(self) -> babel.Locale:
        if not hasattr(self, '_locale'):
            sep = '-' if '-' in self.language_code else '_'
            locale = babel.Locale.parse(self.language_code, sep=sep)
            setattr(self, '_locale', locale)
        return getattr(self, '_locale')

    @property
    def language_code(self):
        if not hasattr(self, '_language_code'):
            file_name = os.path.split(self._path)[-1]
            language_code, _, _ = file_name.partition('.')
            setattr(self, '_language_code', language_code)
        return getattr(self, '_language_code')

    @locale.setter
    def locale(self, value):
        """
        Trigger update locale from Meta info
        :param value: 
        :return: 
        """
        code = self._meta['language']
        if self._meta['territory']:
            code += '_' + self._meta['territory']
        locale = babel.Locale.parse(code)
        setattr(self, '_locale', locale)

    def _set_changed(self, value=True):
        self._changed = value

    def _check_meta(self, original_meta):
        """
        Check Meta info

        :param original_meta: 
        :return: 
        """

        def pop(key, default):
            result = original_meta.pop(key, None)
            if result is None:
                self._set_changed()
            return result or default

        meta = {
            'version': pop('version', self.version),
            'language': pop('language', self.locale.language),
            'territory': pop('territory', self.locale.territory),
            'language_name': pop('language_name', self.locale.language_name),
            'english_name': pop('english_name', self.locale.english_name),
            'authors': pop('authors', []),
        }

        if meta['version'] != self.version:
            raise RuntimeError('Bad locale version!')
        return meta, original_meta

    @classmethod
    def from_file(cls, path):
        """
        Load dictionary from file

        :param path: 
        :return: 
        """
        log.debug(f"Load file '{path}'")
        with open(path, 'r') as file:
            data = yaml.load(file)
        if not data:
            data = {}
        meta = data.pop('meta', {})
        strings = data.pop('strings', {})
        consts = data.pop('consts', {})

        return Locale(path, meta, strings, consts)

    @classmethod
    def new_locale(cls, path):
        return Locale(path, {}, {}, {})

    def save(self, force=False):
        """
        Save dictionary

        :param force: 
        :return: 
        """
        if not self._changed and not force:
            return False
        data = {
            'meta': {k: v for k, v in self._meta.items() if not k.startswith('$')},
            'consts': self._consts,
            'strings': {k: v if v else k for k, v in sorted(self._strings.items(), key=lambda item: item[0])}
        }

        if not data['consts']:
            data.pop('consts')
        log.debug(f"Save file '{self._path}'")
        with open(self._path, 'w') as file:
            yaml.dump(data, file)
        self._set_changed(False)
        return True

    def update(self):
        """
        Check changes from disk

        :return: 
        """
        temp = Locale.from_file(self._path)
        log.debug(f"Start updating '{self._path}'")
        with self as merge:
            for key, value in temp:
                merge(key, value)
        del temp
        return self

    def get_text(self, text):
        """
        Get text from dictionary

        :param text: 
        :return: 
        """
        result = self[text]
        if isinstance(result, yaml.TranslateObject):
            result = result.get_text(self)
        if result is None:
            self[text] = text
            return text
        return result

    def get_meta(self):
        """
        Get Meta info
        :return: 
        """
        return self._meta.copy()

    def get_consts(self):
        """
        Get consts

        :return: 
        """
        return self._consts.copy()

    def __getitem__(self, item):
        """
        Get translate for item

        :param item: 
        :return: 
        """
        if item not in self._strings:
            self[item] = item
        return self._strings[item]

    def __setitem__(self, key, value):
        """
        Update translate for item

        :param key: 
        :param value: 
        :return: 
        """
        if self._strings.get(key) != value:
            log.info(f"Update '{key}' from {self.language_code}")
            self._strings[key] = value
            self._set_changed()
        self.save()

    def __iter__(self):
        """
        Iter all strings
        :return: tuple(key, translate)
        """
        yield from self._strings.items()

    def __enter__(self):
        """
        Start merging

        :return: 
        """
        self.start_merge()
        return self.merge

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()

    def start_merge(self):
        return self._strings.keys()

    def merge(self, key, value=None):
        """
        Insert or remove records

        :param key: 
        :param value: 
        :return: 
        """
        if key not in self._strings:
            self._strings[key] = value or key
            log.info(f"^merge. Insert '{key}' into {self.language_code}")
            self._set_changed()
        elif isinstance(value, DeleteItem):
            del self._strings[key]
            log.info(f"^merge. Delete '{key}' from {self.language_code}")


class DeleteItem:
    pass
