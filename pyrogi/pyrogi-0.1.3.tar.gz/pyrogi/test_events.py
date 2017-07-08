import unittest
import pyrogi
from pyrogi.util import Vec2
from pyrogi.events import _pixel_position_to_tile_position

class TestPixelToTileConversion(unittest.TestCase):
    def setUp(self):
        pyrogi.Backend(Vec2(100, 100), Vec2(2, 5), '')

    def test_pixel_position_to_tile_position(self):
        self.assertEqual(_pixel_position_to_tile_position(Vec2(0, 0)), Vec2(0, 0))
        self.assertEqual(_pixel_position_to_tile_position(Vec2(1, 0)), Vec2(0, 0))
        self.assertEqual(_pixel_position_to_tile_position(Vec2(1, 1)), Vec2(0, 0))
        self.assertEqual(_pixel_position_to_tile_position(Vec2(1.99, 4.99)), Vec2(0, 0))

        self.assertEqual(_pixel_position_to_tile_position(Vec2(2, 5)), Vec2(1, 1))
        self.assertEqual(_pixel_position_to_tile_position(Vec2(2.1, 5.1)), Vec2(1, 1))
        self.assertEqual(_pixel_position_to_tile_position(Vec2(3.999, 9.999)), Vec2(1, 1))

        self.assertEqual(_pixel_position_to_tile_position(Vec2(30, 3)), Vec2(15, 0))
        self.assertEqual(_pixel_position_to_tile_position(Vec2(5, 17)), Vec2(2, 3))
