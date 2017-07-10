from stuffer.configuration import config
from .core import Action


class StoreAction(Action):
    @staticmethod
    def store_dir():
        return config.store_directory

    def create_store_dir(self):
        if not self.store_dir().is_dir():
            self.store_dir().mkdir(parents=True)

    @staticmethod
    def key_path(key):
        return StoreAction.store_dir().joinpath(key)


class Set(StoreAction):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        super().__init__()

    def run(self):
        self.create_store_dir()
        with self.key_path(self.key).open('w') as f:
            f.write(self.value)


def get(key):
    if StoreAction.key_path(key).exists():
        with StoreAction.key_path(key).open('r') as f:
            return f.read()
