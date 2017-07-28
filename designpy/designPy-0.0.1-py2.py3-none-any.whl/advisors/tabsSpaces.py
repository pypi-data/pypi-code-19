import advice as a
import lib

ADVICEMESSAGE = "exclusively using tabs or spaces for indentation"

def advice():
	source = lib.source(_fileName)
	usesSpaces = False
	usesTabs = False
	for line in source.split("\n"):
		for char in line:
			if char == " ":
				usesSpaces = True
			elif char == "\t":
				usesTabs = True
			else:
				break
		if usesSpaces and usesTabs:
			return a.Advice(a.AdviceLevel.BAD, ADVICEMESSAGE)

	return a.Advice(a.AdviceLevel.GOOD, ADVICEMESSAGE)