import advice as a
import lib
import re
import string

ADVICEMESSAGE = "missing whitespace around operator"

def advice():
	source = lib.replaceStringsWithX(lib.replaceCommentsWithHashes(lib.source(_fileName)))
	
	unaryOperators = ["**", "!"]
	binaryOperators = sorted(["/", "//", "%", "|", "&", "=", "+=", "-=", "*=", "/=", "//=", "%=", "==", "!=", "<", ">", "<=", ">="], key = lambda x : -len(x))
	undecidedOperators = ["+", "-", "*"]
	operators = sorted(binaryOperators + unaryOperators + undecidedOperators, key = lambda x : -len(x))

	operatorRegex = "[" + "|".join("'{}'".format("".join("\\" + c for c in op)) for op in operators) + "]"

	UNARY_TOKEN = "`~UNARYOP"
	BINARY_TOKEN = "`~BINARYOP"
	UNDECIDED_TOKEN = "`~UNDECIDEDOP"

	operatorLines = re.findall(".*{}.*".format(operatorRegex), source)

	for line in operatorLines:
		tempLine = replaceOperatorsWith(line, binaryOperators, BINARY_TOKEN)
		tempLine = replaceOperatorsWith(tempLine, unaryOperators, UNARY_TOKEN)
		tempLine = replaceOperatorsWith(tempLine, undecidedOperators, UNDECIDED_TOKEN)

		if re.findall(".*[^ ]{}.*".format(BINARY_TOKEN), tempLine) or re.findall(".*{}[^ ].*".format(BINARY_TOKEN), tempLine):
			return a.Advice(a.AdviceLevel.BAD, ADVICEMESSAGE, annotation = line)
		#elif re.findall(".*[^ ]{}.*".format(UNDECIDED_TOKEN), tempLine) or re.findall(".*{}[^ ].*".format(UNDECIDED_TOKEN), tempLine):
		#	pass

def replaceOperatorsWith(line, operators, token):
	for op in operators:
		line = re.sub("{}".format("".join("\\" + c for c in op)), token, line)
	return line