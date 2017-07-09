import logging
import logging.handlers
import os

def setup_logger(name):
    logger = logging.getLogger(name)
    if not os.path.exists('logs'):
        os.mkdir('logs')
    ch = logging.StreamHandler()
    ch.setLevel(logging.CRITICAL)
    fh = logging.handlers.TimedRotatingFileHandler(
        'logs/args.log', when='M', interval=10)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    # File handlers log level is always DEBUG
    # Console handler depends on -v arg
    fh.setLevel(logging.DEBUG)

#def set_console_handler_log_level(args):
#    if not args.verbose:
#        ch.setLevel(logging.ERROR)
#    elif args.verbose == 1:
#        ch.setLevel(logging.WARNING)
#    elif args.verbose == 2:
#        ch.setLevel(logging.INFO)
#    elif args.verbose >= 3:
#        ch.setLevel(logging.DEBUG)
#    else:
#        pass