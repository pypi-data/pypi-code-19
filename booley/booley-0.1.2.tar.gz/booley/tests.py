# -*- coding: utf-8 -*-
import unittest
from pyparsing import ParseException
from booley.exceptions import BooleySyntaxError
from booley.parsers import Booley


class BooleyTests(unittest.TestCase):

    def setUp(self):
        self.context = {
            'name': 'Michael Jordan',
            'first_name': 'Michael',
            'last_name': 'Jordan',
            'weight': '98.0',
            'height': '1.98',
            'retired': True,
            'one': 1,
            'uno': 1,
            'two': 2,
            'dos': 2,
            'pi': 3.1416
        }
        self.parser = Booley(self.context)

    def test_string_parser(self):
        string_parser = self.parser.get_string_parser()

        code = "'simple quote'"
        result = string_parser.parseString(code)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'simple quote')

        code = '\'simple quote\''
        result = string_parser.parseString(code)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'simple quote')

        code = '"double quote"'
        result = string_parser.parseString(code)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "double quote")

        code = "\"double quote\""
        result = string_parser.parseString(code)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "double quote")

    def test_integer_parser(self):
        integer_parser = self.parser.get_integer_parser()

        code = '9111'
        result = integer_parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(9111, result[0])

        code = '+9111'
        result = integer_parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(9111, result[0])

        code = '-9111'
        result = integer_parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(-9111, result[0])

        with self.assertRaises(ParseException):
            integer_parser.parseString('"9111"')

    def test_real_parser(self):
        real_parser = self.parser.get_real_parser()

        code = '1.0'
        result = real_parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(1.0, result[0])

        code = '.123'
        result = real_parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(0.123, result[0])

        code = '0.123'
        result = real_parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(0.123, result[0])

        code = '-1.12355'
        result = real_parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(-1.12355, result[0])

        code = '+1.12355'
        result = real_parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(1.12355, result[0])

        with self.assertRaises(ParseException):
            real_parser.parseString('"+1.12355"')

    def test_boolean_parser(self):
        boolean_parser = self.parser.get_boolean_parser()

        code = 'TRUE'
        result = boolean_parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertTrue(result[0])

        code = 'true'
        result = boolean_parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertTrue(result[0])

        code = 'True'
        result = boolean_parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertTrue(result[0])

        with self.assertRaises(ParseException):
            boolean_parser.parseString('"True"')

        code = 'FALSE'
        result = boolean_parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertFalse(result[0])

        code = 'false'
        result = boolean_parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertFalse(result[0])

        code = 'False'
        result = boolean_parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertFalse(result[0])

        with self.assertRaises(ParseException):
            boolean_parser.parseString('"False"')

    def test_variable_parser(self):
        var_parser = self.parser.get_variable_parser()

        varname = 'name'
        result = var_parser.parseString(varname)
        self.assertEqual(1, len(result))
        self.assertEqual(self.context.get(varname), result[0])

        varname = 'weight'
        result = var_parser.parseString(varname)
        self.assertEqual(1, len(result))
        self.assertEqual(self.context.get(varname), result[0])

        varname = 'height'
        result = var_parser.parseString(varname)
        self.assertEqual(1, len(result))
        self.assertEqual(self.context.get(varname), result[0])

        varname = 'retired'
        result = var_parser.parseString(varname)
        self.assertEqual(1, len(result))
        self.assertEqual(self.context.get(varname), result[0])

        with self.assertRaises(ParseException):
            var_parser.parseString('123a')

    def test_equality_comparison_operator_parser(self):
        parser = self.parser.get_equality_comparison_operator_parser()

        code = '=='
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(code, result[0])

        code = '='
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(code, result[0])

        code = '!='
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(code, result[0])

        with self.assertRaises(ParseException):
            parser.parseString('"="')

        with self.assertRaises(ParseException):
            parser.parseString('"=="')

        with self.assertRaises(ParseException):
            parser.parseString('"!="')

    def test_size_comparison_operator_parser(self):
        parser = self.parser.get_size_comparison_operator_parser()

        code = '<'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(code, result[0])

        code = '<='
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(code, result[0])

        code = '>'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(code, result[0])

        code = '>='
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(code, result[0])

        with self.assertRaises(ParseException):
            parser.parseString('=<')

        with self.assertRaises(ParseException):
            parser.parseString('=>')

    def test_comparison_operator_parser(self):
        parser = self.parser.get_comparison_operator_parser()

        code = '=='
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(code, result[0])

        code = '='
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(code, result[0])

        code = '!='
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(code, result[0])

        with self.assertRaises(ParseException):
            parser.parseString('"="')

        with self.assertRaises(ParseException):
            parser.parseString('"=="')

        with self.assertRaises(ParseException):
            parser.parseString('"!="')

        code = '<'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(code, result[0])

        code = '<='
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(code, result[0])

        code = '>'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(code, result[0])

        code = '>='
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(code, result[0])

        with self.assertRaises(ParseException):
            parser.parseString('=<', True)

        with self.assertRaises(ParseException):
            parser.parseString('=>', True)

    def test_numeric_value_parser(self):
        parser = self.parser.get_numeric_value_parser()

        code = '9111'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(9111, result[0])

        code = '+9111'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(9111, result[0])

        code = '-9111'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(-9111, result[0])

        code = '1.0'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(1.0, result[0])

        code = '.123'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(0.123, result[0])

        code = '0.123'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(0.123, result[0])

        code = '-1.12355'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(-1.12355, result[0])

        code = '+1.12355'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(1.12355, result[0])

        code = 'one'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(self.context.get(code), result[0])

        code = 'two'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(self.context.get(code), result[0])

        code = 'pi'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(self.context.get(code), result[0])

        with self.assertRaises(ParseException):
            parser.parseString('"9111"')

        with self.assertRaises(ParseException):
            parser.parseString('"+1.12355"')

    def test_numeric_comparison_parser(self):
        parser = self.parser.get_numeric_comparison_parser()
        cases = [
            ('9 == 9', '9 == 10'),
            ('9 = 9', '9 = 10'),
            ('9 != 10', '9 != 9'),
            ('9 < 10', '9 < 9'),
            ('9 <= 10', '9 <= 7'),
            ('9 <= 9', '9 <= 8'),
            ('10 > 9', '9 > 9'),
            ('9 >= 9', '8 >= 9'),
            ('10 >= 9', '7 >= 9'),
            # using vars
            ('two == dos', 'two == uno'),
            ('two = two', 'two = pi'),
            ('two != pi', 'two != two'),
            ('two < pi', 'two < two'),
            ('two <= pi', 'two <= one'),
            ('two <= two', 'two <= one'),
            ('pi > two', 'two > two'),
            ('two >= two', 'one >= two'),
            ('pi >= two', 'one >= two'),
        ]
        for case in cases:
            code = case[0]  # True case
            result = parser.parseString(code)
            self.assertEqual(1, len(result))
            self.assertTrue(result[0])
            code = case[1]  # False case
            result = parser.parseString(code)
            self.assertEqual(1, len(result))
            self.assertFalse(result[0])

    def test_string_value_parser(self):
        parser = self.parser.get_string_value_parser()

        code = "'simple quote'"
        result = parser.parseString(code)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'simple quote')

        code = '\'simple quote\''
        result = parser.parseString(code)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'simple quote')

        code = '"double quote"'
        result = parser.parseString(code)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "double quote")

        code = "\"double quote\""
        result = parser.parseString(code)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "double quote")

        code = 'name'
        result = parser.parseString(code)
        self.assertEqual(1, len(result))
        self.assertEqual(self.context.get(code), result[0])

        with self.assertRaises(ParseException):
            parser.parseString('123a')

    def test_string_comparison_parser(self):
        parser = self.parser.get_string_comparison_parser()
        cases = [
            ('"I love code" == "I love code"', '"I love code" == "I don\'t love code"'),
            ('first_name == "Michael"', 'last_name == "Michael"'),
            ('"Jordan" == last_name', '"Michael" == last_name'),
            ('"I love code" != "I don\'t love code"', '"I love code" != "I love code"'),
            ('first_name != "Jordan"', 'first_name != "Michael"'),
            ('"Michael" != last_name', '"Jordan" != last_name'),
            ('"1" < "2"', '"1" > "2"'),
            ('"1" <= "1"', '"1" <= "0"'),
            ('"2" > "1"', '"2" < "1"'),
            ('"1" >= "1"', '"0" >= "1"')
        ]
        for case in cases:
            code = case[0]  # True case
            result = parser.parseString(code)
            self.assertEqual(1, len(result))
            self.assertTrue(result[0], "In {0}".format(code))
            code = case[1]  # False case
            result = parser.parseString(code)
            self.assertEqual(1, len(result))
            self.assertFalse(result[0], "In {0}".format(code))

    def test_boolean_comparison_parser(self):
        parser = self.parser.get_boolean_binary_operation_parser()
        cases = [
            ('TRUE', 'NOT TRUE'),
            ('NOT FALSE', 'FALSE'),

            ('TRUE == TRUE', 'TRUE != TRUE'),
            ('NOT (TRUE != TRUE)', 'NOT (TRUE == TRUE)'),

            ('FALSE == FALSE', 'FALSE != FALSE'),
            ('NOT (FALSE != FALSE)', 'NOT (FALSE == FALSE)'),

            ('1 < 2 == 2 > 1', '1 < 2 != 2 > 1'),
            ('NOT (1 < 2 != 2 > 1)', 'NOT (1 < 2 == 2 > 1)'),

            ('NOT (FALSE != NOT (1 > 2)) == NOT TRUE', 'NOT (NOT (FALSE != NOT (1 > 2)) == NOT TRUE)'),

            ('NOT (first_name == "Jordan")', 'NOT (first_name == "Michael")'),
        ]
        for case in cases:
            code = case[0]  # True case
            result = parser.parseString(code)
            self.assertEqual(1, len(result))
            self.assertTrue(result[0], "In {0}".format(code))
            code = case[1]  # False case
            result = parser.parseString(code)
            self.assertEqual(1, len(result))
            self.assertFalse(result[0], "In {0}".format(code))

    def test_boolean_binary_operation_parser(self):
        parser = self.parser.get_boolean_binary_operation_parser()
        cases = [
            ('TRUE', True),
            ('TRUE AND TRUE', True),
            ('TRUE AND FALSE', False),
            ('TRUE OR FALSE', True),
            ('NOT TRUE OR FALSE', False),
            ('NOT FALSE AND NOT FALSE', True),
            ('TRUE OR TRUE OR TRUE OR TRUE', True),

            ('TRUE', True),
            ('(2 > 1)', True),
            ('TRUE AND (2 > 1)', True),

            ('1 == 1', True),
            ('NOT 1 == 1', False),

            ('1 = 1', True),
            ('NOT 1 = 1', False),

            ('TRUE AND (2 > 1) AND NOT 1 == 1', False),

            ("'a' != 'b'", True),

            ("TRUE AND (2 > 1) AND NOT 1 == 1 OR 'a' != 'b'", True),

            ('height > 2', False),
            ('2 > 1', True),
            ('TRUE OR (2 > 1)', True),
            ('((TRUE OR (2 > 1)) == (height > 2))', False),
            ('NOT ((TRUE OR (2 > 1)) == (height > 2))', True),

            ("TRUE AND (2 > 1) AND NOT 1 == 1 OR 'a' != 'b' OR NOT ((TRUE OR (2 > 1)) == (height > 2))", True)
        ]
        for case in cases:
            result = parser.parseString(case[0])
            self.assertEqual(1, len(result))
            self.assertEqual(case[1], result[0], "In {0}".format(case[0]))

    def test_syntax_check(self):
        ok_cases = [
            'TRUE',
            'TRUE AND TRUE',
            'TRUE AND FALSE',
            'TRUE OR FALSE',
            'NOT TRUE OR FALSE',
            'NOT FALSE AND NOT FALSE',
            'TRUE OR TRUE OR TRUE OR TRUE',
            'TRUE',
            '(2 > 1)',
            'TRUE AND (2 > 1)',
            '1 == 1',
            '1 = 1',
            'NOT 1 == 1',
            'TRUE AND (2 > 1) AND NOT 1 == 1',
            "'a' != 'b'",
            "TRUE AND (2 > 1) AND NOT 1 == 1 OR 'a' != 'b'",
            'height > 2',
            '2 > 1',
            'TRUE OR (2 > 1)',
            '((TRUE OR (2 > 1)) == (height > 2))',
            'NOT ((TRUE OR (2 > 1)) == (height > 2))',
            "TRUE AND (2 > 1) AND NOT 1 == 1 OR 'a' != 'b' OR NOT ((TRUE OR (2 > 1)) == (height > 2))"
        ]
        try:
            for code in ok_cases:
                self.assertTrue(self.parser.check_syntax(code))
        except:
            self.fail("Raised unexpected exception")

        ko_cases = [
            'TRU',
            'FLASE',
            'TRUE AN TRUE',
            'TRUE RO FALSE',
            'NO TRUE OR FALSE',
            'NOT FALSE AND NO FALSE',
            'TRUE O TRUE OR TRUE OR TRUE',
            '2 > 1)',
            'TRUE (2 > 1)',
            "'a != 'b'",
            "TRUE AND (2 >> 1) AND NOT 1 == 1 OR 'a' != 'b'",
            'height 2',
            '2 > 0 < 1',
            'TRUE O (2 > 1)',
            '(TRUE OR (2 > 1)) == (height > 2))',
            'NOT ((TRUE OR (2 > 1)) == height > 2))',
            "TRUE AND (2 > 1) AND NOT 1 == 1 OR 'a' != 'b' OR NOT ((TRUE OR (2 > 1)) == (height > 2)))"
        ]
        for code in ko_cases:
            with self.assertRaises(BooleySyntaxError):
                self.parser.check_syntax(code)

    def test_parser(self):
        parser = self.parser.get_boolean_binary_operation_parser()
        cases = [
            ('TRUE', True),
            ('TRUE AND TRUE', True),
            ('TRUE AND FALSE', False),
            ('TRUE OR FALSE', True),
            ('NOT TRUE OR FALSE', False),
            ('NOT FALSE AND NOT FALSE', True),
            ('TRUE OR TRUE OR TRUE OR TRUE', True),

            ('TRUE', True),
            ('(2 > 1)', True),
            ('TRUE AND (2 > 1)', True),

            ('1 == 1', True),
            ('NOT 1 == 1', False),

            ('1 = 1', True),
            ('NOT 1 = 1', False),

            ('TRUE AND (2 > 1) AND NOT 1 == 1', False),

            ("'a' != 'b'", True),

            ("TRUE AND (2 > 1) AND NOT 1 == 1 OR 'a' != 'b'", True),

            ('height > 2', False),
            ('2 > 1', True),
            ('TRUE OR (2 > 1)', True),
            ('((TRUE OR (2 > 1)) == (height > 2))', False),
            ('NOT ((TRUE OR (2 > 1)) == (height > 2))', True),

            ("TRUE AND (2 > 1) AND NOT 1 == 1 OR 'a' != 'b' OR NOT ((TRUE OR (2 > 1)) == (height > 2))", True)
        ]
        for case in cases:
            result = self.parser.parse(case[0])
            self.assertEqual(case[1], result, "In {0}".format(case[0]))

        ko_cases = [
            'TRU',
            'FLASE',
            'NO TRUE OR FALSE',
            'NOT FALSE AND NO FALSE',
            'NO 1 = 1',
        ]

        ko_cases = [
            'TRUE AN TRUE',
            'TRUE RO FALSE',
            'TRUE O TRUE OR TRUE OR TRUE',
            '2 > 1)',
            'TRUE (2 > 1)',
            "'a != 'b'",
            "TRUE AND (2 >> 1) AND NOT 1 == 1 OR 'a' != 'b'",
            'height 2',
            '2 > 0 < 1',
            'TRUE O (2 > 1)',
            '(TRUE OR (2 > 1)) == (height > 2))',
            'NOT ((TRUE OR (2 > 1)) == height > 2))',
            "TRUE AND (2 > 1) AND NOT 1 == 1 OR 'a' != 'b' OR NOT ((TRUE OR (2 > 1)) == (height > 2)))"
        ]
        for code in ko_cases:
            with self.assertRaises(BooleySyntaxError):
                self.parser.parse(code)

    def test_variable_starting_with_not(self):
        code = '''(Connecting_Future != "")\r\nAND\r\n(nota_marketing_digital != "")'''
        result = self.parser.parse(code, {u'Connecting_Future': u'1', u'nota_marketing_digital': u''})
        self.assertFalse(result)

    def test_in_operator(self):
        code = '''(Connecting_Future != "")\r\nAND\r\n(nota_marketing_digital != "")'''
        result = self.parser.parse(code, {u'Connecting_Future': u'1', u'nota_marketing_digital': u''})
        self.assertFalse(result)

        code = '''"apple" in fruits'''
        result = self.parser.parse(code, {u'fruits': [u'apple', u'banana']})
        self.assertTrue(result)

    def test_not_in_operator(self):
        code = '''"apple" not in fruits'''
        result = self.parser.parse(code, {u'fruits': [u'apple', u'banana']})
        self.assertFalse(result)

    def test_has_operator(self):
        code = '''fruits has "apple"'''
        result = self.parser.parse(code, {u'fruits': [u'apple', u'banana']})
        self.assertTrue(result)

    def test_not_has_operator(self):
        code = '''fruits not has "apple"'''
        result = self.parser.parse(code, {u'fruits': [u'apple', u'banana']})
        self.assertFalse(result)

    def test_starts_with(self):
        code = '''alpha starts with "abc"'''
        result = self.parser.parse(code, {u'alpha': "abcdefghijklmnopqrstuvwxyz"})
        self.assertTrue(result)

    def test_not_starts_swith(self):
        code = '''alpha not starts with "abc"'''
        result = self.parser.parse(code, {u'alpha': "abcdefghijklmnopqrstuvwxyz"})
        self.assertFalse(result)

    def test_ends_with(self):
        code = '''alpha ends with "xyz"'''
        result = self.parser.parse(code, {u'alpha': "abcdefghijklmnopqrstuvwxyz"})
        self.assertTrue(result)

    def test_not_ends_with(self):
        code = '''alpha not ends with "abc"'''
        result = self.parser.parse(code, {u'alpha': "abcdefghijklmnopqrstuvwxyz"})
        self.assertTrue(result)

    def test_slice(self):
        code = '''alpha[2:7] == "cdefg"'''
        result = self.parser.parse(code, {u'alpha': "abcdefghijklmnopqrstuvwxyz"})
        self.assertTrue(result)

    def test_dates(self):
        code = '''invoice_date == invoice_date_filter'''
        result = self.parser.parse(code, {u'invoice_date': "2012-08-05", u'invoice_date_filter': "2012-08-05"})
        self.assertTrue(result)

    def test_length_operator_with_string(self):
        code = '''"123456789" LENGTH IS 9'''
        result = self.parser.parse(code, {})
        self.assertTrue(result)

        code = '''"123456789" LENGTH IS NOT 19'''
        result = self.parser.parse(code, {})
        self.assertTrue(result)

    def test_length_operator_with_variable(self):
        code = '''name LENGTH IS 6'''
        result = self.parser.parse(code, {u'name': "Daniel"})
        self.assertTrue(result)

        code = '''name LENGTH IS NOT 16'''
        result = self.parser.parse(code, {u'name': "Daniel"})
        self.assertTrue(result)
