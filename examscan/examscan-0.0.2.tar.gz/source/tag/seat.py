
import re
import random

random.seed(7)  # Make RNG repeatable.

class Seat(object):
	def __init__(self, name, priority):
		self.name = name
		self.priority = priority

class ExamSeat(object):
	def __init__(self, name, exam_num, order_num):
		self.name = name
		self.exam_num = exam_num
		self.order_num = order_num
	def __iter__(self):
		return iter([self.name, self.exam_num])
	def __str__(self):
		return '%d: %s (%d)' % (self.exam_num, self.name, self.order_num)
	def __repr__(self):
		return str(self)

def is_seat(cell):
	return cell.value is not None and re.sub('\\s', '', str(cell.value))  # Must be a string that isn't just whitespace.

def is_broken(cell):
	return cell.font.b or cell.font.i or cell.fill.fgColor.rgb != '00000000'

def shorten(name):
	return name.replace('Left', '(L)').replace('Right', '(R)').replace('Center', '(C)')

def even_sample(population, k):
	gaps = k + 1
	min_block_size = len(population) // gaps
	larger = set(random.sample(range(gaps), len(population) % gaps))
	blocks = [min_block_size + (1 if i in larger else 0) for i in range(gaps)]
	
	sample = []
	j = 0
	for i in range(k):
		j += blocks[i]
		sample.append(population[j])
	assert(j + blocks[-1] == len(population))
	
	return sample

class Room(object):
	def __init__(self, name, seats):
		self.name = name
		self.seats = seats
	@classmethod
	def from_sheet(self, name, sheet):
		data = [[str(cell.value) if is_seat(cell) and not is_broken(cell) else '' for cell in row] for row in sheet.rows]
		layout = [[cell for cell in row if '>' not in cell and '<' not in cell] for row in data]
		priorities = [[min(abs(i - index) for i in range(len(row)) if (i < index and '>' in row[i]) or (index < i and '<' in row[i])) for index, cell in enumerate(row) if '>' not in cell and '<' not in cell] for row in data]
		seats = [[Seat(cell, priority) for cell, priority in zip(row1, row2)] for row1, row2 in zip(layout, priorities)]
		return Room(name, seats)
	def __str__(self):
		return self.name + '\n' + '-' * 50 + '\n' + '\n'.join(','.join('%4s' % shorten(seat.name) for seat in row) for row in self.seats) + '\n' + '=' * 50
	def __repr__(self):
		return str(self)
	def __iter__(self):
		return iter(self.all_seats())
	def __len__(self):
		return len(self.all_seats())
	def seat_indices(self):
		return [(i, j) for i in range(len(self.seats)) for j in range(len(self.seats[i])) if self.seats[i][j].name]
	def all_seats(self):
		return [seat for row in self.seats for seat in row if seat.name]
	def random(self, size=None):
		if size is None: size = len(self)
		return random.sample(self.all_seats(), size)  # all_seats in a random order.
	def by_priority(self):
		return sorted(self, key=lambda s: s.priority, reverse=True)
	def random_by_priority(self, size=None):
		if size is None: size = len(self)
		return sorted(self.random(size), key=lambda s: s.priority, reverse=True)
	def subroom(self, size):
		sample = set(even_sample(self.seat_indices(), size))
		subseats = [[Seat(self.seats[i][j].name if (i, j) in sample else '', priority=self.seats[i][j].priority) for j in range(len(self.seats[i]))] for i in range(len(self.seats))]
		return Room(self.name, subseats)
	def exam_seats(self, start):
		order_num = dict((seat, index) for index, seat in enumerate(self))
		return [ExamSeat('%s (%s)' % (seat.name, self.name), index, order_num[seat]) for index, seat in enumerate(self.random_by_priority(), start=start)]

