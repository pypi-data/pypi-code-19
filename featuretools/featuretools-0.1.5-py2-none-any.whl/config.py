import logging
import os
import sys
import yaml

dirname = os.path.dirname(__file__)
default_path = os.path.join(dirname, 'config_yaml.py')
ft_config_path = os.path.join(os.path.expanduser('~'), '.featuretools', 'config_yaml.py')


def ensure_config_file(destination=ft_config_path):
    if not os.path.exists(destination):
        import shutil
        if not os.path.exists(os.path.dirname(destination)):
            try:
                os.mkdir(os.path.dirname(destination))
            except OSError:
                pass
        shutil.copy(default_path, destination)


def load_config_file(path=ft_config_path):
    if not os.path.exists(path):
        path = default_path
    with open(path) as f:
        text = f.read()
        config_dict = yaml.load(text)
        return config_dict


ensure_config_file()
config = load_config_file()


def initialize_logging(config):
    loggers = config.get('logging', {})
    loggers.setdefault('featuretools', 'info')

    fmt = '%(asctime)-15s %(name)s - %(levelname)s    %(message)s'
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(fmt))

    for name, level in loggers.items():
        LEVEL = logging._levelNames[level.upper()]
        logger = logging.getLogger(name)
        logger.setLevel(LEVEL)
        for _handler in logger.handlers:
            logger.removeHandler(_handler)

        logger.addHandler(handler)
        logger.propagate = False


initialize_logging(config)
