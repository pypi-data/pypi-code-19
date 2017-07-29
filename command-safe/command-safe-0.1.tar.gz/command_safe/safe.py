import click
import pickle
from subprocess import call

class Safe:
	update = False

	def __init__(self, safe_file):
		self.safe_file = safe_file

	def load(self):
		try:
			with open(self.safe_file, 'rb') as input:
				try:
					self.safe = pickle.load(input)
				except EOFError:
					self.safe = {}
		except IOError:
			self.safe = {}

	def save(self):
		with open(self.safe_file, 'wb') as output:
			pickle.dump(self.safe, output, 2)

	def clear(self):
		self.safe = {}
		self.update = True

	def delete(self, alias):
		if alias in self.safe:
			del self.safe[alias]
		self.update = True

	def get_command(self, alias):
		if alias in self.safe:
			return self.safe[alias]
		else:
			return None

	def set_command(self, alias, command):
		self.safe[alias] = command
		self.update = True

	def execute(self, alias):
		call(self.safe[alias], shell=True)

	def show(self):
		table = [('alias:', 'command:')]
		for key, value in self.safe.items():
			table.append((key, value))
		column_size = [max(map(len, column)) for column in zip(*table)]
		format_string = ' | '.join(["{{:<{}}}".format(i) for i in column_size])
		table.insert(1, ['-' * i for i in column_size])
		for row in table:
			click.echo('{}'.format(format_string.format(*row)))
