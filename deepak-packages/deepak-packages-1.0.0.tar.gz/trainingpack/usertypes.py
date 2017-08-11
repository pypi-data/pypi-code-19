# Raising exceptions and errors

from user_exceptions import InvalidAgeException, InvalidNameException

class Person(object):
	def __init__(self):
		pass

	@property
	def name(self):
		return self.__name
	@name.setter
	def name(self, name):
		if type(name) is not str:
			raise InvalidNameException()
		self.__name = name

	@property
	def age(self):
		return self.__age
	@age.setter
	def age(self, age):
		if type(age) is not int:
			# raise TypeError("Only integer is expected")
			raise InvalidAgeException("Only integer is expected")
		if 0 < age <=120:
			self.__age = age
		else:
			# raise ValueError("Age must be 1 and 120")
			raise InvalidAgeException()
			raise 

	def __str__(self):
		return "{} is {} years old".format(self.__name, self.__age)


def main():
	p1 = Person()
	p1.name = "Granit Xhaka"
	p1.age = "126"
	print(p1)


if __name__ == '__main__':
	main()