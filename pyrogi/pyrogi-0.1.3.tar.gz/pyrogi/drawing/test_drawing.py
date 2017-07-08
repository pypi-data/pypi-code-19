import unittest
from pyrogi.drawing import Color, LinearGradientPaint
from pyrogi.drawing.drawing import _parse_text_into_characters
from pyrogi.util import Vec2

class TestParseTextIntoCharacters(unittest.TestCase):
    def test_plain_characters(self):
        self.assertEqual(_parse_text_into_characters(''), [])
        self.assertEqual(_parse_text_into_characters('a'), ['a'])
        self.assertEqual(_parse_text_into_characters('ab'), ['a', 'b'])
        self.assertEqual(_parse_text_into_characters('abcdefghijk'), ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k'])
        self.assertEqual(_parse_text_into_characters('a b'), ['a', ' ', 'b'])
        self.assertEqual(_parse_text_into_characters('a b '), ['a', ' ', 'b', ' '])
        self.assertEqual(_parse_text_into_characters('a  b'), ['a', ' ', ' ', 'b'])

    def test_escape_characters(self):
        self.assertEqual(_parse_text_into_characters('\\\\'), ['\\'])
        self.assertEqual(_parse_text_into_characters('\\['), ['['])
        self.assertEqual(_parse_text_into_characters('\\]'), [']'])
        self.assertEqual(_parse_text_into_characters('oauhstt tot\\] ath'), ['o', 'a', 'u', 'h', 's', 't', 't', ' ', 't', 'o', 't', ']', ' ', 'a', 't', 'h'])
        self.assertEqual(_parse_text_into_characters('oauhstt to[t\\]] ath'), ['o', 'a', 'u', 'h', 's', 't', 't', ' ', 't', 'o', 't]', ' ', 'a', 't', 'h'])
        self.assertEqual(_parse_text_into_characters('oauhst[t t]o[t\\\\] ath'), ['o', 'a', 'u', 'h', 's', 't', 't t', 'o', 't\\', ' ', 'a', 't', 'h'])

        self.assertRaisesRegex(ValueError, "Invalid escape character 'a'.", _parse_text_into_characters, '\\a')
        self.assertRaisesRegex(ValueError, "Invalid escape character '8'.", _parse_text_into_characters, '\\8')
        self.assertRaisesRegex(ValueError, "Invalid escape character '8'.", _parse_text_into_characters, 'sntahoe a[ot]uhoa\\8 othuas')
        self.assertRaisesRegex(ValueError, "Invalid escape character '8'.", _parse_text_into_characters, 'sntahoe a[ot]uhoa[\\8] othuas')

        self.assertRaisesRegex(ValueError, "The '\\\\' at the end of the string isn't escaping anything.", _parse_text_into_characters, '\\')
        self.assertRaisesRegex(ValueError, "The '\\\\' at the end of the string isn't escaping anything.", _parse_text_into_characters, 'to[u]hats[ ][ot]out tat thot\\')

    def test_groups(self):
        self.assertEqual(_parse_text_into_characters('[a]'), ['a'])
        self.assertEqual(_parse_text_into_characters('[abcdefghijk]'), ['abcdefghijk'])
        self.assertEqual(_parse_text_into_characters('abc [def][hi]toh[oo]'), ['a', 'b', 'c', ' ', 'def', 'hi', 't', 'o', 'h', 'oo'])

        self.assertRaisesRegex(ValueError, 'You cannot end a character group that you have not started.', _parse_text_into_characters, ']')
        self.assertRaisesRegex(ValueError, 'You cannot end a character group that you have not started.', _parse_text_into_characters, 'tohut otuha]')
        self.assertRaisesRegex(ValueError, 'You cannot end a character group that you have not started.', _parse_text_into_characters, 'tou[ot][,,]ot<t   to[iho][otu]]')

        self.assertRaisesRegex(ValueError, 'You started a character group but did not finish it.', _parse_text_into_characters, '[')
        self.assertRaisesRegex(ValueError, 'You started a character group but did not finish it.', _parse_text_into_characters, '[otuh')
        self.assertRaisesRegex(ValueError, 'You started a character group but did not finish it.', _parse_text_into_characters, '[ otat')
        self.assertRaisesRegex(ValueError, 'You started a character group but did not finish it.', _parse_text_into_characters, '[o].4c,9sz[332] o,y092[')

        self.assertRaisesRegex(ValueError, 'You cannot start a character group within another group.', _parse_text_into_characters, '[[a]]')
        self.assertRaisesRegex(ValueError, 'You cannot start a character group within another group.', _parse_text_into_characters, '[35,.p[a] o]')
        self.assertRaisesRegex(ValueError, 'You cannot start a character group within another group.', _parse_text_into_characters, '[,tou]ou, ,[oot. o[ot. teo ]otu]')

        self.assertRaisesRegex(ValueError, 'You cannot have an empty character group.', _parse_text_into_characters, '[]')
        self.assertRaisesRegex(ValueError, 'You cannot have an empty character group.', _parse_text_into_characters, 'aeu[]')
        self.assertRaisesRegex(ValueError, 'You cannot have an empty character group.', _parse_text_into_characters, '[]ouu')
        self.assertRaisesRegex(ValueError, 'You cannot have an empty character group.', _parse_text_into_characters, 'aeaueu[]au')
        self.assertRaisesRegex(ValueError, 'You cannot have an empty character group.', _parse_text_into_characters, '[ateu,] otu,[ot,] ,0o[ote][oth,][][tout,t][out,][out,]')


class TestColor(unittest.TestCase):
    def test_to_tuple(self):
        self.assertEqual(Color(1, 2, 3, 4).to_RGB_tuple(), (1, 2, 3))
        self.assertEqual(Color(1, 2, 3, 4).to_RGBA_tuple(), (1, 2, 3, 4))
        self.assertEqual(Color(1, 2, 3).to_RGBA_tuple(), (1, 2, 3, 255))

    def test_equals(self):
        self.assertEqual(Color(1, 2, 3, 4), Color(1, 2, 3, 4))
        self.assertEqual(Color(1, 2, 3), Color(1, 2, 3, 255))

    def test_initialization_errors(self):
        self.assertRaisesRegex(ValueError, "A Color object cannot contain the float value '1.1'.", Color, 1.1, 2, 3, 4)
        self.assertRaisesRegex(ValueError, "A Color object cannot contain the float value '2.02'.", Color, 1, 2.02, 3, 4)
        self.assertRaisesRegex(ValueError, "A Color object cannot contain the float value '3.7'.", Color, 1, 2, 3.7, 4)
        self.assertRaisesRegex(ValueError, "A Color object cannot contain the float value '4.0'.", Color, 1, 2, 3, 4.0)

        self.assertRaisesRegex(ValueError, 'The parameters to a Color object must be in the range \\[0, 255\\].', Color, -1, 2, 3, 4)
        self.assertRaisesRegex(ValueError, 'The parameters to a Color object must be in the range \\[0, 255\\].', Color, 256, 2, 3, 4)
        self.assertRaisesRegex(ValueError, 'The parameters to a Color object must be in the range \\[0, 255\\].', Color, 1, -38, 3, 4)
        self.assertRaisesRegex(ValueError, 'The parameters to a Color object must be in the range \\[0, 255\\].', Color, 1, 300, 3, 4)
        self.assertRaisesRegex(ValueError, 'The parameters to a Color object must be in the range \\[0, 255\\].', Color, 1, 2, -3, 4)
        self.assertRaisesRegex(ValueError, 'The parameters to a Color object must be in the range \\[0, 255\\].', Color, 1, 2, 256, 4)
        self.assertRaisesRegex(ValueError, 'The parameters to a Color object must be in the range \\[0, 255\\].', Color, 1, 2, 3, -1)
        self.assertRaisesRegex(ValueError, 'The parameters to a Color object must be in the range \\[0, 255\\].', Color, 1, 2, 3, 500)


class TestPaints(unittest.TestCase):
    def test_linear_gradient(self):
        self._run_linear_gradient_test(
            Color(0, 0, 0, 0), Vec2(0, 0),
            Color(255, 255, 255, 255), Vec2(10, 0),
            Vec2(5, 0), Vec2(5, 0),
            Color(128, 128, 128, 128), Color(128, 128, 128, 128), Color(128, 128, 128, 128), Color(128, 128, 128, 128)
        )
        self._run_linear_gradient_test(
            Color(0, 0, 0, 0), Vec2(0, 0),
            Color(255, 255, 255, 255), Vec2(10, 0),
            Vec2(-2, 0), Vec2(-2, 0),
            Color(51, 51, 51, 51), Color(0, 0, 0, 0), Color(51, 51, 51, 51), Color(0, 0, 0, 0)
        )
        self._run_linear_gradient_test(
            Color(0, 0, 0, 0), Vec2(0, 0),
            Color(255, 255, 255, 255), Vec2(10, 0),
            Vec2(8, 0), Vec2(8, 0),
            Color(204, 204, 204, 204), Color(204, 204, 204, 204), Color(204, 204, 204, 204), Color(204, 204, 204, 204)
        )

        self._run_linear_gradient_test(
            Color(0, 0, 0, 0), Vec2(0, 0),
            Color(255, 255, 255, 255), Vec2(10, 0),
            Vec2(10.5, 0), Vec2(10.5, 0),
            Color(242, 242, 242, 242), Color(255, 255, 255, 255), Color(242, 242, 242, 242), Color(255, 255, 255, 255)
        )
        self._run_linear_gradient_test(
            Color(0, 0, 0, 0), Vec2(0, 0),
            Color(255, 255, 255, 255), Vec2(3, 0),
            Vec2(6, 0), Vec2(6, 0),
            Color(0, 0, 0, 0), Color(255, 255, 255, 255), Color(0, 0, 0, 0), Color(255, 255, 255, 255)
        )

        self._run_linear_gradient_test(
            Color(87, 105, 202, 7), Vec2(0, 0),
            Color(230, 188, 12, 38), Vec2(0, 10),
            Vec2(0, 5), Vec2(0, -5),
            Color(158, 146, 107, 22), Color(158, 146, 107, 22), Color(158, 146, 107, 22), Color(87, 105, 202, 7)
        )
        self._run_linear_gradient_test(
            Color(99, 180, 39, 222), Vec2(0, -5),
            Color(0, 60, 120, 205), Vec2(0, 5),
            Vec2(-2, 3), Vec2(193, -7),
            Color(20, 84, 104, 208), Color(20, 84, 104, 208), Color(79, 156, 55, 219), Color(99, 180, 39, 222)
        )

        self._run_linear_gradient_test(
            Color(0, 0, 0, 0), Vec2(1, 6),
            Color(255, 255, 255, 255), Vec2(3, 17.2),
            Vec2(2, 15), Vec2(0.5, 5),
            Color(203, 203, 203, 203), Color(203, 203, 203, 203), Color(24, 24, 24, 24), Color(0, 0, 0, 0)
        )
        self._run_linear_gradient_test(
            Color(0, 0, 0, 0), Vec2(1, 6),
            Color(255, 255, 255, 255), Vec2(3, 17.2),
            Vec2(4, 23), Vec2(-2, -7),
            Color(123, 123, 123, 123), Color(255, 255, 255, 255), Color(211, 211, 211, 211), Color(0, 0, 0, 0)
        )
        self._run_linear_gradient_test(
            Color(0, 0, 0, 0), Vec2(1, 6),
            Color(255, 255, 255, 255), Vec2(3, 17.2),
            Vec2(6, 30), Vec2(-4.5, -100),
            Color(39, 39, 39, 39), Color(255, 255, 255, 255), Color(190, 190, 190, 190), Color(0, 0, 0, 0)
        )
        self._run_linear_gradient_test(
            Color(0, 0, 0, 0), Vec2(1.2, 12.9),
            Color(255, 255, 255, 255), Vec2(30.8, 3.05),
            Vec2(162.7, -40.7), Vec2(-201.5, 195.2),
            Color(139, 139, 139, 139), Color(255, 255, 255, 255), Color(3, 3, 3, 3), Color(0, 0, 0, 0)
        )

        self._run_linear_gradient_test(
            Color(250, 29, 1, 167), Vec2(-7, 2),
            Color(88, 44, 222, 111), Vec2(4, 17.9),
            Vec2(28.8, -193.3), Vec2(-33.9, -2),
            Color(129, 40, 166, 125), Color(250, 29, 1, 167), Color(94, 43, 214, 113), Color(250, 29, 1, 167)
        )
        self._run_linear_gradient_test(
            Color(3, 7, 159, 209), Vec2(-7, 2),
            Color(109, 0, 200, 183), Vec2(4, -10.4),
            Vec2(3.4, 7), Vec2(-8.3, -17),
            Color(23, 6, 167, 204), Color(23, 6, 167, 204), Color(88, 1, 192, 188), Color(88, 1, 192, 188)
        )
        self._run_linear_gradient_test(
            Color(67, 29, 252, 67), Vec2(-7, 2),
            Color(90, 174, 39, 105), Vec2(-20.3, 12),
            Vec2(-30, 200.5), Vec2(28.8, -77.7),
            Color(73, 69, 194, 77), Color(90, 174, 39, 105), Color(81, 116, 125, 90), Color(67, 29, 252, 67)
        )
        self._run_linear_gradient_test(
            Color(29, 189, 75, 253), Vec2(-7, 2),
            Color(109, 0, 200, 183), Vec2(-20.3, -10.4),
            Vec2(-100, 0.4), Vec2(2.3, 23),
            Color(45, 151, 100, 239), Color(109, 0, 200, 183), Color(96, 31, 180, 194), Color(29, 189, 75, 253)
        )

    def _run_linear_gradient_test(
            self, color1, position1, color2, position2,
            relative_position, absolute_position,
            t_t_expected_color, f_t_expected_color, t_f_expected_color, f_f_expected_color):
        for pair in [(t_t_expected_color, (True, True)), (f_t_expected_color, (False, True)), (t_f_expected_color, (True, False)), (f_f_expected_color, (False, False))]:
            expected_color = pair[0]
            is_cyclical = pair[1][0]
            is_relative = pair[1][1]
            # test positions/colors in given order
            gradient = LinearGradientPaint(color1, position1, color2, position2, is_cyclical, is_relative)
            self._assertColorsEqual(gradient.get_tile_color(relative_position, absolute_position), expected_color)
            # test positions/colors in reverse order
            gradient = LinearGradientPaint(color2, position2, color1, position1, is_cyclical, is_relative)
            self._assertColorsEqual(gradient.get_tile_color(relative_position, absolute_position), expected_color)

    def _assertColorsEqual(self, color1, color2):
        self.assertEqual(color1.r, color2.r)
        self.assertEqual(color1.g, color2.g)
        self.assertEqual(color1.b, color2.b)
        self.assertEqual(color1.a, color2.a)
