from __future__ import division
import advice as a
import lib
import ast

ADVICEMESSAGE = "possibly too short names"

def advice():
	try:
		root = ast.parse(lib.source(_fileName))
	except:
		return

	names = {node.id for node in ast.walk(root) if isinstance(node, ast.Name)}
	names -= set(name for name in __builtins__)
	names -= set(["x", "y", "i", "j", "k"])
	names = sorted(names)

	shortNames = [name for name in names if len(name) <= 2]

	if shortNames:
		return a.Advice(a.AdviceLevel.UNSURE, ADVICEMESSAGE + ": {}".format(shortNames))