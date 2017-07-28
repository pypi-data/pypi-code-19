import os

import jinja2
import yaml


class YAMLTestCase(object):
    def render_template(self, name, context=None):
        if context is None:
            context = {}
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
        )
        template = env.get_template(name, context)
        return template.render(context)

    def thenYAMLShouldBeEqual(self, template, result, message, template_context=None):
        expected_result = self.render_template(template, template_context)
        yaml_expected = yaml.load(expected_result)
        yaml_computed = yaml.load(result)
        self.assertEqual(yaml_expected, yaml_computed, message)
