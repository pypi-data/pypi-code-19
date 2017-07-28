import sys
import printer
import advice as a
import os.path
import pkgutil
import importlib

def main():
	if len(sys.argv) != 2:
		printer.displayError("Wrong number of arguments provided to design, usage: design <pyfile>")
		return
		
	fileName = sys.argv[1] if sys.argv[1].endswith(".py") else sys.argv[1] + ".py"

	for _, name, _ in pkgutil.iter_modules([os.path.dirname(__file__)  + "/advisors"]):
		module = importlib.import_module("advisors.%s" %name)
		module._fileName = fileName
		printer.display(module.advice())

main()