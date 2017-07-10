import os

this_dir = os.path.dirname(os.path.realpath(__file__))

# Get the cli version from VERSION file
version_file = open(os.path.join(this_dir, 'VERSION'))
VERSION = version_file.read().strip()
version_file.close()
