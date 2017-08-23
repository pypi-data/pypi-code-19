import stevedore
import logging


def _callback(manager, entrypoint, exception):
    """Log errors in loading extensions as warnings"""
    logging.warning("Failed to load '{}' due to {}".format(entrypoint, exception))
    return


class IngesterManager:
    """Load ingest extensions and invoke them on demand"""

    def __init__(self):
        self.extension_manager = stevedore.extension.ExtensionManager(
            namespace='citrine.dice.converter',
            invoke_on_load=False,
            on_load_failure_callback=_callback
        )

    def run_extension(self, name, path, args):
        """Run extension by name on path with arguments"""
        if name in self.extension_manager:
            extension = self.extension_manager[name]
            pifs = extension.plugin.convert([path], **args)
            return pifs
        else:
            logging.error("{} is an unknown format\nAvailable formats: {}".format(name, self.extension_manager.names()))
            exit(1)
