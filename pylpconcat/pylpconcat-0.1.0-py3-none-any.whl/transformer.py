"""

Concatenation transformer.

Copyright (C) 2017 The Pylp Authors.
This file is under the MIT License.

"""

import os
import pylp


class concat(pylp.Transformer):

	# Constructor
	def __init__(self, filename, **options):
		super().__init__()

		self.filename = filename
		self.sep = options.get('sep', '\n')

		self.first_file = None
		self.buffer = ''


	# Function called when a file need to be transformed
	async def transform(self, file):
		# Ignore empty files
		if not file.contents:
			return

		# Store the first file for cloning it
		if not self.first_file:
			self.first_file = file
		
		# Add the contents
		self.buffer += file.contents + self.sep


	# Function called when all files are transformed
	async def flush(self):
		# No files contatenated
		if not self.first_file:
			return

		# Append the result file into the stream
		self.append(pylp.File(
			os.path.join(self.first_file.cwd, self.filename),
			contents = self.buffer,
			cwd = self.first_file.cwd,
			base = self.first_file.base
		))
