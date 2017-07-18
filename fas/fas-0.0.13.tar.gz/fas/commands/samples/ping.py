#########
# This ia a sample for a function-as-a-service, provided by FaaSpot.
#

import time
import random


def main(args, context):
    """
    :param args: dictionary of function arguments
    :param context: dictionary of environment variables
    """
    if 'sec' in args:
        time.sleep(int(args['sec']))
    return 'PIN' + 'G' * random.randint(1, 10)
