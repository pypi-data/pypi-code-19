import exception as excep
import advice as a
from colorama import init
init()

class Colors:
	PASS = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'

class Smileys:
	HAPPY = ":)"
	SAD = ":("
	CONFUSED = ":S"
	
def display(advice):
	if advice == None:
		return

	color, smiley = _selectColorAndSmiley(advice)
	print("{}{} {}{}".format(color, smiley, advice.message, Colors.ENDC))
	if advice.annotation:
		print("  -{}".format(advice.annotation))

def _selectColorAndSmiley(advice):
	if advice.adviceLevel == a.AdviceLevel.GOOD:
		return Colors.PASS, Smileys.HAPPY
	if advice.adviceLevel == a.AdviceLevel.MIXED or advice.adviceLevel == a.AdviceLevel.UNSURE:
		return Colors.WARNING, Smileys.CONFUSED
	return Colors.FAIL, Smileys.SAD

def displayError(message):
	print("{}{} {}{}".format(Colors.WARNING, Smileys.CONFUSED, message, Colors.ENDC))