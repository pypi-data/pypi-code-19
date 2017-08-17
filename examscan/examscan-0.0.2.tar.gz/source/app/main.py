
''' The main window of the exam GUI application. '''

import re
import os
import io
import sys
import pickle
import shutil
from math import sin, cos, pi, ceil, sqrt
from itertools import combinations

import foo.app

try:
	import Tkinter as TK
	import tkFileDialog
	import tkMessageBox
except ImportError:  # Python 3.
	import tkinter as TK
	import tkinter.filedialog as tkFileDialog
	import tkinter.messagebox as tkMessageBox

try:
	import ttk as TTK
except ImportError:  # Python 3.
	from tkinter import ttk as TTK

# Some constants.
if sys.platform in ['darwin']:
	COMMAND = {
		'new': 'Command+N',
		'open': 'Command+O',
		'save': 'Command+S',
		'close': 'Command+W',
		}
	COMMAND_KEY = {
		'new': '<Command-n>',
		'open': '<Command-o>',
		'save': '<Command-s>',
		'close': '<Command-w>',
		}
else:
	COMMAND = {
		'new': 'Ctrl+N',
		'open': 'Ctrl+O',
		'save': 'Ctrl+S',
		'close': 'Ctrl+W',
		}
	COMMAND_KEY = {
		'new': '<Control-n>',
		'open': '<Control-o>',
		'save': '<Control-s>',
		'close': '<Control-w>',
		}

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class Exam(object):
	def __init__(self, parent):
		self.parent = parent
		
		self.parent.bind(COMMAND_KEY['close'], lambda e: self.quit())
		# self.parent.bind('<Delete>', self.delete)
		
		self.notebook = TTK.Notebook(self.parent)
		self.page_generate = TTK.Frame(self.notebook)
		self.page_analyse = TTK.Frame(self.notebook)
		self.page_error = TTK.Frame(self.notebook)
		self.page_reports = TTK.Frame(self.notebook)
		self.page_options = TTK.Frame(self.notebook)
		self.notebook.add(self.page_generate, text='Tag')
		self.notebook.add(self.page_analyse, text='Analyse')
		self.notebook.add(self.page_error, text='Errors')
		self.notebook.add(self.page_reports, text='Reports')
		self.notebook.add(self.page_options, text='Options')
		
		self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
		
		self.parent.protocol('WM_DELETE_WINDOW', self.quit)
		
		### Generate:
		self.gen_exams_tree = TTK.Treeview(self.page_generate)
		self.gen_exams_tree['columns'] = ('path', 'scores')
		self.gen_exams_tree.heading('#0', text='Version', anchor='w')
		self.gen_exams_tree.column('#0', anchor='w', width=100)
		self.gen_exams_tree.heading('path', text='Path')
		self.gen_exams_tree.column('path', anchor='center')
		self.gen_exams_tree.heading('scores', text='Page scores')
		self.gen_exams_tree.column('scores', anchor='center', width=100)
		self.gen_exams_tree.bind('<Double-Button-1>', self.gen_exams_tree_double_left)
		self.exams = []
		self.gen_exams_scroll = TTK.Scrollbar(self.page_generate)
		self.gen_exams_scroll.configure(command=self.gen_exams_tree.yview)
		self.gen_exams_tree.configure(yscrollcommand=self.gen_exams_scroll.set)
		
		self.gen_rooms_tree = TTK.Treeview(self.page_generate)
		self.gen_rooms_tree['columns'] = ('seats', 'density')
		self.gen_rooms_tree.heading('#0', text='Room', anchor='w')
		self.gen_rooms_tree.column('#0', anchor='w', width=100)
		self.gen_rooms_tree.heading('seats', text='Seats')
		self.gen_rooms_tree.column('seats', anchor='center', width=100)
		self.gen_rooms_tree.heading('density', text='Density')
		self.gen_rooms_tree.column('density', anchor='center', width=100)
		for room in sorted(ROOMS):
			self.gen_rooms_tree.insert('', 'end', text=room, values=('0', FULL))
		self.gen_rooms_tree.bind('<Double-Button-1>', self.gen_rooms_tree_double_left)
		self.gen_rooms_scroll = TTK.Scrollbar(self.page_generate)
		self.gen_rooms_scroll.configure(command=self.gen_rooms_tree.yview)
		self.gen_rooms_tree.configure(yscrollcommand=self.gen_rooms_scroll.set)
		
		self.gen_build_button = TK.Button(self.page_generate, text='Generate', command=self.gen_build_button_click)
		
		self.gen_exams_tree.grid(row=0, column=0, columnspan=3, sticky='nesw')
		self.gen_exams_scroll.grid(row=0, column=4, sticky='ns')
		self.gen_rooms_tree.grid(row=1, column=0, columnspan=3, sticky='nesw')
		self.gen_rooms_scroll.grid(row=1, column=4, sticky='ns')
		self.gen_build_button.grid(row=2, column=2, sticky='e')
		
		self.page_generate.grid_rowconfigure(0, pad=10, weight=1)
		self.page_generate.grid_rowconfigure(1, pad=10, weight=1)
		self.page_generate.grid_rowconfigure(2, pad=10)
		self.page_generate.grid_columnconfigure(0, pad=100, weight=1)
		self.page_generate.grid_columnconfigure(1, pad=100, weight=1)
		self.page_generate.grid_columnconfigure(2, pad=100, weight=1)
		
		### Analyse:
	
	def quit(self):
		# Apparantly there are some problems with comboboxes, see:
		#  http://stackoverflow.com/questions/15448914/python-tkinter-ttk-combobox-throws-exception-on-quit
		self.parent.eval('::ttk::CancelRepeat')
		self.parent.destroy()
		self.parent.quit()
	
	def show_about(self):
		tkMessageBox.showinfo('About', 'qp (Version %s).\nCopyright (c) Mark Bell 2017.' % qp.__version__)
	
	def gen_exams_tree_double_left(self, event):
		file_path = tkFileDialog.askopenfilename(
			defaultextension='.pdf',
			filetypes=[('portable document format', '.pdf'), ('all files', '.*')],
			title='Open exam file')
		if not file_path: return  # Cancelled.
		
		scores = foo.app.get_input('Page scores', 'Enter page scores as comma separated list', default='')
		if scores is None: return  # Cancelled.
		
		self.exams.append((file_path, scores))
		self.update_exams_tree()
	
	def update_exams_tree(self):
		self.gen_exams_tree.delete(*self.gen_exams_tree.get_children())
		for letter, (file_path, scores) in zip(LETTERS, self.exams):
			truncated_file_path = file_path[:5] + ' ... ' + file_path[-16:]
			self.gen_exams_tree.insert('', 'end', text=letter, values=(truncated_file_path, scores))
	
	def gen_rooms_tree_double_left(self, event):
		region = self.gen_rooms_tree.identify('region', event.x, event.y)
		row = self.gen_rooms_tree.identify_row(event.y)
		column = self.gen_rooms_tree.identify_column(event.x)
		if column == '#1':
			if region == 'cell':
				row_data = self.gen_rooms_tree.item(row)
				num_seats = foo.app.get_input('Page scores', 'Enter number of seats needed', default=row_data['values'][0])
				if num_seats is None: return  # Cancelled.
				
				self.gen_rooms_tree.set(row, column='seats', value=num_seats)
		elif column == '#2':
			if region == 'cell':
				self.gen_rooms_tree.set(row, 'density', SPARSE if self.gen_rooms_tree.set(row, 'density') == FULL else FULL)
			elif region == 'heading':
				if all(self.gen_rooms_tree.set(row, 'density') == FULL for row in self.gen_rooms_tree.get_children()):
					for row in self.gen_rooms_tree.get_children():
						self.gen_rooms_tree.set(row, 'density', SPARSE)
				else:
					for row in self.gen_rooms_tree.get_children():
						self.gen_rooms_tree.set(row, 'density', FULL)
	
	def gen_build_button_click(self):
		pass


def start():
	root = TK.Tk()
	root.title('Exam')
	exam = Exam(root)
	# root.minsize(300, 300)
	# root.geometry('700x500')
	root.wait_visibility(root)
	# Set the icon.
	# Make sure to get the right path if we are in a cx_Freeze compiled executable.
	# See: http://cx-freeze.readthedocs.org/en/latest/faq.html#using-data-files
	datadir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
	icon_path = os.path.join(datadir, 'icon', 'icon.gif')
	img = TK.PhotoImage(file=icon_path)
	try:
		root.tk.call('wm', 'iconphoto', root._w, img)
	except TK.TclError:
		# Give up if we can't set the icon for some reason.
		pass
	root.mainloop()

if __name__ == '__main__':
	start()

