import os
import importlib


def load_module_from_file(module_path: str):
    module_name: str = os.path.basename(module_path.replace('.py', ''))
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
