
'''
Scanned pages are upside-down PDFs.
'''

import glob, os, subprocess, tempfile
from PyPDF2 import PdfFileReader, PdfFileWriter

class PDFPages:
	''' Break a PDF file into single pages. '''
	def __init__(self, file_path, directory=None):
		self.directory = tempfile.mkdtemp() if directory is None else directory
		
		with open(file_path, 'rb') as input_file:
			input_pdf = PdfFileReader(input_file)
			num_pages = input_pdf.numPages
			
			for index in range(num_pages):
				page = input_pdf.getPage(index)
				page.rotateClockwise(180)
				
				output_pdf = PdfFileWriter()
				output_pdf.addPage(page)
				with open(os.path.join(self.directory, 'pg_%010d.pdf' % (index + 1)), 'wb') as output_file:
					output_pdf.write(output_file)
		
		self.page_files = [os.path.join(self.directory, 'pg_%010d.pdf' % (index + 1)) for index in range(num_pages)]
	def __getitem__(self, index):
		return self.page_files[index]
	def __len__(self):
		return len(self.page_files)
	def __iter__(self):
		return iter(self.page_files)
	def __del__(self):
		import shutil  # Can't assume imports in __del__.
		shutil.rmtree(self.directory)

