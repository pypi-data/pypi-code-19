class StateException(Exception):
	pass

class StateMachine(object):
	def __init__(self, start):
		self._start = start

	def run(self, lineGen):
		state = self._start
		for line in lineGen:
			try:
				state = state.next(line)
			except StateException as e:
				return False, str(e)
		return True, ""

class State(object):
	def __init__(self, name, errorMessageCreator):
		self._name = name
		self._errorMessageCreator = errorMessageCreator
		self._transitions = []

	def addTransition(self, nextState, condition, action = None):
		self._transitions.append((nextState, condition, action))

	def next(self, line):
		for state, condition, action in self._transitions:
			if condition(line):
				if action:
					action(line)
				return state
		raise StateException(self._errorMessageCreator(line))
