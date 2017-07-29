from unittest import TestCase

from pypathutil import common


class Foo(TestCase):
    def test_add_basic(self):
        result = common.add(
            path="/etc:/var",
            folder="/tmp",
            head=True,
        )
        self.assertEqual(result, "/tmp:/etc:/var")

    def test_add_head_clean_path(self):
        result = common.add(
            path="/non:/var",
            folder="/tmp",
            head=True,
        )
        self.assertEqual(result, "/tmp:/var")

    def test_add_head_clean_folder(self):
        result = common.add(
            path="/etc:/var",
            folder="/non",
            head=True,
        )
        self.assertEqual(result, "/etc:/var")

    def test_add_head_empty_path(self):
        result = common.add(
            path="",
            folder="/etc",
            head=True,
        )
        self.assertEqual(result, "/etc")

    def test_add_head_empty_path_empty_folder(self):
        result = common.add(
            path="",
            folder="",
            head=True,
        )
        self.assertEqual(result, "")

    def test_add_head_existing(self):
        result = common.add(
            path="/var:/tmp",
            folder="/tmp",
            head=True,
        )
        self.assertEqual(result, "/tmp:/var")

    def test_add_tail_existing(self):
        result = common.add(
            path="/var:/tmp",
            folder="/var",
            head=False,
        )
        self.assertEqual(result, "/tmp:/var")

    def test_add_head_no_clean(self):
        result = common.add(
            path="/a:/b",
            folder="/c",
            remove_non_folders=False,
            head=True,
        )
        self.assertEqual(result, "/c:/a:/b")
