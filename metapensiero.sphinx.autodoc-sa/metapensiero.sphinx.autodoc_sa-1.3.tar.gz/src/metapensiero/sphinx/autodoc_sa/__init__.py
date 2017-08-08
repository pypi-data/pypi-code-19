# -*- coding: utf-8 -*-
# :Project:   metapensiero.sphinx.autodoc_sa -- Pretty print canned SQLAlchemy statements
# :Created:   mar 11 ago 2015 11:44:44 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2015, 2016, 2017 Lele Gaifax
#

from sphinx.ext import autodoc
from sqlalchemy.sql import ClauseElement
from sqlalchemy.orm import Query


try:
    from sqlparse import format as sqlparse_format
except ImportError:
    sqlparse_prettifier = None
else:
    def sqlparse_prettifier(sql):
        return sqlparse_format(sql, reindent=True)

try:
    from pg_query import prettify
except ImportError:
    pg_query_prettifier = None
else:
    def pg_query_prettifier(sql):
        return prettify(sql)


dialect = None

def select_sa_dialect(app):
    global dialect
    classname = app.config.autodoc_sa_dialect
    if classname:
        if isinstance(classname, str):
            modulename, classname = classname.rsplit('.', 1)
            module = __import__(modulename, fromlist=[classname])
            dialect = getattr(module, classname)()
        else:
            dialect = classname
    else:
        dialect = None


def stringify(how, stmt):
    if how == 'sqlparse':
        prettifier = sqlparse_prettifier
    elif how == 'pg_query':
        prettifier = pg_query_prettifier
    else:
        prettifier = None

    if isinstance(stmt, Query):
        stmt = stmt.statement
    if dialect is not None:
        stmt = stmt.compile(dialect=dialect)
    sql = str(stmt)
    if prettifier is not None:
        try:
            sql = prettifier(sql)
        except Exception as e:
            # TODO: log the error
            pass

    return sql


class AttributeDocumenter(autodoc.AttributeDocumenter):
    """
    Customized AttributeDocumenter that knows about SA Select
    """

    def add_directive_header(self, sig):
        if not isinstance(self.object, (ClauseElement, Query)):
            autodoc.AttributeDocumenter.add_directive_header(self, sig)
        else:
            autodoc.ClassLevelDocumenter.add_directive_header(self, sig)

    def add_content(self, more_content, no_docstring=False):
        autodoc.AttributeDocumenter.add_content(self, more_content, no_docstring)
        if isinstance(self.object, (ClauseElement, Query)):
            sql = stringify(self.env.config.autodoc_sa_prettifier, self.object)
            self.add_line("", "")
            lang = self.env.config.autodoc_sa_pygments_lang
            self.add_line(".. code-block:: %s" % lang, "")
            self.add_line("", "")
            for line in sql.splitlines():
                self.add_line("   " + line, "")


class DataDocumenter(autodoc.DataDocumenter):
    """
    Customized DataDocumenter that knows about SA Select
    """

    def add_directive_header(self, sig):
        if not isinstance(self.object, (ClauseElement, Query)):
            autodoc.DataDocumenter.add_directive_header(self, sig)
        else:
            autodoc.ModuleLevelDocumenter.add_directive_header(self, sig)

    def add_content(self, more_content, no_docstring=False):
        autodoc.DataDocumenter.add_content(self, more_content, no_docstring)
        if isinstance(self.object, (ClauseElement, Query)):
            sql = stringify(self.env.config.autodoc_sa_prettifier, self.object)
            self.add_line("", "")
            lang = self.env.config.autodoc_sa_pygments_lang
            self.add_line(".. code-block:: %s" % lang, "")
            self.add_line("", "")
            for line in sql.splitlines():
                self.add_line("   " + line, "")


def setup(app):
    "Setup the Sphinx environment."

    from sphinx.config import ENUM

    autodoc.add_documenter(AttributeDocumenter)
    autodoc.add_documenter(DataDocumenter)
    app.add_config_value('autodoc_sa_dialect', None, True)
    app.add_config_value('autodoc_sa_prettifier', 'sqlparse', True,
                         ENUM('sqlparse', 'pg_query'))
    app.add_config_value('autodoc_sa_pygments_lang', 'sql', True)
    app.connect('builder-inited', select_sa_dialect)
