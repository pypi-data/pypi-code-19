import math

from pyrogi.drawing import Color, Paint

class SolidPaint(Paint):
    def __init__(self, color):
        self.color = color
    def get_tile_color(self, absolute_position, relative_position):
        return self.color


class GradientPaint(Paint):
    pass


class LinearGradientPaint(GradientPaint):
    def __init__(self, color1, position1, color2, position2, is_cyclical=True, is_relative=True):
        self.color1 = color1
        self.position1 = position1
        self.color2 = color2
        self.position2 = position2
        self.is_cyclical = is_cyclical
        self.is_relative = is_relative
        self.direction_vector = (self.position2 - self.position1).normalized()
    def get_tile_color(self, relative_position, absolute_position):
        position = relative_position if self.is_relative else absolute_position
        projection = position.dot(self.direction_vector) # project the position onto the linear direction vector
        p1_projection = self.position1.dot(self.direction_vector)
        p2_projection = self.position2.dot(self.direction_vector)
        percent = self._get_percent_along_projection(projection, p1_projection, p2_projection)
        return Color(
            int(round(self.color1.r + percent * (self.color2.r - self.color1.r))),
            int(round(self.color1.g + percent * (self.color2.g - self.color1.g))),
            int(round(self.color1.b + percent * (self.color2.b - self.color1.b))),
            int(round(self.color1.a + percent * (self.color2.a - self.color1.a))),
        )
    def _get_percent_along_projection(self, projection, p1_projection, p2_projection):
        diff = p2_projection - p1_projection
        raw_percent = (projection-p1_projection) / diff
        if self.is_cyclical:
            must_inverse = int(raw_percent) % 2 == 1
            fractional_part = math.modf(raw_percent)[0]
            percent_before_inverse = abs(fractional_part)
            return 1-percent_before_inverse if must_inverse else percent_before_inverse
        else:
            if raw_percent < 0:
                return 0
            elif raw_percent > 1:
                return 1
            else:
                return raw_percent
