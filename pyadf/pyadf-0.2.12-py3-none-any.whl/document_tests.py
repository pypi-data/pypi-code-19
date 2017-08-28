import unittest
from pyadf.document import Document

class DocumentTests(unittest.TestCase):

    def test_empty_document(self):
        document = Document()
        doc = document.to_doc()
        self.assertEqual(doc, {
                'version': 1,
                'type': 'doc',
                'content': []
            })

    def test_document_with_empty_paragraph(self):
        document = Document()
        document.paragraph()
        doc = document.to_doc()
        self.assertEqual(doc, {
            'version': 1,
            'type': 'doc',
            'content': [{
                'type': 'paragraph',
                'content': []
            }]
        })

    def test_document_with_text_in_paragraph(self):
        document = Document()
        document.paragraph().text('Hello world')
        doc = document.to_doc()
        self.assertEqual(doc, {
            'version': 1,
            'type': 'doc',
            'content': [{
                'type': 'paragraph',
                'content': [{
                    'type': 'text',
                    'text': 'Hello world'
                }]
            }]
        })

    def test_document_with_text_in_paragraph_fluent_api(self):
        document = Document()        \
            .paragraph()             \
                .text('Hello world') \
            .end()
        
        doc = document.to_doc()
        self.assertEqual(doc, {
            'version': 1,
            'type': 'doc',
            'content': [{
                'type': 'paragraph',
                'content': [{
                    'type': 'text',
                    'text': 'Hello world'
                }]
            }]
        })

    def test_document_with_multiple_text_nodes(self):
        doc = Document()        \
            .paragraph()             \
                .text('Hello world') \
                .text('How are you') \
            .end()                   \
            .to_doc()

        self.assertEqual(doc, {
            'version': 1,
            'type': 'doc',
            'content': [{
                'type': 'paragraph',
                'content': [{
                    'type': 'text',
                    'text': 'Hello world'
                }, {
                    'type': 'text',
                    'text': 'How are you'
                }]
            }]
        })

if __name__ == '__main__':
    unittest.main()