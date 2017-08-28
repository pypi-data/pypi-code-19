import unittest
from pyadf.inline_nodes.emoji import Emoji

class DocumentTests(unittest.TestCase):
    
    def test_emoji_with_all_details(self):
        emoji = Emoji(':shortname:', emoji_id='123', fallback='fallback')
        doc = emoji.to_doc()
        self.assertEqual(doc, {
            'type': 'emoji',
            'attrs': {
                'shortname': ':shortname:',
                'fallback': 'fallback',
                'id': '123'
            }
        })

    def test_emoji_with_no_fallback(self):
        emoji = Emoji(':shortname:', emoji_id='123')
        doc = emoji.to_doc()
        self.assertEqual(doc, {
            'type': 'emoji',
            'attrs': {
                'shortname': ':shortname:',
                'id': '123'
            }
        })

    def test_emoji_with_no_fallback_no_id(self):
        emoji = Emoji(':shortname:')
        doc = emoji.to_doc()
        self.assertEqual(doc, {
            'type': 'emoji',
            'attrs': {
                'shortname': ':shortname:'
            }
        })

if __name__ == '__main__':
    unittest.main()