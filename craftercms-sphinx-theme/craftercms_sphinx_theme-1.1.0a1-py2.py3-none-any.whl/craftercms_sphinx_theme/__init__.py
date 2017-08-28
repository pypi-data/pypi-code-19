"""Sphinx theme for CrafterCMS docs.

From https://github.com/rart/craftercms-sphinx-theme.

"""
import os
from os import path

__version__ = '1.1.0.a1'
__version_full__ = __version__

def get_html_theme_path():
    """Return list of HTML theme paths."""
    cur_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    return cur_dir

def setup(app):
    app.add_html_theme('craftercms_sphinx_theme', path.abspath(path.dirname(__file__)))
