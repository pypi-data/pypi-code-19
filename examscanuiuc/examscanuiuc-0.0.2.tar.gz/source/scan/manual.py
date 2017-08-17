
import os, sys, json, subprocess
import examscanuiuc

def default_open(file_path):
	if sys.platform.startswith('darwin'):
	    subprocess.call(['open', file_path])
	elif os.name == 'nt':
	    os.startfile(file_path)
	elif os.name == 'posix':
	    subprocess.call(['xdg-open', file_path])

def manual_process_page(page_path, roster):
	print('Processing %s' % os.path.basename(page_path))
	default_open(page_path)
	
	image = examscanuiuc.scan.image_from_pdf(page_path)
	try:
		exam_num, exam_pagenum, page_max = [int(p) for p in examscanuiuc.scan.read_page_id(image).split(b',')]
	except examscanuiuc.scan.CouldNotGetQRCode:
		print('Could not read QR code.')
		exam_num = raw_input('Enter exam number: ')
		if exam_num == '': return False
		page_num = raw_input('Enter page number: ')
		if page_num == '': return False
		max_score = raw_input('Enter max score: ')
		if max_score == '': return False
		exam_num, page_num, max_score = int(exam_num), int(page_num), int(max_score)
	
	if page == 1:
		try:
			uin = examscanuiuc.scan.read_uin(image)
		except examscanuiuc.scan.ScoreReadError:
			uin = raw_input('Enter correct UIN: ')
			if uin == '': return False
		
		matched = roster.match(uin)
		if matched['UIN'] != uin:
			print('Entered UIN: %d matched %d of %s' % (uin, matched['UIN'], dict(matched)))
			ans = raw_input('Enter "Yes" to accept this correction: ')
			if ans != 'Yes': return False
		matched['exam'] = exam_num
		parsed = dict(matched)
		
		with open(os.path.join('tmp', 'uins', 'manual.json'), 'a') as uins:
			uins.write(json.dumps(parsed) + '\n')
	else:
		try:
			score, quality = examscanuiuc.scan.read_tickbox(image)
			if score > page_max: raise ValueError('Tried to award %d on %d point question.' % (score, page_max))
		except examscanuiuc.scan.ScoreReadError:
			score = raw_input('Enter correct score: ')
			if score == '': return False
			score, quality = int(score), 10
		
		assert(0 <= score <= max_score)
		parsed = {'exam': exam_num, 'page': exam_pagenum, 'score': score, 'tickcertainty': quality}
		with open(os.path.join('tmp', 'scores', 'manual.json'), 'a') as scores:
			scores.write(json.dumps(parsed) + '\n')
	
	this_exam_dir = os.path.join('tmp', 'exams', str(exam_num))
	if not os.path.exists(this_exam_dir): os.makedirs(this_exam_dir)
	subprocess.call(['cp', file_path, os.path.join(this_exam_dir, str(page_num) + '.pdf')])
	subprocess.call(['mv', file_path, os.path.join('tmp', 'manual')])
	return True

