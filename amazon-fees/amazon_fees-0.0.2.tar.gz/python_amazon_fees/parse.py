import package as pkg
from numpy import median
from decimal import Decimal

TWO_PLACES = Decimal("0.01")

class AmazonFeesCalculator(object):
	"""
	calculator = FBACalculator(length, weidth, height, [is_media, is_apparel, is_pro])
	fees = calculator.fees()
	"""

	PACKAGE_TYPES = {
		"SmallStandardMedia": pkg.SmallStandardMedia,
		"LargeStandardMedia": pkg.SmallStandardMedia,
		"XLargeStandardMedia": pkg.SmallStandardMedia,
		"SmallStandardNonMedia": pkg.SmallStandardNonMedia,
		"LargeStandardNonMedia": pkg.LargeStandardNonMedia,
		"XLargeStandardNonMedia": pkg.XLargeStandardNonMedia,
		"SmallOversize": pkg.SmallOversize,
		"MediumOversize": pkg.MediumOversize,
		"LargeOversize": pkg.LargeOversize,
		"SpecialOversize": pkg.SpecialOversize}

	def __init__(self,
				 length,
				 width,
				 height,
			     weight,
			     is_media = False,
			     is_apparel = False,
			     is_pro = False):

		self._height = pkg.Package.decimal(height)
		self._length = pkg.Package.decimal(length)
		self._width = pkg.Package.decimal(width)
		self._weight = pkg.Package.decimal(weight)
		self._is_media = is_media
		self._is_apparel = is_apparel
		self._is_pro = is_pro
		self._size = pkg.Package.size(self.length, self.width,
			self.height, self.weight)
		self._girth = pkg.Package.girth(self.length,
			self.width, self.height)
		self._tier = self._size_tier()
		self._package = self.thepackage()

	def fees(self):
		"""Calculate the FBA fees for the given package.

		Returns:
			:fees [Decimal]: FBA fees for the pacakge
		"""
		fees = self.package.pick_pack
		fees += self.package.weight_handling
		fees += self.package.thirtyday()
		fees += self.package.order_handling
		if self.package.is_apparel:
		    fees += Decimal("0.40")
		if not self.package.is_pro:
		    fees += Decimal("1.0")
		return fees.quantize(TWO_PLACES)

	def thepackage(self):
		thepackage = self._packageclass()
		return thepackage(self.height, self.length,
			self.width, self.weight, is_media=False,
			is_apparel=False, is_pro=False)

	def _packageclass(self):
		"""Create a package object.

		Returns:
			:package [ocls Package]: a reference to a package object
		"""
		if self.size == "Oversize":
			package = "{tier}{size}".format(tier=self.tier, size=self.size)
			return self.PACKAGE_TYPES[package]
		media = "NonMedia"
		if self.is_media:
			media = "Media"
		package = "{tier}{size}{media}".format(tier=self.tier,
			size=self.size, media=media)
		return self.PACKAGE_TYPES[package]

	def _size_tier(self):
		"""Determine whether the package is
			small, med, lrg, xlrg, special size
		"""
		if self.size == "Standard":
			size_tier = self._standard()
			return size_tier
		#pacakge is oversize
		size_tier = self._oversize()
		return size_tier

	def _standard(self):
		"""Determine whether the package is
			small, lrg size

		Returns:
			:[string]: Small | Large
		"""
		fee_weight = 12/16.0
		if self.is_media:
			fee_weight = 14/16.0
		small = [(fee_weight >= self.weight),
		    (max(self.length, self.width, self.height) <= 15),
		    (min(self.length, self.width, self.height) <= 0.75),
		    (median([self.length, self.width, self.height]) <= 12)]
		if all(small):
			return "Small"
		return "Large"

	def _oversize(self):
		"""Determine whether the package is
			small, medium, large, or special size

		Returns:
			:[string]: Special | Large | Medium | Small
		"""
		special = [(self.girth > 165), (self.weight > 150),
			(max(self.length, self.width, self.height) > 108)]
		medium = [(self.weight > 70),
			(max(self.length, self.width, self.height) > 60),
		    (median([self.length, self.width, self.height]) > 30)]
		if any(special):
		    return "Special"
		if self.girth > 130:
		    return "Large"
		if any(medium):
		    return "Medium"
		return "Small"


	@property
	def height(self):
	    return self._height

	@property
	def length(self):
	    return self._length

	@property
	def width(self):
	    return self._width

	@property
	def weight(self):
	    return self._weight

	@property
	def is_media(self):
	    return self._is_media

	@property
	def is_apparel(self):
	    return self._is_apparel

	@property
	def is_pro(self):
	    return self._is_pro

	@property
	def size(self):
		return self._size

	@property
	def tier(self):
		return self._tier

	@property
	def girth(self):
		return self._girth

	@property
	def package(self):
		return self._package
