import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configfactory.settings")
    from django.core.management import execute_from_command_line
    sys.argv.insert(1, 'run')
    execute_from_command_line(sys.argv)
