import os.path

from django.template import TemplateDoesNotExist

from xtc import TemplateTestCase


class BasicTestCase(TemplateTestCase):
    def test_simple(self):
        self.assertTemplateEqual('simple.html', save=True)

    def test_reset(self):
        self.template_context['one'] = 'value'
        self.reset_template_context()
        with self.assertRaises(KeyError):
            print(self.template_context['one'])

    def test_context(self):
        self.reset_template_context()
        self.template_context['planet'] = 'earth'
        self.assertTemplateEqual('context.html', save=True)

    def test_render_template_save_false(self):
        self.reset_template_context()
        self.cleanActualDir()
        output, path = self.render_template(
            'context.html', extra={'planet': 'earth'}
        )
        self.assertIsNone(path)
        self.assertPathNotExists(
            os.path.join(self._actual_dir, 'context.html')
        )
        with open(os.path.join(self._expect_dir, 'context.html')) as f:
            expect = f.read()
            f.close()

        self.assertEqual(expect.strip(), output.strip())

    def test_syntax_error(self):
        with self.assertSyntaxError():
            self.render_template('syntax.html')

    def test_dir_filled(self):
        self.assertDirNotEmpty(self._source_dir)

    def test_no_source_template(self):
        with self.assertRaises(TemplateDoesNotExist):
            self.assertTemplateEqual('nonexistent.html')


class ClassAttributeTestCase(TemplateTestCase):
    template_test_dir = os.path.join(
        os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'templates'
    )

    def test_simple(self):
        self.assertTemplateEqual('simple.html')
