


def percentOf(portion,total):
    a = portion
    b = total

    c = a / b
    d = c * 100

    return d

def index_of_element(sequence, element):
    """
    Finds the index of a certain element in a list. Returns the index of the first occurrence or ValueError if the
    element is not contained in the list. Raises a ValueError if the element is not contained in the sequence.

    Note: This is a slow operation (O(n)).

    :param sequence: iterable
    :param element: single element
    :return: the index of the element
    """
    for index, e in enumerate(sequence):
        if e == element:
            return index
    raise ValueError('element not contained in sequence')

class List2D:
    """
    Implements an 2D array with getter and setter for two indices (x,y). Based on a list but with a mapping of the
    two-dimensional indices into a one-dimensional index.
    """

    def __init__(self, dimension):
        """
        Creates an empty array with a given 2D dimension (tuple - width/height).

        :param dimension: Dimension
        """
        # create empty list
        size = dimension[0] * dimension[1]
        self._array = [0] * size
        # store dimension
        self.dimension = dimension

    def get(self, x, y):
        """
        Returns the element at position (x,y).

        :param x: x position
        :param y: y position
        :return: value
        """
        index = x + self.dimension[0] * y
        return self._array[index]

    def set(self, x, y, v):
        """
        Sets the element at position (x,y).

        :param x: x position
        :param y: y position
        :param v: value
        """
        index = x + self.dimension[0] * y
        self._array[index] = v