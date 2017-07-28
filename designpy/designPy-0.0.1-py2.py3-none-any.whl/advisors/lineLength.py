import advice as a
import lib

MAXLINELENGTH = 80
ADVICEMESSAGE = "all lines contain max {} characters".format(MAXLINELENGTH)


def advice():
	source = lib.source(_fileName)
	if any(len(line) > MAXLINELENGTH for line in source.split("\n")):
		return a.Advice(a.AdviceLevel.BAD, ADVICEMESSAGE)
	return a.Advice(a.AdviceLevel.GOOD, ADVICEMESSAGE)