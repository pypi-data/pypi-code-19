import importlib
import os
import types

import astroid


pylint_extra_modules = os.environ.get('PYLINT_EXTRA_MODULES', '').split(',')


def transform(mod):
    if mod.name in pylint_extra_modules:
        module = importlib.import_module(mod.name)

        for name, obj in vars(module).copy().items():
            if name in mod.locals:
                continue
            elif isinstance(obj, types.ModuleType):
                ast_node = [astroid.MANAGER.ast_from_module(obj)]
            elif isinstance(obj, types.ClassType):
                ast_node = [astroid.Class(name, None)]
            elif not hasattr(obj, '__module__') or not hasattr(obj, '__name__'):
                ast_node = [astroid.Const(name, None)]
            else:
                if hasattr(astroid.MANAGER, 'extension_package_whitelist'):
                    astroid.MANAGER.extension_package_whitelist.add(
                        obj.__module__)
                real_mod = astroid.MANAGER.ast_from_module_name(obj.__module__)
                ast_node = real_mod.getattr(obj.__name__)
                for node in ast_node:
                    fix_linenos(node)

            mod.locals[name] = ast_node

def fix_linenos(node):
    if node.fromlineno is None:
        node.fromlineno = 0
    for child in node.get_children():
        fix_linenos(child)


def register(linter):
    astroid.MANAGER.register_transform(astroid.Module, transform)
