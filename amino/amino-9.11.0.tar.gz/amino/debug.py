import sys
import inspect
import logging
from types import ModuleType
from importlib.machinery import SourceFileLoader, SOURCE_SUFFIXES, FileFinder

from enforce import runtime_validation


class Loader(SourceFileLoader):

    def exec_module(self, module: ModuleType) -> None:
        super().exec_module(module)
        if module.__package__ and module.__package__.startswith('amino'):
            for clsname, cls in inspect.getmembers(module, inspect.isclass):
                for funname, fun in list((k, v) for k, v in cls.__dict__.items() if inspect.isfunction(v)):
                    try:
                        module.__dict__[funname] = runtime_validation(fun)
                    except Exception as e:
                        logging.debug(f'failed to apply runtime validation on {fun}: {e}')


def hook() -> None:
    loader_details = (Loader, SOURCE_SUFFIXES)
    sys.path_hooks.insert(0, FileFinder.path_hook(loader_details))  # type: ignore

__all__ = ('hook',)
