# -*- coding: utf-8 -*-
"""
this should be a basic package that
reads everything from a directory
structure (data lazy) and provide
a flexible object model to access
all the resources

- data files (rst, yaml, csv, xlsx, etc)
    rst needs support for :ref: inside nao datastructure
    add rst parsing to yaml files, also support cross yaml referencing with rst style tags
- database connections (sqlite, special yaml files using, sqlalchemy models?)
- automatically serve those files as a webserver
- python files for code support (no relative import only through nao.self?)
    - decorators to provide functionality outside (e.g. auth, etc)
- template files made available automatically (in nao.current.template)

later multilayer support should be added
the main resaon for that is supporting
multilingualism (also production, testing separation)

multilingualism is supported by babel negotiatble tags(e.g. en_US)

mode separation is set up based on _identifier style tags

"""
from __future__ import unicode_literals # no need in python3 stack

# basic logging
import os
import sys
import logging
import time
import functools
import codecs
import re
import collections

# from future.utils import python_2_unicode_compatible

from .utils import obj2xml, recursive_update, padded
from .types import odict, naodict, nao

from ._yaml import load as yaml_load, dump as dump

# no handler is added
rootlogger = logging.getLogger()

def logger(name,
        level='debug',
        dict_config=None,
        add_default_logger=False,
    ):
    """
    For logging in modules outside of nao use::
    log = nao.logger(__name__)
    """
    # process dict config

    # not necessary since Python2.7 accept string levels
    levels = {
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
    }
    lvl = levels[level.lower()]

    log = logging.getLogger(name)
    log.setLevel(lvl)

    # optional only if there is no other logger
    if add_default_logger:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        fmtr = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(fmtr)
        log.addHandler(ch)

    log.root = rootlogger

    return log

# default logger for nao
log = logger(__name__) 


op = os.path


def load(source=None):
    """
    main entry point, loads everything from a given point
    of the file system (usually __file__)

    builds a tree based on file names and parse
    files based on extension and alphabetical
    order

    .yaml
        regular python data
        with some type of nao reference type available
        maybe all text fields interpreted as rst is a good idea
        add protocol handling as well (file://, ext://, oracle://, ...)
        see `logging.config.dictConfig` for reference

    .rst
        parsed as in sphinx docs into raw html
        :nao:`something` should be available

    .csv, .sql, .xls, .xlsx
        deferred datatable
        sql should run on the default db connection
        defined by nao-tree (with special .nao files)
        if nothing defined .nao-s own default sqlite
        db should be used (cashing, etc also in that)
    
    .nao
        special resource described in YAML
        e.g. database connaction, RPC service, aPI calls, etc.
        return a Python object???
        similar .rst's and .yaml's ext directive

    .html, .jinja
        parsed as jinja templates by default
        the object returned in load is available by the
        name nao in tempate global (think it over more)

    .py
        parsed as python code and an object tree
        is build (I know this is going to be controversial...)

    .jpg, .png, .mp3, .wav, .avi, ...
        parsed as media resource (embed in template)


    read system information as well and do
    everything in a multilayer and cascading
    manner

    returns a root element
    """
    if source is None:
        # doubles the check for existence, but avoids strange errors
        if op.exists('nao'):
            source = 'nao'

        # TODO check for nao.yaml, nao/, config.yaml, config/
        # in some order defined as a cutomizable parameter

        # finally load current directory as a config directory

    if op.exists(source):
        if op.isdir(source):
            log.debug("Loading from directory recursively")
            pass
            # TODO implement recursive directory loading
            # see Naopath.filter
        else:
            log.debug("Loading from single file")
            with codecs.open(source, encoding='utf8') as f:
                # TODO add content negotiation here
                return yaml_load(f)

    else:
        log.debug("Loading from string")

        # TODO create yaml naodictloader

        return yaml_load(source)
    # if source == None, then try to load [cwd]/nao

    # get directory based on source

    # create root_node of current directory
    # walk recursively, skip everything that starts with _
    # create nao* object-tree

    # nao.path(data.config.general)
    # str(data.config) # returns a path if it is a file/directory
    # nao.url(naobject :)


def separate(data, values):
    """
    recursively traverse data tree (mappings, lists)
    and yield that many different data stucture as the
    length of values
    """

    for val in values:

        yield val, _filter(data, val)


# from copy import deepcopy

