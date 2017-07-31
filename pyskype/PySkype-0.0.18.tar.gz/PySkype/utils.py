import logging
import os

# --- --- --- --- --- --- --- --- ---
#   Logger config
# --- --- --- --- --- --- --- --- ---
# create _logger
_logger = logging.getLogger('Skype_API')
_logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
current_dir = os.path.dirname(os.path.abspath(__file__))
fh = logging.FileHandler('{}/{}.log'.format(current_dir, 'Skype_API'))
fh.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s %(name)s.%(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the _logger
_logger.addHandler(fh)
_logger.addHandler(ch)
