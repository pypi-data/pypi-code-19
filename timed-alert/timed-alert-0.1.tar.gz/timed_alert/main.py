import click
import time
import sys

@click.command()
@click.option('--verbose', '-v', is_flag = True, help = 'Verbose output.')
@click.argument('minutes', default = '')
def tal(verbose, minutes):
	if verbose:
		click.echo('INFO: Starting alert at {} minute intervals'.format(minutes))
	try:
		minutes = float(minutes)
		while 1:
			time.sleep(60 * minutes)
			for _ in range(3):
				time.sleep(0.3)
				sys.stdout.write('\a')
				sys.stdout.flush()
	except ValueError:
		click.echo('Error: Invalid "minutes" argument. Please enter a number greater than 0')
