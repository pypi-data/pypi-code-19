class tokenizer(object):
    delims = '(),'

    def __init__(self, production):
        self.prod = production.replace(' ', '')
        self.pos = 0
        self.tok = ''
        self.advance()

    def advance(self):
        if self.empty():
            return

        self.tok = self.prod[0]
        if self.tok not in self.delims:
            o = 0
            for c in self.prod:
                if c in self.delims:
                    break
                o = o + 1
            self.tok = self.prod[0:o]

    def empty(self):
        return len(self.prod) == 0

    def peek(self):
        return self.tok

    def next(self):
        tok = self.tok

        lt = len(tok)
        self.prod = self.prod[lt:]
        self.pos = self.pos + lt
        self.advance()

        return tok

class parser(object):
    def __init__(self, code, **kwargs):
        self.tokens = tokenizer(code)
        self.shiftwidth = kwargs.get('shiftwidth', 4)
        self.bemmy = kwargs.get('bemmy', False)

    def expect(self, c):
        if self.tokens.next() != c:
            pos = self.tokens.pos
            raise RuntimeError("Expected '{}' at position {}".format(c, pos))

    def parse(self, depth=0):
        name = self.tokens.next()
        if name in tokenizer.delims:
            raise RuntimeError(
                'Expected selector. Found reserved character ' + name)

        indent = ' '*(depth*self.shiftwidth)

        if depth > 0 and self.bemmy:
            name = '&' + name
        else:
            name = '.' + name

        kids = ''
        if self.tokens.peek() == '(':
            self.expect('(')
            kids = self.parse(depth + 1)
            self.expect(')')

        body = "{0}{1} {{\n{2}{0}}}\n".format(indent, name, kids)

        sibling = ''
        if not self.tokens.empty() and self.tokens.peek() != ')':
            self.expect(',')
            body += "\n"
            sibling = self.parse(depth)

        return body + sibling

def plot(code, **kwargs):
    return parser(code, **kwargs).parse()
