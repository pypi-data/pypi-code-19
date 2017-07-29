import click
from command_safe.safe import Safe
from command_safe.config import *

@click.command()
@click.option('--verbose', '-v', is_flag = True, help = 'Verbose output.')
@click.option('--show', '-s', is_flag = True, help = 'Show saved commands.')
@click.option('--clear', is_flag = True, help = 'Clear all saved commands.')
@click.option('--delete', '-d', help = 'Delete the command saved to the specified alias.')
@click.argument('alias', default = '')
@click.argument('command', default = '')
def csa(verbose, show, clear, delete, alias, command):

	# Load safe
	if verbose:
		click.echo('INFO: Loading safe')
	safe = Safe(safe_file)
	safe.load()

	# Clear safe
	if clear:
		if verbose:
			click.echo('INFO: Clearing safe')
		safe.clear()

	# Delete alias
	if delete:
		if verbose:
			click.echo('INFO: Deleting alias "{}"'.format(delete))
		safe.delete(delete)

	# Save command
	if command and not clear:
		if not alias:
			click.echo('ERROR: Alias cannot be blank')
			return
		if verbose:
			click.echo('INFO: Saving command "{}" to alias "{}"'.format(command, alias))
		safe.set_command(alias, command)

	# Print safe
	if show:
		if verbose:
			click.echo('INFO: Printing safe')
		safe.show()

	# Execute command
	if alias and not command and not clear:
		command = safe.get_command(alias)
		if command:
			if verbose:
				click.echo('INFO: Executing command "{}" specified by alias "{}"\n'.format(safe.get_command(alias), alias))
			safe.execute(alias)
		else:
			click.echo('Error: The alias "{}" does not exist'.format(alias))
			return

	# Save safe
	if safe.update:
		if verbose:
			click.echo('INFO: Saving safe')
		safe.save()
