__version__ = "1.0.2"

from osxNC import *
import subprocess, os

# Check if terminal-notifier is installed
proc = subprocess.Popen(["which", "terminal-notifier"], stdout=subprocess.PIPE)
env_bin_path = proc.communicate()[0].strip()

if not os.path.exists(env_bin_path):
	raise Exception("Dependency terminal-notifier is not installed. Download it at github.com/julienXX/terminal-notifier")