"""

Transformer for filtering unchanged files.

Copyright (C) 2017 The Pylp Authors.
This file is under the MIT License.

"""

import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pylp
from pylp.lib.dest import get_path, FileWriter
from pylp.lib.runner import TaskEndTransformer



# Get the file 'mtime' (or -1 if the file doesn't exist)
def get_stat_mtime(file):
	if not os.path.isfile(file):
		return -1
	return os.stat(file).st_mtime



# Filter unchanged files
class changed(pylp.Transformer):

	# Constructor
	def __init__(self, dest = None):
		super().__init__()

		self.dest = dest
		self.enabled = True

		self.exe = ThreadPoolExecutor()
		self.loop = asyncio.get_event_loop()


	# Wait for the destination stream
	async def wait_for_dest(self):
		stream = self.stream

		while True:
			if not stream.next:
				await stream.onpiped
			stream = stream.next

			if isinstance(stream.transformer, TaskEndTransformer):
				self.enabled = False
			elif isinstance(stream.transformer, FileWriter):
				self.dest = stream.transformer.dest

			if self.dest or not self.enabled:
				return


	# Function called when a file need to be transformed
	async def transform(self, file):
		# If no destination was provided: search the destination stream
		if not self.dest and self.enabled:
			await self.wait_for_dest()

		# If the filter is disabled
		if not self.enabled:
			return file

		# Get the real path of the file
		src = file.relpath
		if not src:
			return file

		# Get the destination path of the file
		dest = get_path(self.dest, file)

		# Get the mtime of the source and destination file
		src_future = self.loop.run_in_executor(self.exe, get_stat_mtime, src)
		dest_future = self.loop.run_in_executor(self.exe, get_stat_mtime, dest)

		await asyncio.wait([ src_future, dest_future ])

		src_mtime = src_future.result()
		dest_mtime = dest_future.result()

		# Test if the source changed more recently than the destination
		if dest_mtime == -1 or src_mtime > dest_mtime:
			return file
