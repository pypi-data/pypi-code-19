import advice as a
import lib
import statemachine as sm

ADVICEMESSAGE = "consistent indentation"

_indentationLevel = 0
_indentationStep = ""

def advice():
	source = lib.removeComments(lib.source(_fileName))
	setIndentationStep(getIndentationStep(source))

	defaultState = sm.State("default", lambda line : "inconsistent indentation at: {}".format(line.strip()))
	mustMatchIndentation = sm.State(u"must match indentation", lambda line : chr(192) + "inconsistent indentation at: {}".format(line.strip()))
	backslash = sm.State("backslash", lambda line : "unexpected error occured at: {}".format(line.strip()))

	defaultState.addTransition(\
		mustMatchIndentation,\
		lambda line : endsWithDoubleDot(line) and matchesIndentationLevelOrLess(line),\
		action = lambda line : setIndentationLevel(line) and incrementIndentationLevel())
	defaultState.addTransition(\
		backslash,\
		lambda line : endsWithBackslash(line) and matchesIndentationLevelOrLess(line))
	defaultState.addTransition(\
		defaultState,\
		matchesIndentationLevelOrLess,\
		action = setIndentationLevel)

	mustMatchIndentation.addTransition(\
		mustMatchIndentation,\
		lambda line : endsWithDoubleDot(line) and matchesIndentationLevel(line),\
		action = lambda line : incrementIndentationLevel())
	mustMatchIndentation.addTransition(\
		backslash,\
		lambda line : endsWithBackslash(line) and matchesIndentationLevel(line))
	mustMatchIndentation.addTransition(\
		defaultState,\
		lambda line : matchesIndentationLevel(line),\
		action = setIndentationLevel)

	backslash.addTransition(\
		mustMatchIndentation,\
		endsWithDoubleDot,\
		action = lambda line : incrementIndentationLevel())
	backslash.addTransition(\
		backslash,\
		endsWithBackslash)
	backslash.addTransition(\
		defaultState,\
		lambda line : True)

	success, message = sm.StateMachine(defaultState).run((line for line in source.split("\n") if len(line.strip()) != 0))
	if success:
		return a.Advice(a.AdviceLevel.GOOD, ADVICEMESSAGE)
	return a.Advice(a.AdviceLevel.BAD, ADVICEMESSAGE, message)

def getIndentationStep(source):
	nextLineIndented = False
	for line in source.split("\n"):
		if nextLineIndented:
			indentationStep = ""
			for char in line:
				if char == " " or char == "\t":
					indentationStep += char
				else:
					return indentationStep

		if line.strip().endswith(":"):
			nextLineIndented = True
	return ""

def endsWithBackslash(line):
	return line.strip().endswith("\\")

def endsWithDoubleDot(line):
	return line.strip().endswith(":")

def matchesIndentationLevel(line):
	return getIndentationLevel(line) == _indentationLevel

def matchesIndentationLevelOrLess(line):
	return getIndentationLevel(line) <= _indentationLevel

def ifMatchesThenSetIndentationLevel(line):
	if matchesIndentationLevel(line):
		return setIndentationLevel(line)
	return False

def setIndentationStep(indentationStep):
	global _indentationStep
	_indentationStep = indentationStep
	return True

def setIndentationLevel(line):
	global _indentationLevel
	_indentationLevel = getIndentationLevel(line)
	return True

def incrementIndentationLevel():
	global _indentationLevel
	_indentationLevel += 1
	return True

def getIndentationLevel(line):
	if _indentationStep == "":
		return 0

	indentationLevel = 0
	while line.startswith(_indentationStep):
		indentationLevel += 1
		line = line[len(_indentationStep):]
	return indentationLevel