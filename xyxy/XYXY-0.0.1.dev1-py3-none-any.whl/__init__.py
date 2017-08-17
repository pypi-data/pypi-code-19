from . import _dataset
from . import _db
from . import _helpers


def load(dataset_title):
    return _dataset.Dataset(dataset_title)


def connect(uri=None):
    return _db.connect(uri)


def clear():
    _helpers.clear()


__all__ = [load, connect, clear]
