from typing import Union, List, Tuple
from numpy import ndarray
from .vcontours import vContour, vContours
from .colors import vColor

# contour_list_type will accept either lists of type ndarray or vcontour,
# as well as vContours (which is a list subclass)
contour_list_type = Union[List[Union[List[ndarray],vContour]], vContours]

# color_type will accept either Tuples of three integers or a vColor class object
color_type = Union[Tuple[int, int, int], vColor]




