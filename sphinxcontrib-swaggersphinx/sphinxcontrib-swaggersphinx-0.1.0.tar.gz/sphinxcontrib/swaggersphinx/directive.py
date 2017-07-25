import json
import os
import traceback
import urllib.request

from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives


nodes.Node.__enter__ = lambda self: self
nodes.Node.__exit__ = lambda self, exc_type, exc_val, exc_tb: None


class SwaggerDirective(Directive):
    required_arguments = 1
    has_content = True
    param_headers = ('Name', 'Type', 'Description', 'Data Type')
    col_widths = (1, 1, 3, 1)

    def cell(self, text):
        return nodes.entry('', nodes.paragraph(text=text))

    def row(self, items):
        return nodes.row('', *[self.cell(text) for text in items])

    @staticmethod
    def get_type(param):
        paramtype = param.get('type', '')
        if paramtype == 'array':
            item_type = param.get('items', {}).get('type', '')
            paramtype = 'array({})'.format(item_type)
        return paramtype

    def get_param_rows(self, parameters):
        for param in parameters:
            if param.get('in') == 'body':
                continue
            cols = (
                param.get('name', ''),
                param.get('in', ''),
                param.get('description', ''),
                self.get_type(param),
            )
            yield self.row(cols)

    def get_body_rows(self, parameters):
        for param in parameters:
            if param.get('in') != 'body':
                continue
            schema = param.get('schema', {})
            for name, bodyparam in schema.get('properties', {}).items():
                description = bodyparam.get('description', '')
                if name in schema.get('required', ()):
                    description = 'Required. ' + description
                cols = (
                    name,
                    'body',
                    description,
                    self.get_type(bodyparam),
                )
                yield self.row(cols)

    def create_param_table(self, parameters):
        with nodes.table() as tbl:
            with nodes.tgroup(cols=len(self.param_headers)) as tgroup:
                tbl.append(tgroup)
                tgroup.extend(nodes.colspec(colwidth=x) for x in self.col_widths)

                with nodes.thead() as thead:
                    tgroup.append(thead)
                    thead.append(self.row(self.param_headers))

                with nodes.tbody() as tbody:
                    tgroup.append(tbody)
                    tbody.extend(self.get_param_rows(parameters))
                    tbody.extend(self.get_body_rows(parameters))

                    if not len(tbody):
                        tbody.append(self.row(['None', '', '', '']))

            return tbl

    def process_swagger(self, data):
        prev_section = None

        for path, methods in data['paths'].items():
            section = path.strip('/').split('/', 1)[0]
            if section != prev_section:
                with nodes.section(ids=[section]) as secheader:
                    secheader.append(nodes.title(text=section))
                yield secheader
            prev_section = section

            for method, options in methods.items():
                ptext = '{} {}'.format(method.upper(), path)
                cssid = '{}{}'.format(method, path.replace('/', '-'))

                with nodes.paragraph(ids=cssid) as paragraph:
                    with nodes.literal() as literal:
                        paragraph.append(literal)
                        literal.append(nodes.strong(text=ptext))
                    yield paragraph

                parameters = options.get('parameters', ())
                yield self.create_param_table(parameters)

    def get_full_path(self, path):
        source = self.state_machine.input_lines.source(self.lineno - self.state_machine.input_offset - 1)
        source_dir = os.path.dirname(os.path.abspath(source))
        return os.path.normpath(os.path.join(source_dir, path))

    def open_from_url(self, path):
        with urllib.request.urlopen(path) as response:
            return response.read()

    def open_from_file(self, path):
        with open(path, 'r') as handle:
            return handle.read()

    def run(self):
        full_path = None
        try:
            path = directives.path(self.arguments[0])
            if path.startswith('http://') or path.startswith('https://'):
                full_path = path
                data = self.open_from_url(full_path)
            else:
                full_path = self.get_full_path(path)
                data = self.open_from_file(full_path)
            return list(self.process_swagger(json.loads(data)))
        except Exception as exc:
            traceback.print_exc()
            with nodes.error('') as error:
                error.append(nodes.paragraph(text=str(exc)))
                error.append(nodes.paragraph(text='Make sure the path to the swagger JSON file is correct:'))
                error.append(nodes.paragraph(text=full_path))
            return [error]
