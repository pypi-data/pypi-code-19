from collections import OrderedDict
from operator import itemgetter
from pathlib import PurePosixPath


class Crumb(tuple):
	"""A representation of dispatch descent progress or endpoint enumeration."""
	
	__slots__ = ()
	_fields = ('dispatcher', 'origin', 'path', 'endpoint', 'handler', 'options')
	
	Path = PurePosixPath
	
	dispatcher = property(itemgetter(0), doc="The dispatcher instance that generated this event.")
	origin = property(itemgetter(1), doc="The dispatch root object.")
	path = property(itemgetter(2), doc="The path element or sequence represented by this crumb.")
	endpoint = property(itemgetter(3), doc="A boolean indicating if this is an endpoint or midpoint in dispatch.")
	handler = property(itemgetter(4), doc="The associated handler for the path; may be `None` in some circumstances.")
	options = property(itemgetter(5), doc="A set of valid HTTP verbs for this endpoint, if applicable.")
	
	def __new__(cls, dispatcher, origin, path=None, endpoint=False, handler=None, options=None):
		"""Construct a new Crumb instance."""
		
		return tuple.__new__(cls, (
				dispatcher,
				origin,
				cls.Path(path) if path else None,
				endpoint,
				handler,
				frozenset(options) if options else None,
			))
	
	@classmethod
	def _make(cls, iterable, new=tuple.__new__, len=len):
		"""Construct a Crumb from a sequence or iterable."""
		
		result = new(cls, iterable)
		
		if 3 < len(result) < 7:
			raise TypeError('Expected 4-6 arguments, got %d' % len(result))
		
		return result
	
	def __json__(self):
		"""Return a new OrderedDict which maps field names to their values."""
		
		return OrderedDict(zip(self._fields, self))
	
	as_dict = as_json = property(__json__)
	
	def replace(self, **kw):
		"""Return a new Crumb replacing specified fields with new values."""
		
		result = self._make(map(kw.pop, self._fields, self))
		
		if kw:
			raise ValueError('Got unexpected field names: ' + str(list(kw)))
		
		return result
	
	def __repr__(self):
		"""An attractive representation for the Crumb instance."""
		
		parts = [(f + '=' + repr(v)) for f, v in zip(self._fields, self) if v is not None]
		return self.__class__.__name__ + '(' + ', '.join(parts) + ')'
	
	def __getnewargs__(self):
		"""Return self as a plain tuple; as used by copy and pickle."""
		
		return tuple(self)
