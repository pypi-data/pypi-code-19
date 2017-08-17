
import shutil
import os, json, glob
from multiprocessing import Pool
import pandas as pd
import numpy as np
try:
	from itertools import imap
except ImportError:  # Python 3.
	imap = map

from examscan.scan import Roster, PDFPages, image_from_pdf, read_page_id, read_uin, read_tickbox
from examscan.scan import ScoreReadError, CouldNotGetQRCode
import examscan.tmp

import examscan.scan.report

DATA, ERROR = 'Data', 'Error'

def process_page(file_name, page_num, page_path, roster):
	state = DATA
	image = image_from_pdf(page_path)
	try:
		exam_num, exam_page_num, page_max = [int(p) for p in read_page_id(image).split(b',')]
		page_info = (exam_num, exam_page_num, file_name, page_num)
		message = ''
		if exam_page_num == 1:
			uin = read_uin(image)
			matched = roster.match(uin)
			if matched['UIN'] != uin:
				message = 'Warning on page %d: UIN fudged %d -> %d' % (page_num, uin, matched['UIN'])
			parsed = [
				{'exam': exam_num, 'data_type': 'name', 'data': matched['name']},
				{'exam': exam_num, 'data_type': 'netid', 'data': matched['netid']},
				{'exam': exam_num, 'data_type': 'UIN', 'data': matched['UIN']}
				]
		else:
			score, quality = read_tickbox(image)
			if score > page_max: raise ValueError('Tried to award %d on %d point question.' % (score, page_max))
			parsed = [{'exam': exam_num, 'data_type': 'score %d' % exam_page_num, 'data': score}]
		
	except (CouldNotGetQRCode, ScoreReadError, ValueError) as error:
		state = ERROR
		parsed = None
		error_str = error if isinstance(error, str) else error.args[0]
		message = 'Error on page %d of %s: ' % (page_num, file_name) + error_str
		shutil.copy(page_path, os.path.join(examscan.tmp.DIR, '%s_%d.pdf.error' % (file_name, page_num)))
	
	return state, parsed, message, page_info

def helper(data):
	return process_page(*data)

def process_file(file_path, roster, reprocess=False, cores=1):
	file_name = os.path.basename(file_path)
	if os.path.exists(os.path.join(examscan.tmp.DIR, 'data', '%s.csv' % file_name)) and not reprocess:
		print('Skipping as already finished: ' + file_name)
		return
	
	print('Starting processing of: ' + file_name)
	
	with PDFPages(file_path) as pages:  # Split the PDF
		todo = [(file_name, index, page_file_path, roster) for index, page_file_path in enumerate(pages, start=1)]
		
		if cores == 1:
			results = imap(helper, todo)
		else:  # cores > 1.
			pool = Pool(processes=cores)
			results = pool.map(helper, to_do)
			pool.close()
		
		error_count = 0
		lines = []
		page_infos = []
		for state, parsed, message, page_info in results:
			if state == ERROR:
				error_count += 1
			else:  # state == DATA
				for line in parsed:
					print(line)
					lines.append(line)
				page_infos.append(page_info)
			
			if message:
				print('   ' + message)
	
	pd.DataFrame(lines)[['exam', 'data_type', 'data']].to_csv(os.path.splitext(file_path)[0] + '.data', index=False)
	pd.DataFrame(page_infos, columns=['exam', 'exam_page', 'file_name', 'page']).to_csv(os.path.splitext(file_path)[0] + '.info', index=False)
	
	print('Processed %d pages with %d errors\n' % (len(todo), error_count))

def load_data():
	df = pd.concat([pd.read_csv(file_path) for file_path in glob.glob(examscan.tmp.DIR + '/*.data')], ignore_index=True)
	
	if not df.empty:
		df = df.drop_duplicates()
		df = df.pivot(index='exam', columns='data_type', values='data')
		
		score_columns = [column for column in df.columns if column.startswith('score')]
		df['total'] = df[score_columns].sum(axis=1).astype(int)
		df.loc[df[score_columns].isnull().any(axis=1), 'total'] = np.nan
	
	return df

def load_info():
	df = pd.concat([pd.read_csv(file_path) for file_path in glob.glob(examscan.tmp.DIR + '/*.info')], ignore_index=True)
	
	return {(row.exam, row.exam_page): (row.file_name, row.page) for _, row in df.iterrows()}

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Extract tagged exams')
	parser.add_argument('files', nargs='*', type=str, default='', help='files to process')
	parser.add_argument('--roster', required=True, type=str, help='roster file')
	parser.add_argument('--reprocess', action='store_true', help='reprocess files that have already been completed')
	parser.add_argument('--results', type=str, default='results.csv', help='results output file')
	parser.add_argument('--template', type=str, help='report template to use')
	parser.add_argument('--reports', type=str, default='reports', help='report output directory')
	parser.add_argument('--cores', type=int, default=1, help='number of cores to use')
	args = parser.parse_args()
	
	roster = Roster.from_file(args.roster)
	
	DB = examscan.tmp.ScanDatabase()
	
	for file_path in args.files:
		file_path = DB.add(file_path)
		process_file(file_path, roster, reprocess=args.reprocess, cores=args.cores)
	
	results = load_data()
	page_info = load_info()
	unmatched = roster.roster[-roster.roster.UIN.isin(results.UIN)]  # The students we don't have anything for.
	
	print('Progress:')
	for column in sorted(results.columns, key=str):
		missing = results[column].isnull()
		print('\t%s: Have %s, missing %s' % (column, sum(-missing), sum(missing)))
	
	num_incomplete = len(results[results.isnull().any(axis=1)])
	print('%d exams with complete information.' % (len(results) - num_incomplete))
	print('%d exams with incomplete information.' % num_incomplete)
	print('%d students in roster without an exam assigned.' % len(unmatched))
	
	if num_incomplete:
		print('\tProcess more files and/or deal with any errors to begin report generation.')
		exit(0)
	
	print('Saving results to "%s".' % args.results)
	results.to_csv(args.results, index=False)
	
	if args.template is not None:
		print('Generating report:')
		examscan.scan.report.main(results, args.template, args.reports)
	else:
		print('\tRerun with --template to generate student reports.')

