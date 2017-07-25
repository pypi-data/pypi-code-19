import logging
from ding0.tools import logger
from ding0.tools.test_logging2 import say_iam_here

logger = logger.setup_logger()

logger.info('asd')
logger.warning('ASD')

say_iam_here()