# Structure
#    |- abstract Package
#        |- Mock Package
#        |- abstract Media
#            |- SmallStandardMedia
#            |- LargeStandardMedia
#            |- XLargeStandardMedia
#        |- abstract Standard
#            |- SmallStandardNonMedia
#            |- LargeStandardNonMedia
#            |- XLargeStandardNonMedia
#        |- abstract Oversize
#            |- SmallOversize
#            |- MediumOversize
#            |- LargeOversize
#            |- SpecialOversize
import math
import logging
from numpy import median
import six, abc
from decimal import Decimal, ROUND_HALF_UP, ROUND_UP


@six.add_metaclass(abc.ABCMeta)
class Package():

    TWO_PLACES = Decimal("0.01")

    def __init__(self,
                 packagetype,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        self._packagetype = packagetype
        self._height = self.decimal(height)
        self._length = self.decimal(length)
        self._width = self.decimal(width)
        self._weight = self.decimal(weight)
        self._is_media = is_media
        self._is_apparel = is_apparel
        self._is_pro = is_pro

    @staticmethod
    def decimal(num):
        """Tries to convert `num` to Decimal

        Args:
            :num Decimal Compatible:
                a number to be converted to Decimal

        Returns:
            :Decimal(num):
        """
        try:
            return Decimal(num)
        except:
            raise TypeError("Please provide Decimal compatible values.")

    @abc.abstractmethod
    def thirtyday(standard_oversize):
        pass

    @staticmethod
    def size(length, width, height, weight):
        """Determine if the package is standard or oversize.

        Args
            :length Decimal: length of package
            :width Decimal: width of package
            :height Decimal: height of package
            :weight Decimal: weight of package
        Return:
            :size str: amazon size of package. "Oversize" or "Standard"
        """
        size = "Standard"
        if any(
            [
                (weight > 20),
                (max(length, width, height) > 18),
                (min(length, width, height) > 8),
                (median([length, width, height]) > 14)
            ]
        ):
            size = "Oversize"
        return size

    @staticmethod
    def cubicfoot(length, width, height):
        cubicfoot = Decimal(length * width * height) / Decimal('1728.0')
        return cubicfoot

    @staticmethod
    def girth(length, width, height):
        girth = (
            max(length, width, height) +
            (median([length, width, height]) * 2) +
            (min(length, width, height) * 2))
        return Decimal(girth).quantize(Decimal("0.1"))

    def dimensional_weight(self):
        dimensional_weight = (
            Decimal(self.height * self.length * self.width) / Decimal(166.0)
        ).quantize(self.TWO_PLACES)
        return dimensional_weight

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


class Mock(Package):

    def __init__(self,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(Mock, self).__init__('Mock', height, length,
                                   width, weight, is_media, is_apparel, is_pro)


class Standard(Package):

    def __init__(self,
                 packagetype,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(Standard, self).__init__(packagetype, height, length,
                                       width, weight, is_media, is_apparel, is_pro)
        self._pick_pack = Decimal("1.06")

    def thirtyday(self):
        return Decimal('0.5525') * Package.cubicfoot(self.length,
                                                     self.width, self.height)

    @property
    def pick_pack(self):
        return self._pick_pack


class StandardNonMedia(Standard):

    def __init__(self,
                 packagetype,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(StandardNonMedia, self).__init__(packagetype, height, length, width,
                                               weight, is_media, is_apparel, is_pro)
        self._order_handling = 0
        self._package_weight = Package.decimal("0.25")

    @property
    def order_handling(self):
        return self._order_handling

    @property
    def package_weight(self):
        return self._package_weight

    @abc.abstractproperty
    def outbound(self):
        pass


class SmallStandardNonMedia(StandardNonMedia):

    def __init__(self,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(SmallStandardNonMedia, self).__init__('SmallStandardNonMedia', height, length,
                                                    width, weight, is_media, is_apparel, is_pro)
        self._weight_handling = Decimal("0.50")
        self._outbound = self._calculate_outbound()

    @property
    def package_type(self):
        return self._package_type

    @property
    def weight_handling(self):
        return self._weight_handling

    @property
    def outbound(self):
        return self._outbound

    def _calculate_outbound(self):
        return Decimal(
            self.weight + self.weight_handling
        ).quantize(Decimal('0'), rounding=ROUND_UP)


class LargeStandardNonMedia(StandardNonMedia):

    def __init__(self,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(LargeStandardNonMedia, self).__init__('LargeStandardNonMedia', height, length,
                                                    width, weight, is_media, is_apparel, is_pro)
        self._weight_handling = Decimal("0.96")
        self._outbound = self._calculate_outbound()

    @property
    def weight_handling(self):
        return self._weight_handling

    @property
    def outbound(self):
        return self._outbound

    def _calculate_outbound(self):
        outbound = Decimal(
            Decimal(max(self.weight, self.dimensional_weight())) +
            Decimal(self.package_weight)
        )
        return outbound.quantize(Decimal('0'), rounding=ROUND_UP)


class XLargeStandardNonMedia(LargeStandardNonMedia):

    def __init__(self,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(XLargeStandardNonMedia, self).__init__('XLargeStandardNonMedia', height, length,
                                                     width, weight, is_media, is_apparel, is_pro)
        self._weight_handling = Decimal("1.95")
        self._weight_handling_multiplier = Decimal("0.39")
        self._threshold = Decimal("2")

    @property
    def weight_handling(self):
        return self._weight_handling

    @property
    def weight_handling_multiplier(self):
        return self._weight_handling_multiplier

    @property
    def threshold(self):
        return self._threshold


class Media(Standard):

    def __init__(self,
                 packagetype,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(Media, self).__init__(packagetype, height, length,
                                    width, weight, is_media, is_apparel, is_pro)
        self._order_handling = 0
        self._package_weight = Package.decimal("0.125")

    @property
    def order_handling(self):
        return self._order_handling


class SmallStandardMedia(Media):

    def __init__(self,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(SmallStandardMedia, self).__init__('SmallStandardMedia', height, length,
                                                 width, weight, is_media, is_apparel, is_pro)
        self._weight_handling = Decimal("0.50")

    @property
    def weight_handling(self):
        return self._weight_handling


class LargeStandardMedia(Standard):

    def __init__(self,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(LargeStandardMedia, self).__init__('LargeStandardMedia', height, length,
                                                 width, weight, is_media, is_apparel, is_pro)
        self._weight_handling = Decimal("0.85")

    @property
    def weight_handling(self):
        return self._weight_handling


class XLargeStandardMedia(Standard):

    def __init__(self,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(XLargeStandardMedia, self).__init__('XLargeStandardMedia', height, length,
                                                  width, weight, is_media, is_apparel, is_pro)
        self._weight_handling = Decimal("1.24")
        self._weight_handling_multiplier = Decimal("0.41"),
        self._threshold = Decimal("2")

    @property
    def weight_handling(self):
        return self._weight_handling

    @property
    def weight_handling_multiplier(self):
        return self._weight_handling_multiplier


class Oversize(Package):

    def __init__(self,
                 packagetype,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(Oversize, self).__init__(packagetype, height, length,
                                       width, weight, is_media, is_apparel, is_pro)
        self._order_handling = Decimal("0")
        self._package_weight = Package.decimal("1.00")

    def thirtyday(self):
        return Decimal('0.4325') * self.cubicfoot(self.length,
                                                  self.width, self.height)

    def outbound(self):
        outbound = Decimal(self.weight + self.package_weight)
        return outbound.quantize(Decimal('0'), rounding=ROUND_UP)

    @property
    def order_handling(self):
        return self._order_handling

    @property
    def package_weight(self):
        return self._package_weight

    @abc.abstractproperty
    def pick_pack(self):
        pass

    @abc.abstractproperty
    def weight_handling(self):
        pass

    @abc.abstractproperty
    def weight_handling_multiplier(self):
        pass

    @abc.abstractproperty
    def threshold(self):
        pass


class SmallOversize(Oversize):

    def __init__(self,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(SmallOversize, self).__init__('SmallOversize', height, length,
                                            width, weight, is_media, is_apparel, is_pro)
        self._pick_pack = Decimal("4.09")
        self._weight_handling = Decimal("2.06")
        self._weight_handling_multiplier = Decimal("0.39")
        self._threshold = Decimal("2")

    @property
    def pick_pack(self):
        return self._pick_pack

    @property
    def weight_handling(self):
        return self._weight_handling

    @property
    def weight_handling_multiplier(self):
        return self._weight_handling_multiplier

    @property
    def threshold(self):
        return self._threshold


class MediumOversize(Oversize):

    def __init__(self,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(MediumOversize, self).__init__('MediumOversize', height, length,
                                             width, weight, is_media, is_apparel, is_pro)
        self._pick_pack = Decimal("5.20")
        self._weight_handling = Decimal("2.73")
        self._weight_handling_multiplier = Decimal("0.39")
        self._threshold = Decimal("2")

    @property
    def pick_pack(self):
        return self._pick_pack

    @property
    def weight_handling(self):
        return self._weight_handling

    @property
    def weight_handling_multiplier(self):
        return self._weight_handling_multiplier

    @property
    def threshold(self):
        return self._threshold


class LargeOversize(Oversize):

    def __init__(self,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(LargeOversize, self).__init__('LargeOversize', height, length,
                                            width, weight, is_media, is_apparel, is_pro)
        self._pick_pack = Decimal("8.40")
        self._weight_handling = Decimal("63.98")
        self._weight_handling_multiplier = Decimal("0.80")
        self._threshold = Decimal("90")

    @property
    def pick_pack(self):
        return self._pick_pack

    @property
    def weight_handling(self):
        return self._weight_handling

    @property
    def weight_handling_multiplier(self):
        return self._weight_handling_multiplier

    @property
    def threshold(self):
        return self._threshold


class SpecialOversize(Oversize):

    def __init__(self,
                 height,
                 length,
                 width,
                 weight,
                 is_media=False,
                 is_apparel=False,
                 is_pro=False):
        super(SpecialOversize, self).__init__('SpecialOversize', height, length,
                                              width, weight, is_media, is_apparel, is_pro)
        self._pick_pack = Decimal("10.53")
        self._weight_handling = Decimal("124.58")
        self._weight_handling_multiplier = Decimal("0.92")
        self._threshold = Decimal("90")

    @property
    def pick_pack(self):
        return self._pick_pack

    @property
    def weight_handling(self):
        return self._weight_handling

    @property
    def weight_handling_multiplier(self):
        return self._weight_handling_multiplier

    @property
    def threshold(self):
        return self._threshold

    def outbound(self):
        outbound = Decimal(
            Decimal(max(self.weight, self.dimensional_weight())) +
            Decimal(self.package_weight)
        )
        return outbound.quantize(Decimal('0'), rounding=ROUND_UP)
