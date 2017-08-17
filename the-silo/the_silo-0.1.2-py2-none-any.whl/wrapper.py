import importlib


def exec_script(module, func):
    mod = importlib.import_module('the_silo.scripts.{0}'.format(module))
    func = getattr(mod, func)
    func()


def create_gizmo(gizmo_name):
    import nuke
    nuke.createNode(gizmo_name, inpanel=False)
