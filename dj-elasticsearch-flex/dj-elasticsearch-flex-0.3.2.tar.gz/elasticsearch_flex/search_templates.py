import elasticsearch
import json
import logging
import os
import re
import six

logger = logging.getLogger(__name__)


@six.python_2_unicode_compatible
class SearchTemplate(object):
    '''Partial Search Templates

    Wrapper for lower level Search Templates stored as mustache templates in
    elasticsearch cluster.

    A template is a `json` file containing the elasticsearch query with
    placeholders for parameters passed during the queries. It is possible to
    also optionally specify a `script` file name, which is inlined before
    it is registered in elasticsearch.

    To specify the `script`, use the following substitution:

            "field": "#[filename]",
    '''

    def __init__(self, name, filepath):
        self.name = name
        self.template = self._prerender(filepath)

    def register(self, index):
        c = index.get_connection()
        try:
            c.put_template(self.name, self.template)
            logger.info('Registered template %s', self)
        except elasticsearch.TransportError:
            logger.exception('Error while attempting to PUT template <%s>', self.name)
            raise

    def unregister(self, index):
        c = index.get_connection()
        c.delete_template(self.name)

    def _prerender(self, filepath):
        file_abspath = os.path.abspath(filepath)
        file_dir = os.path.dirname(file_abspath)
        with open(filepath, 'r') as fp:
            content = json.load(fp)

        # Recurse and look for a #[filename] pattern and load that file.
        def interpolate(dat):
            if type(dat) is dict:
                return {k: interpolate(v) for k, v in dat.items()}
            elif type(dat) is list:
                return [interpolate(x) for x in dat]
            elif type(dat) is six.text_type:
                matches = re.match(r'#\[(.+)\]', dat)
                if matches is not None:
                    script_name = matches.group(1)
                    script_file = os.path.join(file_dir, '{}.java'.format(script_name))
                    with open(script_file, 'r') as fp:
                        script = fp.read()
                        # XXX: Very cheap Java code "minification".
                        # It looks for spaces and tab marks in the beginning
                        # and end of the string, and replaces them with a single
                        # space.
                        # This is not robust and will fail for multi-line
                        # strings which want to preserve the spaces, however
                        # in our use case, we probably won't need that.
                        # In any case, this can use a rewrite.
                        return re.sub(r'^[ \t]+|\s+$', ' ', script, flags=re.M)
            return dat

        prerendered = interpolate(content)
        body = json.dumps(prerendered)

        # We need to fix the above (valid) json to cater for being a template
        # Remove the quotes around the json props.
        body = (body
                .replace('"{{#toJson}}', "{{#toJson}}")
                .replace('{{/toJson}}"', '{{/toJson}}'))
        return json.dumps(dict(template=body))

    def __repr__(self):
        return '<{0} name={1}>'.format(self.__class__.__name__, self.name)

    def __str__(self):
        return repr(self)
