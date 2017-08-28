import unittest
from pyadf.block_quote import BlockQuote

class DocumentTests(unittest.TestCase):
    
    def test_empty_block_quote(self):
        quote = BlockQuote().to_doc()

        self.assertEqual(quote, {
            'type': 'blockquote',
            'content': []
        })

    def test_block_quote_with_text(self):
        quote = BlockQuote()  \
            .text('Hi there') \
            .to_doc()
        
        self.assertEqual(quote, {
            'type': 'blockquote',
            'content': [{
                'type': 'text',
                'text': 'Hi there'
            }]
        })

    def test_block_quote_with_emoji(self):
        quote = BlockQuote()  \
            .emoji(':smile:', emoji_id='123', fallback='fallback') \
            .to_doc()
        
        self.assertEqual(quote, {
            'type': 'blockquote',
            'content': [{
                'type': 'emoji',
                'attrs': {
                    'shortname': ':smile:',
                    'fallback': 'fallback',
                    'id': '123'
                }
            }]
        })



if __name__ == '__main__':
    unittest.main()