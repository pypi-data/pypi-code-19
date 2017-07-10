import os

this_dir = os.path.dirname(os.path.realpath(__file__))

# Get the cli command from COMMAND file
command_file = open(os.path.join(this_dir, 'COMMAND'))
CMD = command_file.read().strip()
command_file.close()
