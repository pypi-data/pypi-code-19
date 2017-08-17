
import os

from PyPDF2 import PdfFileReader
try:
	from StringIO import StringIO
except ImportError:
	from io import StringIO

from examscanuiuc.tag.generate import main, parse_file
from examscanuiuc.tag.seat import ExamSeat, Room

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Generate tagged exams for printing')
	parser.add_argument('exams', nargs='+', type=str, default='', help='exam files to process')
	parser.add_argument('--output', type=str, default='.', help='output directory')
	parser.add_argument('--num', type=int, help='number of exams required')
	parser.add_argument('--scores', type=str, help='max score for each page')
	parser.add_argument('--start', type=int, help='value to start numbering from')
	parser.add_argument('--rooms', type=str, help='path to room spreadsheet')
	parser.add_argument('--config', type=str, default='', help='use config file')
	args = parser.parse_args()
	
	exams = []
	for exam in args.exams:
		with open(exam, 'rb') as exam_input:
			exams.append(PdfFileReader(StringIO(exam_input.read())))
	
	page_count = exams[0].getNumPages()
	for exam in exams:
		if exam.getNumPages() != page_count:
			raise ValueError('Not all exams have the same number of pages.')
	
	if args.config:
		scores, request, spares, start = parse_file(args.config)
		
		print('Using scoring system: %s' % scores)
		print('Assigning:')
		for room, room_name, num_exams in request:
			print('\t%d seats in %s' % (num_exams, room))
		
		import openpyxl  # Slow import so move it later.
		W = openpyxl.load_workbook(args.rooms)
		
		cumulative = start if args.start is None else args.start
		for room, room_name, num_exams in request:
			exam_room = Room.from_sheet(room_name, W.get_sheet_by_name(room))
			
			exam_seats = exam_room.subroom(num_exams).exam_seats(start=cumulative) + \
				[ExamSeat('Spare %d (%s)' % (i+1, room_name), cumulative + num_exams + i, i) for i in range(spares)]
			
			cumulative += len(exam_seats)
			
			main(args.exams, scores, exam_seats, os.path.join(args.output, '%s.pdf' % room_name))
	else:
		if args.start is None: args.start = 1
		
		if args.num is None:
			raw_num = raw_input('Number of exams needed: ')
			if not raw_num: exit()
		else:
			raw_num = args.num
		try:
			args.num = int(raw_num)
		except ValueError:
			raise ValueError('Couldn\'t parse "%s" as a number of exams' % raw_num)
		
		if args.scores is None:
			raw_scores = raw_input('Enter points available per page as a comma separated list (or blank to cancel).\nExpecting %d page scores.\nUnless you want to award points for completing the cover sheet, this should start with a 0: ' % page_count)
			if not raw_scores: exit()
		else:
			raw_scores = args.scores
		try:
			scores = [int(i) for i in raw_scores.split(',')]
		except ValueError:
			raise ValueError('Couldn\'t parse "%s" as comma separated list of scores' % raw_scores)
		
		if len(scores) != page_count:
			raise ValueError('Expected %d page scores but got %d page scores.' % (page_count, len(scores)))
		if not all(0 <= score <= 10 for score in scores):
			raise ValueError('Scores must be in the range [0, 10].')
		
		print('Using scoring system: %s' % scores)
		exam_seats = [ExamSeat('', exam_num, exam_num) for exam_num in range(args.start, args.start + args.num)]
		
		main(args.exams, scores, exam_seats, os.path.join(args.output, 'output.pdf'))

