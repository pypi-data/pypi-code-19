import unittest
from pyrogi import Screen, Backend
from pyrogi.util import Vec2

class TestScreen(Screen):
    pass

class TestBackend(unittest.TestCase):
    def test_screens(self):
        backend = Backend(Vec2(0, 0), Vec2(0, 0), '')
        self.assertEqual(len(backend.screens), 0)

        backend.set_screen(TestScreen())
        self.assertEqual(len(backend.screens), 1)

        backend.set_screen(TestScreen())
        self.assertEqual(len(backend.screens), 2)

        backend.go_back_n_screens(1)
        self.assertEqual(len(backend.screens), 1)

        backend.set_screen(TestScreen())
        self.assertEqual(len(backend.screens), 2)

        backend.go_back_n_screens(2)
        self.assertEqual(len(backend.screens), 0)
