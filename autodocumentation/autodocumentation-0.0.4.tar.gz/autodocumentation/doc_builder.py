#coding: utf8
import logging
import re

from jinja2.environment import Template

from autodocumentation.compat import to_unicode, to_string
from autodocumentation.util import add_prefix_to_lines

LOGGER = logging.getLogger("autodoc")

TEMPLATE = """{% for call in calls %}* {{call.comment or "Пример запроса"}}
    Request::

        {{call.method}} {{call.url}}
{{add_prefix_to_lines("        ", call.headers)}}

{{add_prefix_to_lines("        ", call.body)}}

    Response::

{{add_prefix_to_lines("        ", call.response)}}
{% endfor %}"""

FUNCTION_TEMPLATE = """{% for call in calls %}* {{call.comment or "Пример запроса"}}::

    Функция {{call.name}}
    Вызвана с параметрами:
    {% for key, value in call.arguments %}
    * {{key}}: {{value}}{% endfor %}

    Ответ: {{call.output}}
{% endfor %}"""

class DocBuilder(object):

    writer = None   #type: FlaskRequestWriter
    template = None

    def __init__(self, limit=3, template=TEMPLATE):
        self.template = template
        self.limit = limit

    def add_doc(self, func):
        calls = self.writer.get_calls(func)[:self.limit]

        try:
            func.__doc__ = self._modify_docstring(
                to_unicode(func.__doc__), calls
            )
        except:
            LOGGER.exception("Can't build autodoc for func %s", func)

    def _modify_docstring(self, doc, calls):
        examplesPart = Template(to_unicode(self.template))

        pattern = r"([\t ]+)\<examples\>"
        space = re.findall(pattern, doc)[0]

        rendered = add_prefix_to_lines(space, examplesPart.render(
            calls=calls,
            add_prefix_to_lines=add_prefix_to_lines,
            space=space
        ))

        return re.sub(pattern, to_string(rendered), to_string(doc), count=1)