from __future__ import division
import advice as a
import lib
import re

ADVICEMESSAGE = "possibly too few comments"

def advice():
	#print lib.source(_fileName)
	source = lib.replaceStringsWithX(lib.replaceCommentsWithHashes(lib.source(_fileName)))
	#print source

	nLines = 0
	nLinesOfComments = 0
	for line in source.split("\n"):
		nLines += 1
		if "#" in line:
			nLinesOfComments += 1

	if nLinesOfComments / nLines < 0.1:
		return a.Advice(a.AdviceLevel.UNSURE, ADVICEMESSAGE)