def _filter(data, val=None):

    if isinstance(data, dict):
        if val is not None and val in data:
            return _filter(data[val])

        else:
            r = {}
            for k in data:
                r[k] = _filter(data[k], val)
            return r

    elif isinstance(data, list):

        return [_filter(i, val) for i in data]

    else:
        return data


# from .utils import *
def ordered(*args, **kwds):
    """
    Constructs an `odict` from `args` and `kwds`
    From PYthon 3.6 dict preserve order
    """
    od = odict()
    for a in args:
        od[a] = kwds[a] if a in kwds else None
    return od


u1reg = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
u2reg1 = re.compile('(.)([A-Z][a-z]+)')
u2reg2 = re.compile('(a-z0-9])([A-Z])')

def underscore(text, method='single_reg'):
    """
    Largely based on Stack Overflow.
    Two methods are only implemented out of curiosity.

    Converts `CamelCase` or `camelCase` to under_score style.
    Able to handle `camelAndHTTPResponse` as `camel_and_http_response`.
    Avoids multiple underscores, so `under_Score` remains `under_score`
    does not become `under__score`.
    """

    if method == 'single_reg':
        return u1reg.sub(r'_\1', text).lower().replace('__', '_')

    if method == 'double_reg':
        temp = u2reg1.sub(r'\1_\2', text)
        return u2reg2.sub(r'\1_\2', temp).lower().replace('__', '_')

    raise ValueError("Method not recognized: {}".format(method))


