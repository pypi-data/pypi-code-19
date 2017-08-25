from unittest import TestCase

from zekeconv import utl

class TestUtl(TestCase):
    def test_unpack_key(self):
        self.assertEquals(utl.unpack_key("ex", "ex", "/parent/"),
                          "/parent")
        self.assertEquals(utl.unpack_key("ex", "ex/path/to", "/parent/"),
                          "/parent/path/to")
        self.assertEquals(utl.unpack_key("ex", "ex/path/to", "/"),
                          "/path/to")
        self.assertEquals(utl.unpack_key("ex", "ex", "/"),
                          "/")
        self.assertEquals(utl.unpack_key("ex", "ex/path/to", None),
                          "/path/to")
        self.assertEquals(utl.unpack_key("ex", "ex", None),
                          None)
        # TODO: test invalid input

    def test_strip_trailing(self):
        self.assertEquals(utl.strip_trailing("", ""),          "")
        self.assertEquals(utl.strip_trailing("", "/"),         "")
        self.assertEquals(utl.strip_trailing("abc", ""),       "abc")
        self.assertEquals(utl.strip_trailing("abc", "/"),      "abc")
        self.assertEquals(utl.strip_trailing("abc/", "/"),     "abc")
        self.assertEquals(utl.strip_trailing("abc///", "/"),   "abc")
        self.assertEquals(utl.strip_trailing("abc////", "/"),  "abc")
        self.assertEquals(utl.strip_trailing("abc///", "//"),  "abc/")
        self.assertEquals(utl.strip_trailing("abc////", "//"), "abc")

    def test_strip_trailing_once(self):
        self.assertEquals(utl.strip_trailing_once("", ""),            "")
        self.assertEquals(utl.strip_trailing_once("", "\n"),          "")
        self.assertEquals(utl.strip_trailing_once("abc", "\n"),       "abc")
        self.assertEquals(utl.strip_trailing_once("abc", ""),         "abc")
        self.assertEquals(utl.strip_trailing_once("abc\n", ""),       "abc\n")
        self.assertEquals(utl.strip_trailing_once("abc\n", "\n"),     "abc")
        self.assertEquals(utl.strip_trailing_once("abc\n\n", "\n"),   "abc\n")
        self.assertEquals(utl.strip_trailing_once("abc\n\n\n", "\n"), "abc\n\n")
        self.assertEquals(utl.strip_trailing_once("abc---", "--"),    "abc-")

    def test_pack_value(self):
        txt = "simple ascii value"
        self.assertEquals(utl.pack_value(txt),          txt)
        self.assertEquals(utl.pack_value(txt + "\n"),   txt)
        self.assertEquals(utl.pack_value(txt + "\n\n"), txt + "\n")
        
        
        #self.assertEquals(utl.pack_value(utf),          utf)
        
        b64 = "base64:3q2+7w=="
        bin = "\xDE\xAD\xBE\xEF"
        self.assertEquals(utl.pack_value(bin),          b64)

    def test_unpack_value(self):
        txt = "simple ascii value"
        self.assertEquals(utl.unpack_value(txt),        txt + "\n")
        self.assertEquals(utl.unpack_value(txt + "\n"), txt + "\n\n")
        
        b64 = "base64:3q2+7w=="
        bin = "\xDE\xAD\xBE\xEF"
        self.assertEquals(utl.unpack_value(b64),        bin)
        self.assertEquals(utl.unpack_value(b64 + "\n"), bin)

    def test_pack_unpack_idempotence(self):
        # ascii value as it came from zeke dump
        zk_txt = "simple ascii value"
        self.assertEquals(utl.pack_value(utl.unpack_value(zk_txt)), zk_txt)
        
        # ascii value as extracted into file (with \n for convenient editing)
        fs_txt = zk_txt + "\n"
        self.assertEquals(utl.unpack_value(utl.pack_value(fs_txt)), fs_txt)
        
        # binary data as it came from zeke dump (base64-encoded, with prefix)
        zk_bin = "base64:3q2+7w=="
        self.assertEquals(utl.pack_value(utl.unpack_value(zk_bin)), zk_bin)
        
        # binary data as extracted into file (raw bytes, without \n)
        fs_bin = "\xDE\xAD\xBE\xEF"
        self.assertEquals(utl.unpack_value(utl.pack_value(fs_bin)), fs_bin)

    def test_strip_source_subpath(self):
         self.assertEquals(utl.strip_source_subpath("/some/key", "/"),
                           "some/key")
         self.assertEquals(utl.strip_source_subpath("/some/key", None),
                           "some/key")
         self.assertEquals(utl.strip_source_subpath("/some/key", "/some/"),
                           "key")
         # TODO: test invalid input

    def test_key_filename(self):
        # note: key is assumed to be "relative", with source part stripped
        # TODO: test invalid input
        self.assertEquals(utl.key_filename("", None),
                          "root.txt")
        self.assertEquals(utl.key_filename("", "/"),
                          "root.txt")
        self.assertEquals(utl.key_filename("key", None),
                          "key.txt")
        self.assertEquals(utl.key_filename("path/to/key", None),
                          "path-to-key.txt")
        self.assertEquals(utl.key_filename("", "/source"),
                          "source.txt")
        self.assertEquals(utl.key_filename("", "/nested/source"),
                          "source.txt")
        self.assertEquals(utl.key_filename("key", "/source"),
                          "key.txt")
        self.assertEquals(utl.key_filename("path/to/key", "/source"),
                          "path-to-key.txt")
        self.assertEquals(utl.key_filename("path/to/key", "/nested/source"),
                          "path-to-key.txt")

    def test_preprocess_source_subpath(self):
        self.assertEquals(utl.preprocess_source_subpath(None), None)
        self.assertEquals(utl.preprocess_source_subpath(""), None)
        self.assertEquals(utl.preprocess_source_subpath("////"), "/")
        self.assertEquals(utl.preprocess_source_subpath("/src"), "/src/")
        self.assertEquals(utl.preprocess_source_subpath("/src/"), "/src/")
        self.assertEquals(utl.preprocess_source_subpath("/from/src"),
                          "/from/src/")
        self.assertEquals(utl.preprocess_source_subpath("/from/src/"),
                          "/from/src/")
        self.assertEquals(utl.preprocess_source_subpath("/from/src//"),
                          "/from/src/")

    def test_unpack_pair(self):
        self.assertEquals(utl.unpack_pair('["/key", "value"]'),
                          ("/key", "value"))
        self.assertRaises(ValueError, utl.unpack_pair, '[]')
        self.assertRaises(ValueError, utl.unpack_pair, 'text')
        self.assertRaises(ValueError, utl.unpack_pair, '{"/key": "value"}')
        self.assertRaises(ValueError, utl.unpack_pair, '["/key", "value", "x"]')
