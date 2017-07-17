# -*- coding: utf-8 -*-
"""
    weppy_haml.ext
    --------------

    Provides the Haml extension for weppy

    :copyright: (c) 2017 by Giovanni Barillari
    :license: BSD, see LICENSE for more details.
"""

import os
import codecs
from weppy.extensions import Extension, TemplateExtension
from weppy.utils import cachedprop
from .hamlpy import Compiler


def _read_source(filepath):
    with codecs.open(filepath, 'r', encoding='utf-8') as f:
        rv = f.read()
    return rv


def _store_compiled(filepath, code):
    with codecs.open(filepath + ".html", 'w', encoding='utf-8') as dest:
        dest.write(code)


class Haml(Extension):
    default_config = dict(
        set_as_default=False,
        auto_reload=False,
        preload=True
    )

    def on_load(self):
        self.env.ext = self
        self.env.mtimes = {}
        self.env.builts = {}
        self.env.compiler = Compiler()
        self.app.add_template_extension(HamlTemplate)
        if self.config.set_as_default:
            self.app.template_default_extension = '.haml'
        if not self.config.preload:
            return
        for path, dirs, files in os.walk(self.app.template_path):
            for fname in files:
                if os.path.splitext(fname)[1] == ".haml":
                    file_path = os.path.join(path, fname)
                    rel_path = file_path.split(self.app.template_path + "/")[1]
                    self._build_html(
                        os.path.join(path, fname),
                        rel_path)

    @property
    def changes(self):
        return self.config.auto_reload or self.app.debug

    def _build_html(self, file_path, fname):
        source = _read_source(file_path)
        code = self.env.compiler.process_lines(source.splitlines())
        _store_compiled(file_path, code)
        self.env.mtimes[file_path] = os.stat(file_path).st_mtime
        self.env.builts[file_path] = fname + '.html'
        return self.env.builts[file_path]


class HamlTemplate(TemplateExtension):
    namespace = 'Haml'
    file_extension = '.haml'

    def is_cache_valid(self, file_path):
        try:
            mtime = os.stat(file_path).st_mtime
        except Exception:
            return False
        old_time = self.env.mtimes.get(file_path, 0)
        if mtime > old_time:
            return False
        return True

    def reloader_get(self, file_path):
        if self.is_cache_valid(file_path):
            return self.cached_get(file_path)
        return None

    def cached_get(self, file_path):
        return self.env.builts.get(file_path)

    @cachedprop
    def get_template(self):
        if self.env.ext.changes:
            return self.reloader_get
        return self.cached_get

    def preload(self, path, name):
        file_path = os.path.join(path, name)
        html_name = self.get_template(file_path) or self.env.ext._build_html(
            file_path, name)
        return path, html_name
