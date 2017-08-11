# Creating Execptions
"""
This and every file with .py is known as a Module
A module may comprise: Variables, functions, classes or some executable code
Variables, functions and classes from this module can be used in other modules
"""

class InvalidAgeException(Exception):

	def __init__(self, message="Invalid Age. Must be a number between 1 and 120"):
		self.__message = message

	def __str__(self):
		return self.__message

class InvalidNameException(Exception):

	def __init__(self, message="Invalid Name. Must be a string"):
		self.__message = message

	def __str__(self):
		return self.__message


if __name__ == '__main__':
	main()