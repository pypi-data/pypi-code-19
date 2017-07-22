# -*- coding: utf-8 -*-
import os
import base64
from cryptography.fernet import Fernet
import pkg_resources

__all__ = ['Manager']


class Manager(object):
    def __init__(self, app_name):
        self.__app_name = app_name
        self.__app_folder = os.path.join(os.path.expanduser(path="~"), '.' + app_name)
        self.__fernet_file = pkg_resources.resource_filename('geocode_lite', '.fernet.key')

    def is_key_installed(self, key_name):
        if not os.path.exists(self.__app_folder):
            return False

        return os.path.exists(path=self._get_key_path(key_name))

    def install_key(self, key_name, api_key):
        if not os.path.exists(self.__fernet_file):
            key = Fernet.generate_key()
            self._store_key(key, self.__fernet_file)

        fernet = self._get_fernet()
        encrypted_api_key = fernet.encrypt(api_key.encode())

        if not os.path.exists(self.__app_folder):
            os.mkdir(self.__app_folder, mode=0o755)

        self._store_key(encrypted_api_key, self._get_key_path(key_name=key_name))

    def remove_key(self, key_name):
        if not os.path.exists(self._get_key_path(key_name)):
            return

        os.remove(self._get_key_path(key_name))

        if not os.listdir(self.__app_folder):
            os.rmdir(self.__app_folder)

    def get_key(self, key_name):
        if not self.is_key_installed(key_name):
            return None

        fernet = self._get_fernet()
        if fernet is None:
            return None

        api_key = self._load_key(self._get_key_path(key_name))
        return fernet.decrypt(api_key).decode()

    def _get_key_path(self, key_name):
        return os.path.join(self.__app_folder, key_name + '.key')

    def _get_fernet(self):
        try:
            fernet_key = self._load_key(self.__fernet_file)
        except Exception:
            return None

        return Fernet(fernet_key)

    @staticmethod
    def _store_key(key, path):
        with open(path, 'wb') as fd:
            fd.write(base64.b64encode(key))

    @staticmethod
    def _load_key(path):
        with open(path, 'rb') as fd:
            key = fd.readline()
            return base64.b64decode(key)


if __name__ == '__main__':
    print("api_key_manager.py")
