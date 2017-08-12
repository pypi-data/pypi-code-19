import os
import sys
import subprocess
import pkg_resources
from yadi import binary

def main():
    target = pkg_resources.resource_filename('yadi', os.path.join('vendor', binary.dest()))
    args = [target] + sys.argv[1:]
    code = subprocess.call(args)
    sys.exit(code)
