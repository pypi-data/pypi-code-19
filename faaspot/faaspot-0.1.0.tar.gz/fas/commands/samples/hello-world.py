#########
# This ia a sample for a function-as-a-service, provided by FaaSpot.
#


def main(args, context):
    """
    :param args: dictionary of function arguments
    :param context: dictionary of environment variables
    """
    name = args['name']
    return 'Hello {0}'.format(name)
