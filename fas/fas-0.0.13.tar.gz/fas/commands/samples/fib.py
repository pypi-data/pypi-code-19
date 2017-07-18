#########
# This ia a sample for a function-as-a-service, provided by FaaSpot.
#


def main(args, context):
    """
    :param args: dictionary of function arguments
    :param context: dictionary of environment variables
    """
    return fib(int(args['num']))


def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)