def flatten(d, parent_key='', sep='.'):
    """
    FROM http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten(d):
    """
    TODO implement
    """



################
# NAO OPERATORS
# might not need to be implemented
# from .operators import *
def _back():
    """
    operator on nao nodes

    it could be used in a special interpreter later
    """

#conflicts with other in the same name
def _path():
    """operator on nao nodes"""

def create(path):
    """
    shoud work for magicpath only?
    """
    if not op.exists(path):
        os.makedirs(path)
        log.debug("Path created: {}".format(path))
    return path


def exist(path):

    return op.exists(path)


# TIMING CONTEXTMANAGER AND DECORATOR
def benchmark(arg):

    # normal use returns a context manager
    if not callable(arg):
        return Benchmark(str(arg))

    # decorator use: wrapped into a benchmark context
    func = arg
    @functools.wraps(func)
    def wrapper(*args, **kwds):
        with Benchmark('FUNC ' + func.__name__):
            return func(*args, **kwds)

    return wrapper

class Benchmark(object):
    """
    Based on something similar found long time ago on the internet
    """
    def __init__(self, name):
        self._name = name
        self._time = None

    def __enter__(self):
        self._begin = time.time()
        log.info("Benchmark <{}> started ...".format(self._name))

    def __exit__(self, exc_type, exc_value, traceback):
        self._time = time.time()-self._begin
        log.info("Benchmark <{}> finished in: {}".format(self._name, self.time))
        return False

    @property
    def time(self, raw=False):
        if time is None:
            raise ValueError('Not run yet')

        return self._time if raw else self.format_time(self._time)
    

    @staticmethod
    def format_time(seconds):
        """
        TODO use `babel.dates.format_timedelta` with
        `datetime.timedelta(seconds=...)`

        """
        t = []
        
        if seconds > 60*60:
            hours, seconds = divmod(seconds, 60*60)
            t.append("{:.0f}h".format(hours))
        
        if seconds > 60:
            mins, seconds = divmod(seconds, 60)
            t.append("{:.0f}m".format(mins))

        t.append("{:.3f}s".format(seconds))

        return ' '.join(t)




def _os_join(*bits):
    log.debug('join {}'.format(bits))
    return op.normpath(op.join(*bits))

def _url_join(*bits):
    return '/'.join(*bits)



def path(*base):
    """shortcut to prevent direct class usage"""
    # import pathlib
    # return pathlib.Path(*base)
    
    return NaoPath(*base)


class NaoError(Exception):
    pass

class NoPath(NaoError):
    pass

# @python_2_unicode_compatible
class NaoPath(object):
    """
    use a naodict to navigate through directory structure
    and __call__ to return a path string

    base = MagicPath('base_path')
    base.config == base['config'] # another MagicPath
    base.__up__ ?? base['..']
    base.config()  # base_path/config/
    base.config('my.conf')  # base_path/config/my.conf

    normpath is for reundant separators and up-level references
    realpath is to eliminate symbolic links
    """
    def __init__(self, *base):
        b = op.realpath(op.normpath(op.join(*base)))
        if not op.exists(b):
            log.warning("Non-existent path: {}".format(b))
        self.base = op.dirname(b) if op.isfile(b) else b


    def __getitem__(self, key):
        # log.debug(key)
        # log.debug(type(key))
        if isinstance(key, tuple):
            return self.__class__(self.__call__(*key))
        else:
            return self.__class__(self.__call__(key))


    def __call__(self, *bits, create=False):
        # .normpath
        p = op.normpath(op.join(self.base, *bits))
        if not op.exists(p):
            log.warning("Non-existent path: {}".format(p))
        return p


    def __str__(self):
        return self.base


    def __eq__(self, other):
        return self.base == other.base

    def __ne__(self, other):
        return not self.__eq__(other)


    def filter(self, expression=None, filetype=None, recursive=True, **kwds):
        """
        get certain files from a path
        """
        p = self()

        if not op.exists(p) or not op.isdir(p):
            return

        for root, dirs, files in os.walk(p, **kwds):

            if filetype:
                for f in files:
                    if f.endswith('.'+filetype):
                        yield op.join(root, f), f[:-len(filetype)-1]

            if not recursive:
                break

    def exists(self):

        return op.exists(self.base)

    # def __enter__():
    #     sys.path.insert(0, self.base):

    # def __exit__():
    #     sys.path.remove(self.base):


_nao_path = NaoPath(__file__)  # path for the nao package


def read_dir_raw_text(location, filter=None, encoding='utf8', recursive=False):

    for root, dirs, files in os.walk(location):
        for name in files:
            if filter is not None:
                if not filter(name): continue
                
            with open(op.join(root, name), encoding=encoding) as f:
                data = f.read().strip()  # strip might not adequate here
                yield name, data

        if not recursive: break # no recursion into subdirs


# read_sql from load oracle should come here somewhere


# nao.ext.sphinx

def make_html(doc_path, **kwds):

    return SphinxDoc(doc_path, **kwds)

    
    

class SphinxDoc(object):
    """Wrapping a sphinx documentation"""
    def __init__(self, doc_path, **kwds):
        """ """
        self._conf = {
            'master_doc':'index',
            'html_theme':'alabaster',
        }
        self._conf.update(kwds)
        self._doc_path = doc_path

        # TODO pop special args like build_path
        self._build_path = path(doc_path)('_build', 'html')


    def build(self):
        """ """
        #preparse options:
        conf = self._conf.copy()
        for k,v in conf.items():
            # list is comma separated
            if isinstance(v, list):
                conf[k] = ','.join(v)
            # dict is split
            if isinstance(v, dict):
                for k2,v2 in v.items():
                    conf[k+'.'+k2] = v2
                del conf[k]
            # boolean is 0 or 1
            if isinstance(v, bool):
                conf[k] = '1' if v else '0'


        self._opts = ' '.join(['-D '+k+"='"+v+"'" for k,v in conf.items()])
        # conf = "master_doc='index' -D html_theme='scrolls'"
        self._cmd = "sphinx-build -b html -C {} {} {}".format(self._opts, self._doc_path, self._build_path)

        os.system(self._cmd) # include output in debugging

        return self

    @property
    def command(self):
        return self._cmd

    @property
    def build_path(self):
        return self._build_path

    @property
    def doc_path(self):
        return self._doc_path

    @property
    def options(self):
        return self._opts

    @property
    def config(self):
        return self._conf
    


#################
# MOVE THIS TO nao.ext.web or something :D

class App(object):
    """
    This creates a WSGi application from a file
    structure based on the input parameters and
    app-level config (the config also read based
    on input parameters)

    Sensible defaults are:

    config/
        config directory
        files read: .yml, .yaml, .json, .cfg, .ini (=> incorporate anyconfig)
        namespace:
            directories
            # file names  (len < 24 and alpha start and single dot)
            # // ?? //
            # files only for concept separation

    handler/
        handler directory
        default style: cherrypy
        files parsed: .py
        use __root__ instead of default

    model/
        model directory
        default style: sqlalchemy
        files parsed: .py


    Alternative named setup structures:

    single-hierarchy
        parsing is in a single directory structure
        the file type is used to ditinguish separate
        elements (config, template, handler, model)

        all directories above are substituted for
        the root directory (e.g.: ``./``)

        Needs: import __init__ as root

    sphinx-kb
        A knowledge base type static page using sphinx

        sphinx-build -C bkd/static bkd/static/.sphinx
            http://sphinx-doc.org/invocation.html
        
        if no toctree, then ...
            use a generated __root__.rst to include every
            document with the glob option:
            http://sphinx-doc.org/markup/toctree.html
        
        webbrowser.open( url, new=0 ) 

    sphinx-blog
        A blog engine using sphinx :)


    WARNING make this a WSGI application
    """



    def __init__(self, root,
            setup='nao',
            templating='jinja2',
            modelling='SQLAlchemy',
            ):
        # derive directories from root with nao.path()
        root = os.path.split(os.path.realpath(root))[0]
        self.path = MagicPath(root)  #: path for the application

        self.setup = setup
        self.handlers = object()

        app_root = self.path()
        print(app_root)
        # TODO
        for root, dirs, files in os.walk(app_root):
            for d in dirs:
                if d.startswith('.'):
                    dirs.remove(d)

            for f in files:
                if not f.startswith('.') and not f.startswith('_'):
                    name,ext = os.path.splitext(f)
                    ext = ext[1:]
                    self._process(root, name, ext)
                    

    def _process(self, root, name, ext):
        """
        # applyprocessors
            # handler
                # spam = __import__('spam', globals(), locals(), [], 0)
            # config
            # model
            # template

            
        islink, join, isdir = path.islink, path.join, path.isdir

        # We may not have read permission for top, in which case we can't
        # get a list of the files the directory contains.  os.path.walk
        # always suppressed the exception then, rather than blow up for a
        # minor reason when (say) a thousand readable directories are still
        # left to visit.  That logic is copied here.
        try:
            # Note that listdir and error are globals in this module due
            # to earlier import-*.
            names = listdir(top)
        except error, err:
            if onerror is not None:
                onerror(err)
            return

        dirs, nondirs = [], []
        for name in names:
            if isdir(join(top, name)):
                dirs.append(name)
            else:
                nondirs.append(name)

        if topdown:
            yield top, dirs, nondirs
        for name in dirs:
            new_path = join(top, name)
            if followlinks or not islink(new_path):
                for x in walk(new_path, topdown, onerror, followlinks):
                    yield x
        if not topdown:
            yield top, dirs, nondirs

        """
        if ext == 'py':
            print(root+'-:-'+name+'-:-'+ext)
            # WARNING not threadsafe!
            sys.path.insert(0, root)
            sys.path.pop(0)


            

    def run(self, name, open=True):
        """


        """
        if name != '__main__': return

        if self.setup == 'sphinx-kb':
            # run sphinx
            p = self.path()

            # ' '.join(*['-D '+k+"='"+v+"'" for k,v in conf.iteritems()])
            conf = "master_doc='index' -D html_theme='scrolls'"
            os.system("sphinx-build -C -D {} {} {}/.sphinx".format(conf, p, p))
            
            self.base_url = self.path('.sphinx', 'index.html')
            
            self.open()


            # TODO setup cherrypy to serve static files from .sphinx/_build/html 
            


        else:
            self.base_url = 'http://localhost:8080'

            import cherrypy

            # cherrypy.config.update({'environment': 'embedded'})

            class HelloWorld:
                def index(self):
                    return "Hello world!"
                index.exposed = True

            if open:
                cherrypy.engine.subscribe('start', self.open)

            cherrypy
            cherrypy.quickstart(HelloWorld())


    def open(self):
        print('called')
        import webbrowser

        webbrowser.open(self.base_url, new=0)



class Server(object):

    def __init__(self):
        pass

    def serve(self, app):
        """
        The app could have configuration for the server, e.g.:

        port, ip, mount_point, etc

        The server could try to serve many apps in the same
        Python interpreter
        """
        pass

        # implement a cherrypy server start here :)

        # webbrowser.open( url, new=0 )  # open localhost



# read config before
server = Server()


auth = object()  # auth tool with OAuth support through requests_oauthlib
# add auth.all, auth.user and auth.groups() shortcut auth()

request = object()  # the dynamically changing request object
# expose cherrypy request object

db = object()  # a threadsafe SQLAlchemy session (as deault on SQLite), version aware 

expose = object() # a default decorator to add handlers