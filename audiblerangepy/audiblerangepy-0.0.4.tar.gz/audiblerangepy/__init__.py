class Base:
	def __init__(self):
		pass

	def audible_range(self, hz):
		if hz > self.lowest and hz < self.highest:
			return True
		else:
			return False

class Human(Base):
	def __init__(self):
		self.lowest = 31
		self.highest = 19000

class Tuna(Base):
	def __init__(self):
		self.lowest = 50
		self.highest = 1100

class Chiken(Base):
	def __init__(self):
		self.lowest = 125
		self.highest = 2000

class Goldfish(Base):
	def __init__(self):
		self.lowest = 20
		self.highest = 3000

class Bullfrog(Base):
	def __init__(self):
		self.lowest = 100
		self.highest = 3000

class Catfish(Base):
	def __init__(self):
		self.lowest = 50
		self.highest = 4000

class Treefrog(Base):
	def __init__(self):
		self.lowest = 50
		self.highest = 4000

class Canary(Base):
	def __init__(self):
		self.lowest = 250
		self.highest = 8000

class Cockatiel(Base):
	def __init__(self):
		self.lowest = 250
		self.highest = 8000

class Parakeet(Base):
	def __init__(self):
		self.lowest = 200
		self.highest = 8500

class Elephant(Base):
	def __init__(self):
		self.lowest = 17
		self.highest = 10500

class Owl(Base):
	def __init__(self):
		self.lowest = 200
		self.highest = 12000

class Chinchilla(Base):
	def __init__(self):
		self.lowest = 52
		self.highest = 33000

class Horse(Base):
	def __init__(self):
		self.lowest = 55
		self.highest = 33500

class Cow(Base):
	def __init__(self):
		self.lowest = 23
		self.highest = 35000

class Racoon(Base):
	def __init__(self):
		self.lowest = 100
		self.highest = 40000

class Sheep(Base):
	def __init__(self):
		self.lowest = 125
		self.highest = 42500

class Dog(Base):
	def __init__(self):
		self.lowest = 64
		self.highest = 44000

class Ferret(Base):
	def __init__(self):
		self.lowest = 16
		self.highest = 44000

class Guineapig(Base):
	def __init__(self):
		self.lowest = 47
		self.highest = 49000

class Rabbit(Base):
	def __init__(self):
		self.lowest = 96
		self.highest = 49000

class Sealion(Base):
	def __init__(self):
		self.lowest = 200
		self.highest = 50000

class Gerbil(Base):
	def __init__(self):
		self.lowest = 56
		self.highest = 60000

class Opossim(Base):
	def __init__(self):
		self.lowest = 500
		self.highest = 64000

class Albinorat(Base):
	def __init__(self):
		self.lowest = 390
		self.highest = 72000

class Hoodedrat(Base):
	def __init__(self):
		self.lowest = 530
		self.highest = 75000

class Cat(Base):
	def __init__(self):
		self.lowest = 55
		self.highest = 77000

class Mouse(Base):
	def __init__(self):
		self.lowest = 900
		self.highest = 79000

class Bat(Base):
	def __init__(self):
		self.lowest = 103000
		self.highest = 115000

class Belugawhale(Base):
	def __init__(self):
		self.lowest = 1000
		self.highest = 123000

class Dolphin(Base):
	def __init__(self):
		self.lowest = 150
		self.highest = 150000

class Porpoise(Base):
	def __init__(self):
		self.lowest = 75
		self.highest = 150000
