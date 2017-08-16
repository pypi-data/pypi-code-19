# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sphinx_rtd_theme

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]
napoleon_google_docstring = True
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = 'brent-search'
copyright = '2016, Danilo Horta'
author = 'Danilo Horta'
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = False
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
htmlhelp_basename = 'brent-searchdoc'
latex_elements = {}
latex_documents = [
    (master_doc, 'brent-search.tex', 'brent-search Documentation',
     'Danilo Horta', 'manual'),
]
man_pages = [(master_doc, 'brent-search', 'brent-search Documentation',
              [author], 1)]
texinfo_documents = [
    (master_doc, 'brent-search', 'brent-search Documentation', author,
     'brent-search', 'One line description of project.', 'Miscellaneous'),
]
intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'numpy': ('http://docs.scipy.org/doc/numpy/', None)
}
