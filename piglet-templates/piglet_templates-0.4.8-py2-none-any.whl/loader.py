# Copyright 2016 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from contextlib import contextmanager
from functools import partial
from itertools import chain
from tempfile import NamedTemporaryFile
import hashlib
import io
import os
import re

from gettext import NullTranslations

from piglet.exceptions import TemplateNotFound
from piglet.template import HTMLTemplate, TextTemplate
from piglet import __version__

ustr = type(u'')


class TemplateLoader(object):
    """
    Loads template from the specified file system search path
    """

    hash = hashlib.md5
    extension_map = {'.txt': TextTemplate,
                     '.htm': HTMLTemplate,
                     '.html': HTMLTemplate,
                     '.xhtml': HTMLTemplate,
                     '.xhtm': HTMLTemplate,
                     '.xml': HTMLTemplate,
                     }

    def __init__(self,
                 search_path,
                 auto_reload=False,
                 default_encoding='UTF-8',
                 template_cls=HTMLTemplate,
                 translations_factory=NullTranslations,
                 cache_dir=None,
                 allow_absolute_paths=False,
                 extension_map=extension_map,
                 ):
        """
        :param search_path: a list of paths to be searched for template files;
                            or a single path
        :param auto_reload: If ``True`` the template file modification time
                            will be checked on each call to load, and the
                            template reloaded if it appears to have changed.
        :param default_encoding: The default character encoding to assume
        """
        self.search_path = search_path

        if isinstance(self.search_path, (str, ustr)):
            self.search_path = [self.search_path]

        self.auto_reload = auto_reload
        self.default_encoding = default_encoding
        self.template_cls = template_cls
        self.extension_map = extension_map
        self.translations_factory = translations_factory
        self.allow_absolute_paths = allow_absolute_paths

        #: A cache mapping (filename, relative_to, template_class) -> template
        self._cache = {}
        #: A cache mapping:
        #:
        #:   (MD5(template_content), filename, template_class) -> template
        #:
        #: This is useful because a template will have an entry in the main
        #: cache for every (filename, relative_to) pair. This second level
        #: cache ensures we only ever create a single Template object for
        #: the same content, so these multiple entries will point to a single
        #: Template instance.
        self._level2_cache = {}
        self.pysrc_dir = None

        if cache_dir is None:
            cache_dir = os.environ.get('PIGLET_CACHE', None)

        if cache_dir:
            self.pysrc_dir = os.path.join(cache_dir, __version__)
            try:
                os.makedirs(self.pysrc_dir)
            except OSError:
                pass

    def load(self,
             filename,
             relative_to=None,
             encoding=None,
             template_cls=None,
             normpath=os.path.normpath,
             isabs=os.path.isabs,
             dirname=os.path.dirname,
             relpath=os.path.relpath,
             splitext=os.path.splitext,
             pjoin=os.path.join):

        encoding = encoding or self.default_encoding
        if template_cls is None:
            ext = splitext(filename)[1]
            template_cls = self.extension_map.get(
                ext.lower(), self.template_cls)
        relative_filename = (relative_to.filename
                             if relative_to is not None
                             else None)

        load_relative = relative_to is not None and filename.startswith('./')
        if relative_to is not None:
            for d in self.search_path:
                if relative_filename.startswith(d):
                    filename = pjoin(dirname(relpath(relative_filename, d)),
                                     filename)
                    break
        search_path = self.search_path
        if isabs(filename) and self.allow_absolute_paths:
                search_path = chain([''], search_path)

        if load_relative:
            search_path = chain([dirname(relative_to.filename)],
                                search_path)

        filename = normpath(filename)
        cache_key = (filename, relative_filename, template_cls)
        cached = cached_mtime = None

        try:
            cached, cached_mtime = self._cache[cache_key]
            if not self.auto_reload:
                return cached
        except KeyError:
            pass

        candidates = fs_loader(filename, search_path, encoding)
        if relative_to is not None:
            # A template using <py:extends> to load another template with the
            # same filename should explore lower priority directories before
            # trying to include itself
            candidates = list(candidates)
            candidates = chain(
                ((p, m, o) for p, m, o in candidates if p != relative_filename),
                ((p, m, o) for p, m, o in candidates if p == relative_filename))

        for path, mtime, openfile in candidates:
            if cached and mtime <= cached_mtime:
                return cached

            with openfile() as f:
                content = f.read()
            digest = self.hash(content.encode('utf-8')).digest()
            template = self._get_template_from_level2_cache(
                digest, filename, template_cls)

            if template is None:
                template = self._get_template_from_pysrc_dir(
                    template_cls,
                    path=path,
                    content=content,
                    mtime=mtime)

            if template is None:
                template = template_cls(source=content,
                                        filename=path,
                                        loader=self,
                                        translations_factory=self.translations_factory)

            self._write_pysrc(template)
            self._level2_cache[filename, template_cls] = digest, template
            self._cache[cache_key] = template, mtime
            return template
        raise TemplateNotFound(filename)

    def _get_template_from_level2_cache(self, digest, filename, template_cls):
        try:
            c_digest, template = self._level2_cache[filename, template_cls]
            if c_digest != digest:
                del self._level2_cache[filename, template_cls]
                return None
            return template
        except LookupError:
            return None

    def _get_template_from_pysrc_dir(self, template_cls, path, mtime, content):

        if self.pysrc_dir is None:
            return None

        pysrc_path = self.get_pysrc_path(path)
        if not os.path.isfile(pysrc_path):
            return None

        if os.stat(pysrc_path).st_mtime < mtime:
            return None

        with io.open(pysrc_path, 'r', encoding='utf-8') as f:
            pysrc = f.read()

        return template_cls.from_pysrc(
            pysrc,
            pysrc_path,
            path,
            loader=self,
            translations_factory=self.translations_factory)

    def get_pysrc_path(self, abspath):
        path = '{}_{}.py'.format(re.sub(r'[^A-Za-z0-9\-]', '_', abspath),
                                 self.hash(abspath.encode('utf8')).hexdigest())
        return os.path.join(self.pysrc_dir, path)

    def _write_pysrc(self, template):
        if self.pysrc_dir is None:
            return
        pysrc = template.get_pysrc()
        if pysrc is None:
            return

        pysrc_path = self.get_pysrc_path(template.filename)
        with atomic_write(pysrc_path) as f:
            f.write(pysrc.encode('utf-8'))


def fs_loader(filename,
              searchpath,
              encoding,
              getmtime=os.path.getmtime,
              pjoin=os.path.join):
    filepath = None
    mtime = None
    for p in searchpath:
        filepath = pjoin(p, filename)
        if not filepath.startswith(p):
            continue
        try:
            mtime = getmtime(filepath)
        except OSError:
            continue

        if mtime is not None:
            yield filepath, mtime, partial(io.open, filepath, encoding=encoding)


@contextmanager
def atomic_write(path):
    """
    Write to path in an atomic operation.
    """
    d = os.path.dirname(path)
    tmpfile = NamedTemporaryFile(delete=False, dir=d)
    yield tmpfile
    tmpfile.close()
    os.rename(tmpfile.name, path)
