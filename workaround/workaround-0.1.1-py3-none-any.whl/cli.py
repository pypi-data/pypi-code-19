"""
workaround.

Usage:
    workaround <locations>...
    workaround --examples
"""
from pathlib import Path

import colorama
from docopt import docopt
from termcolor import colored

from workaround.handle import (
    get_examples,
    handle_files,
)


def run():
    colorama.init()

    options = docopt(__doc__)

    if options['--examples']:
        for name, examples in get_examples():
            print(name + ':')
            for adverb, (value, adj) in examples:
                print('   - {adverb} {value} is {adj}'.format(
                    adverb=adverb,
                    value=colored(value, 'red'),
                    adj=colored(adj, 'green')
                ))
            print('')

        return

    paths = [Path(p) for p in options['<locations>']]

    for workaround, status in handle_files(paths):
        print('{0} in file {1} line {2}: {3}. Status is: {4}'.format(
            colored('Error', 'red'),
            colored(workaround.path, 'green'),
            workaround.line,
            colored(workaround.statement, 'yellow'),
            colored(status, 'green')
        ))
        context_pre, message, context_post = workaround.split_context()
        context = context_pre + colored(message, 'red') + context_post
        print(context.strip() + '\n')


if __name__ == '__main__':
    run()
