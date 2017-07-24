from collections import deque
from inspect import isclass, signature
from pathlib import Path, PurePosixPath


class NoDefault(object):
	__slots__ = []
	
	def __repr__(self):
		return "<no default>"

nodefault = NoDefault()  # Sentinel value.


def ipeek(d):
	"""Iterate through a deque, popping elements from the left after they have been seen."""
	
	last = None
	
	# We eat trailing slashes.  No sir, can't say we like 'em.
	while d and d[-1] == '':
		d.pop()
	
	while d:
		yield last, d[0]
		last = d.popleft()


def prepare_path(path):
	"""Construct a dispatch-usable path from a string, Path instance, or other iterable."""
	
	if isinstance(path, str):
		path = PurePosixPath(path)
	
	if isinstance(path, PurePosixPath):
		path = deque(path.parts[1 if path.root else 0:])
	else:
		path = deque(path)
	
	return path


def opts(obj):
	"""Retrieve or attempt to calculate the valid HTTP methods for the given object."""
	
	if isclass(obj):
		if '__call__' in dir(obj):
			obj = obj.__call__
		else:
			return
	
	if '__options__' in dir(obj):
		return obj.__options__
	
	if callable(obj):
		sig = signature(obj)
		
		if len(sig.parameters) > 1:
			return {'GET', 'POST'}
