"""Defines the JekyllMarkdownExporter class."""
from nbconvert.exporters.markdown import MarkdownExporter
import os.path as op
from traitlets import default

__version__ = "0.1"


class JekyllMarkdownExporter(MarkdownExporter):
    """
    Convert Jupyter Notebooks into JekyllMarkdown syntax.

    Defines an ``nbconvert`` class that will convert Jupyter Notebooks into
    a Markdown flavor that works with Jekyll. Currently all this does is
    wrap input / output cells with some divs that let you style them however
    you wish.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the exporter."""
        super(JekyllMarkdownExporter, self).__init__(*args, **kwargs)
        path_templates = op.join(op.dirname(__file__), 'templates')
        self.template_path.append(path_templates)

    @default('template_file')
    def _template_file_default(self):
        return 'jekyllmarkdown'
