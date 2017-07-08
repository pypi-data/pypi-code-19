import math

class Vec2(object):
    def __init__(self, x, y=None):
        if isinstance(x, tuple):
            self.x = x[0]
            self.y = x[1]
        else:
            self.x = x
            self.y = y

    def __mul__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x*other.x, self.y*other.y)
        else:
            return Vec2(other*self.x, other*self.y)
    def __rmul__(self, other):
        return self.__mul__(other)
    def __truediv__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x/other.x, self.y/other.y)
        else:
            return Vec2(self.x/other, self.y/other)
    def __rtruediv__(self, other):
        return Vec2(other/self.x, other/self.y)
    def __floordiv__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x//other.x, self.y//other.y)
        else:
            return Vec2(self.x//other, self.y//other)
    def __rfloordiv__(self, other):
        return Vec2(other//self.x, other//self.y)
    def __add__(self, other):
        return Vec2(self.x+other.x, self.y+other.y)
    def __sub__(self, other):
        return self.__add__(-other)
    def __neg__(self):
        return self.__mul__(-1)

    def dot(self, other):
        multiplied = self * other
        return multiplied.x + multiplied.y

    def magnitude(self):
        return math.sqrt(self.x*self.x + self.y*self.y)

    def normalized(self):
        magnitude = self.magnitude()
        if magnitude > 0:
            return self.__truediv__(magnitude)
        else:
            raise ValueError('Cannot normalize a vector of magnitude zero.')

    def __eq__(self, other):
        return isinstance(other, Vec2) and self.x == other.x and self.y == other.y
    def __ne__(self, other):
        return not self.__eq__(other)

    def to_tuple(self):
        return (self.x, self.y)

    def __str__(self):
        return str(self.to_tuple())
