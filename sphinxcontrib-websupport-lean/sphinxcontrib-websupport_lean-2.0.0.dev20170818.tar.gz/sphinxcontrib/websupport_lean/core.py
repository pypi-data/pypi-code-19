# -*- coding: utf-8 -*-
"""
    sphinxcontrib.websupport_lean.core
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Base Module for web support functions.

    :copyright: Copyright 2007-2016 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import sys
from os import path

from six.moves import cPickle as pickle
from jinja2 import Environment, FileSystemLoader

from sphinx.util.osutil import ensuredir
from sphinxcontrib.websupport_lean import errors
from sphinxcontrib.websupport_lean.storage import StorageBackend

if False:
    # For type annotation
    from typing import Dict  # NOQA


class WebSupport(object):
    """The main API class for the web support package. All interactions
    with the web support package should occur through this class.
    """
    def __init__(self,
                 srcdir=None,      # only required for building
                 builddir='',      # the dir with data/static/doctrees subdirs
                 datadir=None,     # defaults to builddir/data
                 staticdir=None,   # defaults to builddir/static
                 doctreedir=None,  # defaults to builddir/doctrees
                 storage=None,     # defaults to SQLite in datadir
                 buildername='websupport_lean',
                 confoverrides={},
                 status=sys.stdout,
                 warning=sys.stderr,
                 docroot='',
                 staticroot='static',
                 ):
        # directories
        self.srcdir = srcdir
        self.builddir = builddir
        self.outdir = path.join(builddir, 'data')
        self.datadir = datadir or self.outdir
        self.staticdir = staticdir or path.join(self.builddir, 'static')
        self.doctreedir = staticdir or path.join(self.builddir, 'doctrees')
        # web server virtual paths
        self.staticroot = staticroot.strip('/')
        self.docroot = docroot.strip('/')

        self.buildername = buildername
        self.confoverrides = confoverrides

        self.status = status
        self.warning = warning

        self._init_templating()
        self._init_storage(storage)

        self._globalcontext = None  # type: ignore

    def _init_storage(self, storage):
        if isinstance(storage, StorageBackend):
            self.storage = storage
        else:
            # If a StorageBackend isn't provided, use the default
            # SQLAlchemy backend.
            from sphinxcontrib.websupport_lean.storage.sqlalchemystorage \
                import SQLAlchemyStorage
            if not storage:
                # no explicit DB path given; create default sqlite database
                db_path = path.join(self.datadir, 'db', 'websupport.db')
                ensuredir(path.dirname(db_path))
                storage = 'sqlite:///' + db_path
            self.storage = SQLAlchemyStorage(storage)

    def _init_templating(self):
        import sphinx
        template_path = path.join(sphinx.package_dir,
                                  'themes', 'basic')
        loader = FileSystemLoader(template_path)
        self.template_env = Environment(loader=loader)

    def build(self):
        """Build the documentation. Places the data into the `outdir`
        directory. Use it like this::

            support = WebSupport(srcdir, builddir)
            support.build()

        This will read reStructured text files from `srcdir`. Then it will
        build the pickles, placing them into `builddir`.
        It will also save node data to the database.
        """
        if not self.srcdir:
            raise RuntimeError('No srcdir associated with WebSupport object')

        from sphinx.application import Sphinx
        app = Sphinx(self.srcdir, self.srcdir, self.outdir, self.doctreedir,
                     self.buildername, self.confoverrides, status=self.status,
                     warning=self.warning)
        app.builder.set_webinfo(self.staticdir, self.staticroot,  # type: ignore
                                self.storage)

        self.storage.pre_build()
        app.build()
        self.storage.post_build()

    def get_globalcontext(self):
        """Load and return the "global context" pickle."""
        if not self._globalcontext:
            infilename = path.join(self.datadir, 'globalcontext.pickle')
            with open(infilename, 'rb') as f:
                self._globalcontext = pickle.load(f)
        return self._globalcontext

    def get_document(self, docname, username='', moderator=False):
        """Load and return a document from a pickle. The document will
        be a dict object which can be used to render a template::

            support = WebSupport(datadir=datadir)
            support.get_document('index', username, moderator)

        In most cases `docname` will be taken from the request path and
        passed directly to this function. In Flask, that would be something
        like this::

            @app.route('/<path:docname>')
            def index(docname):
                username = g.user.name if g.user else ''
                moderator = g.user.moderator if g.user else False
                try:
                    document = support.get_document(docname, username,
                                                    moderator)
                except DocumentNotFoundError:
                    abort(404)
                render_template('doc.html', document=document)

        The document dict that is returned contains the following items
        to be used during template rendering.

        * **body**: The main body of the document as HTML
        * **sidebar**: The sidebar of the document as HTML
        * **relbar**: A div containing links to related documents
        * **title**: The title of the document
        * **css**: Links to css files used by Sphinx
        * **script**: Javascript assets required for searching

        This raises :class:`~sphinxcontrib.websupport.errors.DocumentNotFoundError`
        if a document matching `docname` is not found.

        :param docname: the name of the document to load.
        """
        docpath = path.join(self.datadir, 'pickles', docname)
        if path.isdir(docpath):
            infilename = docpath + '/index.fpickle'
            if not docname:
                docname = 'index'
            else:
                docname += '/index'
        else:
            infilename = docpath + '.fpickle'

        try:
            with open(infilename, 'rb') as f:
                document = pickle.load(f)
        except IOError:
            raise errors.DocumentNotFoundError(
                'The document "%s" could not be found' % docname)

        document['script'] = document['script']
        return document
