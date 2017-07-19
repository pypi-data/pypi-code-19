class Style(object):
    def __str__(self):
        if len(self.__dict__) < 1:
            return ''
        s_str = ''.join(['%s:%s;' % (k, str(v)) for k, v in self.__dict__.items()])
        return ' style="' + s_str + '"'


class Node(object):
    TAG = ''
    PRIVATE_ATTR = ['style', 'parent']

    def __init__(self, x=None, y=None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.style = Style()

    def translate(self, tx, ty=None):
        y = ''
        if ty is not None:
            y = ' %f' % float(ty)
        if self.transform:
            self.transform += ' '
        self.transform += 'translate(%f%s)' % (float(tx), y)

    def scale(self, sx, sy=None):
        y = ''
        if sy is not None:
            y = ' %f' % float(sy)
        if self.transform:
            self.transform += ' '
        self.transform += 'scale(%f%s)' % (float(sx), y)

    def rotate(self, angle=180, cx=0, cy=0):
        if self.transform:
            self.transform += ' '
        if cx or cy:
            p = ' %f %f' % (float(cx), float(cy))
        self.transform += 'rotate(%f%s)' % (float(angle), p)

    def attr_str(self):
        r = ' '.join(['%s="%s"' % (k, str(v)) for k, v in self.__dict__.items()
                      if k not in self.PRIVATE_ATTR and v])
        if not r:
            return ''
        return ' ' + r

    def __str__(self):
        return '<%s%s%s' % (self.TAG, self.attr_str(), str(self.style))


class Element(Node):
    def __str__(self):
        return Node.__str__(self) + '/>'


class Group(Node):
    TAG = 'g'
    Node.PRIVATE_ATTR.append('children')

    def __init__(self, x=None, y=None):
        Node.__init__(self, x, y)
        self.children = []

    def add(self, node):
        self.children.append(node)
        node.parent = self

    def get_box(self):
        if not self.children:
            return [0, 0, 0, 0]
        boxes = [c.get_box() for c in self.children]
        bound = [min([b[0] for b in boxes]), min([b[1] for b in boxes]),
                 max([b[2] for b in boxes]), max([b[3] for b in boxes])]
        if 'x' in self.__dict__ and self.x < bound[0]:
            bound[0] = self.x
            if 'width' in self.__dict__ and self.x+self.width > bound[2]:
                bound[2] = self.x+self.width
        if 'y' in self.__dict__ and self.y < bound[1]:
            bound[1] = self.y
            if 'height' in self.__dict__ and self.y+self.height > bound[3]:
                bound[3] = self.y+self.height
        return bound

    def child_str(self):
        return '\n'.join([str(_) for _ in self.children])

    def css_str(self):
        if 'CSS' in self.__class__.__dict__ and self.CSS:
            return '\n<style type="text/css"><![CDATA[ %s ]]></style>' % self.CSS
        return ''

    def __str__(self):
        childstr = str(self.child_str())
        if childstr:
            childstr = '\n' + childstr + '\n'
        return Node.__str__(self) + '>%s\n%s\n</%s>' % (self.css_str(), self.child_str(), self.TAG)


class SVG(Group):
    TAG = 'svg'
    CSS = ''

    def __init__(self):
        Group.__init__(self)
        self.xmlns = 'http://www.w3.org/2000/svg'

    def auto_resize(self):
        box = self.get_box()
        box[2] = box[2]-box[0]
        box[3] = box[3]-box[1]
        self.viewBox = ' '.join([str(x) for x in box])

    def __str__(self):
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + Group.__str__(self)


class Text(Element):
    TAG = 'text'
    Element.PRIVATE_ATTR.append('text')

    def __init__(self, text, x=None, y=None):
        Element.__init__(self, x, y)
        self.text = text

    def get_box(self):
        size = 12
        if 'font-size' in self.style.__dict__ and self.style.__dict__['font-size'].isdigit():
            size = int(self.style.__dict__['font-size'])
        if 'text-anchor' in self.__dict__:
            if self.__dict__['text-anchor'] == 'end':
                return [self.x-len(self.text)*int(size/2), self.y, self.x, self.y-size]
        return [self.x, self.y, self.x+len(self.text)*int(size/2), self.y-size]

    def __str__(self):
        return Node.__str__(self) + '>%s</%s>' % (self.text, self.TAG)


class Rect(Element):
    TAG = 'rect'

    def __init__(self, x=None, y=None, width=None, height=None, rx=None, ry=None):
        Element.__init__(self, x, y)
        self.width = width
        self.height = height
        self.rx = rx
        self.ry = ry

    def get_box(self):
        return [self.x, self.y, self.x+self.width, self.y+self.height]


class Circle(Element):
    TAG = 'circle'

    def __init__(self, cx=None, cy=None, r=None):
        Element.__init__(self)
        self.cx = cx
        self.cy = cy
        self.r = r

    def get_box(self):
        return [self.cx-self.r, self.cy-self.r, self.cx+self.r, self.cy+self.r]


class Ellipse(Element):
    TAG = 'ellipse'

    def __init__(self, cx=None, cy=None, rx=None, ry=None):
        Element.__init__(self)
        self.cx = cx
        self.cy = cy
        self.rx = rx
        self.ry = ry

    def get_box(self):
        return [self.cx-self.rx, self.cy-self.ry, self.cx+self.rx, self.cy+self.ry]


class Line(Element):
    TAG = 'line'

    def __init__(self, x1=None, x2=None, y1=None, y2=None):
        Element.__init__(self)
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def get_box(self):
        return [min(self.x1, self.x2), min(self.y1, self.y2),
                max(self.x1, self.x2), max(self.y1, self.y2)]


class Polygon(Element):
    TAG = 'polygon'
    Element.PRIVATE_ATTR.append('points')

    def __init__(self, points=[]):
        Element.__init__(self)
        self.points = points

    def __str__(self):
        p_str = ' points="' + ' '.join(['%d,%d' % (x, y) for x, y in self.points]) + '"'
        return Node.__str__(self) + p_str + '/>'


class Polyline(Polygon):
    TAG = 'polyline'


class Path(Element):
    TAG = 'path'

    def __init__(self, d=[]):
        Element.__init__(self)
        self.d = d
