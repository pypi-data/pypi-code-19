BASE_INDENT = '    '

class AstNode(object):
    pass

class FieldPicker(AstNode):
    def __init__(self, key):
        self.key = key

class ValueExpr(AstNode):
    def __init__(self, fd):
        assert not isinstance(fd, ValueExpr)
        self.fd = fd
    def get_value(self, data):
        if isinstance(self.fd, list):
            d = data
            for picker in self.fd:
                d = d[picker.key]
            return d
        else:
            return self.fd
    def format(self):
        if isinstance(self.fd, list):
            d = '.'
            for picker in self.fd:
                d += '[%r]' % picker.key
            return d
        return repr(self.fd)

class Compare(AstNode):
    def __init__(self, a, b, op):
        self.a = a
        self.b = b
        self.op = op
    def test(self, data):
        a = self.a.get_value(data)
        b = self.b.get_value(data)
        if self.op == '==':
            r = a == b
        elif self.op == '!=':
            r = a != b
        elif self.op == '>':
            r = a > b
        elif self.op == '<':
            r = a < b
        elif self.op == '>=':
            r = a >= b
        elif self.op == '<=':
            r = a <= b
        elif self.op == 'in':
            r = a in b
        #print a, self.op, b, r
        return r
    def format(self, lines, indent):
        lines.append('%s%s %s %s' % (
            indent,
            self.a.format(),
            self.op,
            self.b.format(),
        ))

class CondTerm(AstNode):
    def __init__(self):
        self.exprs = []
    def test(self, data):
        for expr in self.exprs:
            if not expr.test(data):
                return False
        return True
    def format(self, lines, indent):
        lines.append('%sCondTerm[%d](' % (indent, len(self.exprs)))
        for expr in self.exprs:
            expr.format(lines, indent + BASE_INDENT)
        lines.append('%s)' % indent)

class CondExpr(AstNode):
    def __init__(self):
        self.terms = []
        self.not_expr = False
    def test(self, data):
        r = len(self.terms) == 0
        for term in self.terms:
            if term.test(data):
                r = True
                break
        if self.not_expr:
            return not r
        return r
    def format(self, lines, indent):
        if self.not_expr:
            lines.append('%sNotCondExpr[%d](' % (indent, len(self.terms)))
        else:
            lines.append('%sCondExpr[%d](' % (indent, len(self.terms)))
        for term in self.terms:
            term.format(lines, indent + BASE_INDENT)
        lines.append('%s)' % indent)

class Query(AstNode):
    def __init__(self, fields, conditions):
        self.fields = fields
        self.conditions = conditions

    def format(self, lines, indent=''):
        lines.append('Query(')
        lines.append('%sFields(' % BASE_INDENT)
        for field in self.fields:
            lines.append(BASE_INDENT * 2 + field.format())
        lines.append('%s)' % BASE_INDENT)
        self.conditions.format(lines, BASE_INDENT)
        lines.append(')')

    def __str__(self):
        lines = []
        self.format(lines)
        return '\n'.join(lines)

    def test(self, data):
        return self.conditions.test(data)

    def pick(self, data):
        return tuple([ve.get_value(data) for ve in self.fields])
                
