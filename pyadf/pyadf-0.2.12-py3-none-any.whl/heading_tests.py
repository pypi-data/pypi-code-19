import unittest
from pyadf.heading import Heading

class HeadingTests(unittest.TestCase):

    def test_heading_with_full_mention(self):
        heading = Heading(2).mention('mention_id', 'mention_text', access_level='NONE')
        doc = heading.to_doc()

        self.assertEqual(doc, {
            'type': 'heading',
            'attrs': {
                'level': 2
            },
            'content': [{
                'type': 'mention',
                'attrs': {
                    'id': 'mention_id',
                    'text': 'mention_text',
                    'access_level': 'NONE'
                }
            }]
        })

if __name__ == '__main__':
    unittest.main()