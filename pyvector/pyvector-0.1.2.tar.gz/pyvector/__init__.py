class Style(object):
    def __str__(self):
        if len(self.__dict__) < 1:
            return ''
        s_str = ' '.join(['%s: %s;' % (k.replace('_', '-'), str(v))
                          for k, v in self.__dict__.items() if v])
        return ' style="' + s_str + '"'


class Node(object):
    TAG = ''
    PRIVATE_ATTR = ['style', 'parent', 'class_name', 'transform']

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.style = Style()
        self.class_name = ''
        self.transform = []

    def translate(self, tx, ty=None):
        if ty is None:
            ty = tx
        self.transform.append(['translate', [tx, ty]])
        return self

    def scale(self, sx, sy=None):
        if sy is None:
            sy = sx
        self.transform.append(['scale', [sx, sy]])
        return self

    def rotate(self, angle=180, cx=None, cy=None):
        if cx is None or cy is None:
            self.transform.append(['rotate', [angle]])
        else:
            self.transform.append(['rotate', [angle, cx, cy]])
        return self

    def transform_str(self):
        return ' '.join(['%s(%s)' % (t, ', '.join([str(x) for x in c])) for t, c in self.transform])

    def apply_transform(self):
        for t, c in self.transform:
            if t == 'translate':
                self.x += c[0]
                self.y += c[1]
            elif t == 'scale':
                self.x *= c[0]
                self.y *= c[1]
        self.transform = [t for t in self.transform if t[0] == 'rotate']
        return self

    def attr_str(self):
        if self.class_name:
            self.__dict__['class'] = self.class_name
        r = ' '.join(['%s="%s"' % (k.replace('_', '-'), str(v)) for k, v in self.__dict__.items()
                      if k not in self.PRIVATE_ATTR and v])
        if self.transform:
            r += ' transform="' + self.transform_str() + '"'
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

    def __init__(self, x=0, y=0):
        Node.__init__(self, x, y)
        self.children = []

    def add(self, node):
        self.children.append(node)
        node.parent = self
        return self

    def get_box(self):
        if not self.children:
            return [self.x, self.y, self.x, self.y]
        boxes = [c.get_box() for c in self.children]
        bound = [min([b[0] for b in boxes]), min([b[1] for b in boxes]),
                 max([b[2] for b in boxes]), max([b[3] for b in boxes])]
        if 'x' in self.__dict__ and self.x and self.x < bound[0]:
            bound[0] = self.x
            if 'width' in self.__dict__ and self.x+self.width > bound[2]:
                bound[2] = self.x+self.width
        if 'y' in self.__dict__ and self.y and self.y < bound[1]:
            bound[1] = self.y
            if 'height' in self.__dict__ and self.y+self.height > bound[3]:
                bound[3] = self.y+self.height
        return bound

    def apply_transform(self):
        trans = [t for t in self.transform if t[0] != 'rotate']
        for c in self.children:
            c.transform.extend(trans)
            c.apply_transform()
        for t, c in trans:
            if t == 'translate':
                self.x += c[0]
                self.y += c[1]
            elif t == 'scale':
                self.x *= c[0]
                self.y *= c[1]
        self.transform = [t for t in self.transform if t[0] == 'rotate']
        return self

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
        self.viewBox = ''

    def auto_resize(self):
        box = self.get_box()
        box[2] = box[2]-box[0]
        box[3] = box[3]-box[1]
        self.viewBox = ' '.join([str(x) for x in box])
        return self

    def __str__(self):
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + Group.__str__(self)


class Text(Element):
    TAG = 'text'
    Element.PRIVATE_ATTR.append('text')

    def __init__(self, text, x=0, y=0):
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

    def __init__(self, x=0, y=0, width=0, height=0, rx=0, ry=0):
        Element.__init__(self, x, y)
        self.width = width
        self.height = height
        self.rx = rx
        self.ry = ry

    def apply_transform(self):
        for t, c in self.transform:
            if t == 'translate':
                self.x += c[0]
                self.y += c[1]
            elif t == 'scale':
                self.x *= c[0]
                self.y *= c[1]
                self.width *= c[0]
                self.height *= c[1]
                self.rx *= c[0]
                self.ry *= c[1]
        self.transform = [t for t in self.transform if t[0] == 'rotate']
        return self

    def get_box(self):
        return [self.x, self.y, self.x+self.width, self.y+self.height]


class Circle(Element):
    TAG = 'circle'

    def __init__(self, cx=0, cy=0, r=0):
        Element.__init__(self)
        self.cx = cx
        self.cy = cy
        self.r = r

    def get_box(self):
        return [self.cx-self.r, self.cy-self.r, self.cx+self.r, self.cy+self.r]


class Ellipse(Element):
    TAG = 'ellipse'

    def __init__(self, cx=0, cy=0, rx=0, ry=0):
        Element.__init__(self)
        self.cx = cx
        self.cy = cy
        self.rx = rx
        self.ry = ry

    def get_box(self):
        return [self.cx-self.rx, self.cy-self.ry, self.cx+self.rx, self.cy+self.ry]


class Line(Element):
    TAG = 'line'

    def __init__(self, x1=0, x2=0, y1=0, y2=0):
        Element.__init__(self)
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def apply_transform(self):
        for t, c in self.transform:
            if t == 'translate':
                self.x1 += c[0]
                self.x2 += c[0]
                self.y1 += c[1]
                self.y2 += c[1]
            elif t == 'scale':
                self.x1 *= c[0]
                self.x2 *= c[0]
                self.y1 *= c[1]
                self.y2 *= c[1]
        self.transform = [t for t in self.transform if t[0] == 'rotate']
        return self

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
        p_str = ' points="'
        p_str += ' '.join(['%f,%f' % (float(x), float(y)) for x, y in self.points])
        p_str += '"'
        return Node.__str__(self) + p_str + '/>'


class Polyline(Polygon):
    TAG = 'polyline'


class Path(Element):
    TAG = 'path'

    def __init__(self, d=[]):
        Element.__init__(self)
        self.d = d
