import logging

import click

def _enable_verbose(ctx, opts, verbose):
  if verbose:
    logging.basicConfig(level=logging.DEBUG)


verbose_flag = click.option('--verbose', '-v', is_flag=True, callback=_enable_verbose, expose_value=False, is_eager=True)

sort_flag = click.option('--sort-created',
                         type=click.Choice(['asc', 'des']),
                         help='Sort by created date')
