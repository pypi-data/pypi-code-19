
import sys

from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch, cm
import qrcode

from examscanuiuc.tag.pdf import images_from_pdf

def parse_file(file_path):
	with open(file_path) as config_input:
		contents = config_input.readlines()
	
	spares = 5
	start = 1
	request = []
	for line in contents:
		line = line.strip()
		if '#' in line: line = line[:line.find('#')]
		if line.startswith('scores:'):
			_, y = line.split(':')
			y = y.replace(' ', '')
			scores = [int(i) for i in y.split(',')]
		elif line.startswith('spares:'):
			_, y = line.split(':')
			spares = int(y)
		elif line.startswith('start:'):
			_, y = line.split(':')
			start = int(y)
		elif line != '':
			x, y, z = line.split(':')
			request.append((x.strip(), y.strip(), int(z)))
	
	return scores, request, spares, start

def overlay(exam_images, max_scores, exam_seats, output_file, code=None, paper_type=letter):
	can = Canvas(output_file, pagesize=paper_type)
	paper_width, paper_height = paper_type
	
	exam_images = [[ImageReader(image) for image in exam] for exam in exam_images]
	
	for xxx, exam_seat in enumerate(exam_seats):
		sys.stdout.write('\rCompiling: %d / %d' % (xxx+1, len(exam_seats)))
		sys.stdout.flush()
		for index, max_score in enumerate(max_scores):
			page_code = 0 if code is None else code[xxx * len(max_scores) + index]
			bg = exam_images[page_code][index]
			can.drawImage(bg, 0*cm, 0*cm, width=paper_width, height=paper_height)
			
			# Draw QR codes.
			qr = ImageReader(qrcode.make('%d, %d, %d' % (exam_seat.exam_num, index+1, max_score), box_size=1).get_image())
			
			can.drawImage(qr, 0.75*cm, 0.75*cm, width=1.5*cm, height=1.5*cm)
			can.drawImage(qr, 19.34*cm, 0.75*cm, width=1.5*cm, height=1.5*cm)
			
			can.setFont('Times-Roman', 10)
			can.drawCentredString(1.5*cm, 0.6*cm, 'Ex %d' % exam_seat.exam_num)
			can.drawCentredString(20.09*cm, 0.6*cm, 'Ex %d' % exam_seat.exam_num)
			can.drawCentredString(3.4*cm, 0.6*cm, 'Page score')
			
			if index == 0:
				# Write seat name.
				if exam_seat.name:
					can.setFont('Times-Bold', 22)
					can.drawString(11.4*cm, 26.60*cm, 'Seat:')
					
					can.setFont('Times-Roman', 22)
					can.drawString(13.3*cm, 26.60*cm, exam_seat.name)
				
				# Draw UIN box.
				# US letter is 21.58cm x 27.93cm
				box_l, box_t = 11.79*cm, 23.825*cm
				box_w, box_h = 8*cm, 10*cm
				num_digits = 9
				
				can.rect(box_l, box_t - box_h, box_w, box_h)
				can.line(box_l, box_t - 1.4*cm, box_l + box_w, box_t - 1.4*cm)
				xstep = box_w / (num_digits + 1)
				ystep = box_h / (10 + 1)
				for i in range(num_digits-1):
					can.line(box_l + 1.5*xstep + i*xstep, box_t - 1.4*cm, box_l + 1.5*xstep + i*xstep, box_t - 1.4*cm + 0.32*cm)
				can.setFont('Times-Bold', 12)
				can.drawString(box_l+0.2*cm, box_t - 0.52*cm, 'Write and bubble in your UIN:')
				can.setFont('Times-Roman', 10)
				for i in range(num_digits):
					for j in range(10):
						can.circle(box_l + 1.0*xstep + i*xstep, box_t - 1.4*cm - 0.6*cm - 0.8*j*cm, 0.3*cm)
						can.drawCentredString(box_l + 1.0*xstep + i*xstep, box_t - 1.4*cm - 0.12*cm - 0.6*cm - 0.8*j*cm, str(j))
			
			# Draw score box.
			can.setLineWidth(1.5)
			can.line(0*cm, 2.3*cm, 21.59*cm, 2.3*cm)
			can.line(2.3*cm, 0*cm, 2.3*cm, 2.3*cm)
			can.line(4.5*cm, 0*cm, 4.5*cm, 2.3*cm)
			can.line(19.0*cm, 0*cm, 19.0*cm, 2.3*cm)
			can.line(4.5*cm, 0.7*cm, 19.0*cm, 0.7*cm)
			
			if max_score > 0:
				can.setLineWidth(0.5)
				for x in range(max_score+1):
					can.rect(5.05*cm + 1.3*x*cm, 1.3*cm, 0.4*cm, 0.4*cm)
				can.setFont('Times-Roman', 10)
				for x in range(max_score+1):
					can.drawCentredString(5.25*cm + 1.3*x*cm, 1.375*cm, str(x))
				
				can.setDash(2, 3)
				for x in range(max_score+1):
					can.rect(4.85*cm + 1.3*x*cm, 1.1*cm, 0.8*cm,0.8*cm)
			
			can.showPage()
	
	can.save()
	sys.stdout.write('\n')
	sys.stdout.flush()

def main(exams, max_scores, exam_seats, output_file):
	exam_images = [images_from_pdf(exam) for exam in exams]
	num_pages = len(exam_images[0])
	
	overlay(exam_images, max_scores, exam_seats, output_file, code=None)

