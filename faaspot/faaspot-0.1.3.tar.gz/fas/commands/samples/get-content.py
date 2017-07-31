#########
# This ia a sample for a function-as-a-service, provided by FaaSpot.
#
import sh


def main(args, context):
    """
    This function doesn't require any input argument.
    The returned value is the public ip of the vm.

    :param args: dictionary of function arguments
    :param context: dictionary of environment variables
    """
    response = {'content': sh.curl(args.get('url'))}
    return response
