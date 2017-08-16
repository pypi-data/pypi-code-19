import shutil


class Screen:
    _braille_base = 0x2800
    _braille_dot = (
        (0x01, 0x08),
        (0x02, 0x10),
        (0x04, 0x20),
        (0x40, 0x80))
    braille_width = 2
    braille_height = 4

    @staticmethod
    def _braille_subpixel(x, y):
        return Screen._braille_dot[y][x]

    @staticmethod
    def _terminal_size():
        w, h = shutil.get_terminal_size()
        w *= Screen.braille_width
        h *= Screen.braille_height
        return w, h

    def __init__(self, width=None, height=None, roundf=round):
        self._width = 1
        self._height = 1
        self.size = width, height

        self._round = roundf

    @property
    def width(self):
        return self._width * Screen.braille_width

    @width.setter
    def width(self, width):
        if width is None:
            width, _ = Screen._terminal_size()
        width -= width % Screen.braille_width
        width //= Screen.braille_width

        if width <= 0:
            raise ValueError(
                "Width must be larger than zero after convertion (it was {}).".format(width))

        self._width = width
        self.clear()

    @property
    def height(self):
        return self._height * Screen.braille_height

    @height.setter
    def height(self, height):
        if height is None:
            _, height = Screen._terminal_size()
        height -= height % Screen.braille_height
        height //= Screen.braille_height

        if height <= 0:
            raise ValueError(
                "Height must be larger than zero after convertion (it was {}).".format(height))

        self._height = height
        self.clear()

    @property
    def size(self):
        return self.width, self.height

    @size.setter
    def size(self, width_height):
        try:
            self.width, self.height = width_height
        except TypeError:
            raise TypeError("Setting size requires an iterable with two values.")

    def clear(self):
        self._screen = [[Screen._braille_base for _ in range(self._width)] for _ in range(self._height)]

    def __call__(self, x, y, mode=True):
        x, y = self._round(x), self._round(y)

        # skip a point if it's outside of the screen
        if x >= self.width or x < 0:
            return
        if y >= self.height or y < 0:
            return

        px, py = x // Screen.braille_width, y // Screen.braille_height
        sp = Screen._braille_subpixel(
            x % Screen.braille_width,
            y % Screen.braille_height)

        # do note that we can't just test mode since bool(None) would be False
        if mode is True:
            # turn x, y on
            self._screen[py][px] |= sp
        elif mode is False:
            # turn x, y off
            self._screen[py][px] |= ~sp
        elif mode is None:
            # toggle x, y
            self._screen[py][px] ^= sp
        else:
            raise TypeError("Mode must be one of (True, False, None).")

    def __str__(self):
        out = []
        for line in self._screen:
            out.append("".join(map(chr, line)))
        return "\n".join(out)
