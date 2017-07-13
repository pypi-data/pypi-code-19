# -*- coding: utf-8 -*-
from pyparsing import quotedString, dblQuotedString, nums, Optional, OneOrMore, Word, Literal, alphanums, alphas, \
    Combine, CaselessLiteral, Group, Forward, ZeroOrMore, replaceWith, ParseException
from booley.exceptions import UnknownOperation, BooleySyntaxError
from booley.utils import flatten


class Booley(object):

    def __init__(self, context={}):
        self.variables = list()
        self.context = context
        self.parser = self._init_parser()

    def _get_str(self, string, location, tokens):
        token = tokens[0][0]
        value = token[1:-1]
        return value

    def get_string_parser(self):
        return Group(quotedString | dblQuotedString).setParseAction(self._get_str)

    def get_integer_parser(self):
        plus_or_minus = Literal('+') | Literal('-')
        number = Word(nums)
        return Combine(Optional(plus_or_minus) + number).setParseAction(lambda t: int(t[0]))

    def get_real_parser(self):
        integer = self.get_integer_parser()
        number = Word(nums)
        point = Literal('.')
        e = CaselessLiteral('E')
        return Combine(Optional(integer) + point + number + Optional(e + integer)).setParseAction(lambda t: float(t[0]))

    def get_boolean_parser(self):
        return CaselessLiteral("TRUE").setParseAction(replaceWith(True)) | CaselessLiteral("FALSE").setParseAction(replaceWith(False))

    def _get_variable_value(self, string, location, tokens):
        token = tokens[0]
        if token.endswith("]"):
            token_parts = token[:-1].split("[")
            token = token_parts[0]
            split = list(map(lambda x: int(x), token_parts[1].split(":")))
        else:
            split = list()
        if token not in self.variables:
            self.variables.append(token)
        if self.context is None:
            return '0'
        else:
            value = self.context.get(token)
            if not value:
                return ""
            elif type(value) == list:
                value = '|'.join(value)
            if len(split) == 2:
                return value[split[0]:split[1]]
            else:
                return value

    def get_variable_parser(self):
        slice = Combine(Literal('[') + Word(nums) + Literal(':') + Word(nums) + Literal(']'))
        return Combine(Word(alphas, alphanums + '_') + Optional(slice)).setParseAction(self._get_variable_value)

    def get_equality_comparison_operator_parser(self):
        return Literal('==') | Literal('!=') | Literal('=') | CaselessLiteral('HAS ') | CaselessLiteral('IN ')

    def get_including_operator_parser(self):
        return CaselessLiteral('IN ') | CaselessLiteral('NOT IN ') | CaselessLiteral('HAS ') | CaselessLiteral('NOT HAS ')

    def get_starts_with_operator_parser(self):
        return CaselessLiteral('STARTS WITH ') | CaselessLiteral('NOT STARTS WITH ')

    def get_ends_with_operator_parser(self):
        return CaselessLiteral('ENDS WITH ') | CaselessLiteral('NOT ENDS WITH ')

    def get_is_null_operator_parser(self):
        return CaselessLiteral('IS ') | CaselessLiteral('IS NOT ')

    def get_size_comparison_operator_parser(self):
        return Literal('<=') | Literal('>=') | Literal('<') | Literal('>')

    def get_comparison_operator_parser(self):
        return self.get_equality_comparison_operator_parser() | self.get_size_comparison_operator_parser() | \
               self.get_including_operator_parser() | self.get_starts_with_operator_parser() | \
               self.get_ends_with_operator_parser() | self.get_is_null_operator_parser()

    def get_numeric_value_parser(self):
        return self.get_variable_parser() | self.get_real_parser() | self.get_integer_parser()

    def _compare_num(self, string, location, tokens):
        token = flatten(tokens.asList())
        try:
            operator_a = float(token[0])
            operation = token[1]
            operator_b = float(token[2])
            return self._compare(operator_a, operation, operator_b)
        except ValueError as e:
            return self._compare_str(string, location, tokens)

    def _compare_str(self, string, location, tokens):
        token = flatten(tokens.asList())
        operator_a = token[0]
        operation = token[1]
        operator_b = token[2]
        return self._compare(operator_a, operation, operator_b)

    def _compare_length(self, string, location, tokens):
        token = flatten(tokens.asList())
        operator_a = token[0]
        operation = token[1]
        operator_b = token[2]
        if operation == "LENGTH IS ":
            return len(operator_a) == operator_b
        return len(operator_a) != operator_b

    def _compare(self, operator_a, operation, operator_b):
        if operation == '=' or operation == '==':
            return operator_a == operator_b
        elif operation == '!=':
            return operator_a != operator_b
        elif operation == '<':
            return operator_a < operator_b
        elif operation == '<=':
            return operator_a <= operator_b
        elif operation == '>':
            return operator_a > operator_b
        elif operation == '>=':
            return operator_a >= operator_b
        elif operation == 'HAS ':
            return operator_b in operator_a
        elif operation == 'NOT HAS ':
            return operator_b not in operator_a
        elif operation == 'IN ':
            return operator_a in operator_b
        elif operation == 'NOT IN ':
            return operator_a not in operator_b
        elif operation == 'STARTS WITH ':
            return operator_a.startswith(operator_b)
        elif operation == 'NOT STARTS WITH ':
            return not operator_a.startswith(operator_b)
        elif operation == 'ENDS WITH ':
            return operator_a.endswith(operator_b)
        elif operation == 'NOT ENDS WITH ':
            return not operator_a.endswith(operator_b)
        elif operation == 'IS ':
            if operator_b not in ('NULL', 'null'):
                raise BooleySyntaxError(u"Syntax error near '{1}' in '{0}': {2}. {2} must be 'NULL'".format(
                    operator_a, operation, operator_b
                ))
            return operator_a is None
        elif operation == 'IS NOT ':
            if operator_b not in ('NULL', 'null'):
                raise BooleySyntaxError(u"Syntax error near '{1}' in '{0}': {2}. {2} must be 'NULL'".format(
                    operator_a, operation, operator_b
                ))
            return operator_a is not None
        else:
            raise UnknownOperation(u"Unknown operation '{0}'".format(operation))

    def get_numeric_comparison_parser(self):
        numeric_value = self.get_numeric_value_parser()
        comparison_operator = self.get_comparison_operator_parser()
        return Group(numeric_value + comparison_operator + numeric_value).setParseAction(self._compare_num)

    def get_string_value_parser(self):
        return self.get_variable_parser() | self.get_string_parser()

    def get_string_comparison_parser(self):
        string_value = self.get_string_value_parser()
        comparison_operator = self.get_comparison_operator_parser()
        return Group(string_value + comparison_operator + string_value).setParseAction(self._compare_str)

    def get_length_comparison_parser(self):
        numeric_value = self.get_numeric_value_parser()
        string_value = self.get_string_value_parser()
        comparison_operator = CaselessLiteral('LENGTH IS NOT ') | CaselessLiteral('LENGTH IS ')
        return Group(string_value + comparison_operator + numeric_value).setParseAction(self._compare_length)

    def _compare_boolean(self, string, location, tokens):
        token = flatten(tokens.asList())
        operator_a = token[0]
        operation = token[1]
        operator_b = token[2]

        if operation == '=' or operation == '==':
            return operator_a == operator_b
        elif operation == '!=':
            return operator_a != operator_b
        else:
            raise UnknownOperation(u"Unknown operation '{0}' in '{1}'".format(operation, string))

    def _binary_boolean(self, string, location, tokens):
        list = flatten(tokens.asList())
        operator_a = None
        operation = None
        operator_b = None
        for item in list:
            if operator_a is None:
                operator_a = item
            elif operation is None:
                operation = item
            elif operator_b is None:
                operator_b = item
                if operation == 'AND':
                    operator_a = operator_a and operator_b
                elif operation == 'OR':
                    operator_a = operator_a or operator_b
                else:
                    raise UnknownOperation(u"Unknown operation '{0}' in '{1}'".format(operation, string))
                operation = None
                operator_b = None

        return operator_a

    def _boolean_not(self, string, location, tokens):
        list = flatten(tokens.asList())
        return not list[1]

    def get_boolean_binary_operation_parser(self):
        boolean = self.get_boolean_parser()
        equality_comparison_operator = self.get_equality_comparison_operator_parser()
        numeric_comparison = self.get_numeric_comparison_parser()
        string_comparison = self.get_string_comparison_parser()
        length_comparison = self.get_length_comparison_parser()

        boolean_operator = Forward()
        boolean_binary_operation = Forward()

        boolean_comparison = Group(boolean_operator + OneOrMore(equality_comparison_operator + boolean_operator)).setParseAction(self._compare_boolean)

        nested_boolean_operator = Group(Literal("(").suppress() + Group(boolean_binary_operation | boolean_comparison | numeric_comparison | string_comparison) + Literal(")").suppress())

        boolean_operator_not = Group(CaselessLiteral("NOT ") + boolean_operator).setParseAction(self._boolean_not)

        boolean_operator << Group(boolean | boolean_operator_not | length_comparison | numeric_comparison | string_comparison | nested_boolean_operator)

        boolean_binary_symbols = CaselessLiteral("AND") | CaselessLiteral("OR")

        boolean_binary_operator = Group(boolean_comparison | boolean_operator)

        boolean_binary_operation << Group(boolean_binary_operator + ZeroOrMore(
            boolean_binary_symbols + boolean_binary_operator)).setParseAction(self._binary_boolean)

        return boolean_binary_operation

    def _init_parser(self):
        return self.get_boolean_binary_operation_parser()

    def _parse(self, code):
        try:
            return self.parser.parseString(code, True)[0]
        except ParseException as e:
            raise BooleySyntaxError(u"Syntax error near '{1}' in '{0}': {2}".format(e.line, e.line[e.loc:10], e.msg))

    def parse(self, code, context=None):
        if context is not None:
            self.context = context
        return self._parse(code)

    def check_syntax(self, code):
        aux_context = self.context
        self.context = None
        value = self._parse(code)
        self.context = aux_context
        if value in (True, False):
            return True
        else:
            return False