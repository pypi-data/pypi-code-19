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
    sleep_time_str = args.get('sec', '0')
    time.sleep(int(sleep_time_str))
    return create_result()


def create_result():
    return 'Done' + '!' * random.randint(1, 10)
