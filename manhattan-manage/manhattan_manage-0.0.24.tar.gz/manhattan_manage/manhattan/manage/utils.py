"""
A set of classes and functions that help manage applications.
"""

from importlib import import_module

__all__ = ['load_blueprints']


def load_blueprints(app, app_name, blueprints):
    """
    Import and register a list of blueprints and return a map of the modules
    imported.
    """

    blueprint_modules = {}
    for blueprint in blueprints:
        # Import the blueprint module
        blueprint_module = import_module(
            'blueprints.{0}.{1}'.format(blueprint, app_name)
            )
        blueprint_modules[blueprint] = blueprint_module

        # Register the blueprint
        app.register_blueprint(blueprint_module.blueprint)

    return blueprint_modules
