"""Utilities for getting usage/help"""

import chewrap
import chewrap.arguments


def get_program_info():
    """Get information about the program (version, description)."""

    return "\033[1;4mCheWrap version {}\033[0m\n{}\n".format(
                                                       chewrap.__version__,
                                                       chewrap.__doc__.strip())


def get_usage():
    """Get the program's usage as a string."""

    usage = """\033[1;4mUsage:\033[0m che "<CHE-COMMANDS>" [OPTIONS]

<CHE-COMMANDS> should be whatever commands you want to send to the Che CLI. So,
if you would normally enter:

  $ docker run . . . eclipse/che start --pull

The syntax with CheWrap would instead be:

  $ che "start --pull" . . .

This applies to anything that comes after the image name, since that is
interpreted by the Che CLI, not Docker. To control things like bind mounts and
environment variables, which are set by Docker, options must be used.

"""

    return "\n".join([get_program_info(), usage])


def get_help():
    """Get the program's full help as a string."""

    help = [get_usage(), """\033[1;4mOptions:\033[0m
Options alter how Docker creates the container. Although these options are
limited, you can use `--docker-opts` to pass arbitrary arguments to Docker.

"""]

    args = chewrap.arguments.get_arguments()
    args['--help'] = {
        'type': 'store_true',
        'shorthand': '-h',
        'help': 'Show this help message'
    }

    for key in sorted(args, key=chewrap.arguments.sort_args_key):
        arg = args[key]

        if arg['type'] == 'positional':
            continue

        help.append('\033[1m')

        if 'shorthand' in arg:
            help.append('{}, '.format(arg['shorthand']))

        help.append(key)

        if 'metavar' in arg:
            help.append(' {}\033[0m:\n    {}\n'.format(arg['metavar'],
                                                       arg['help']))
        else:
            help.append('\033[0m:\n    {}\n'.format(arg['help']))

    return ''.join(help)
