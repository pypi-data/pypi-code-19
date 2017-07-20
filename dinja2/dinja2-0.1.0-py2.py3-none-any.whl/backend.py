# coding=utf-8
import logging
import os
import sys
from collections import OrderedDict

import six

import jinja2
from django.conf import settings
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.template.backends.base import BaseEngine
from django.template.backends.jinja2 import Template, get_exception_info
from django.template.context import make_context
from django.test.signals import template_rendered
from django.utils._os import upath
from django.utils.functional import cached_property
from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import split_template_path
from jinja2.utils import import_string, open_if_exists

logging = logging.getLogger(__name__)


class Jinja2Engine(BaseEngine):
    app_dirname = 'jinja2'

    def __init__(self, params):
        params = params.copy()
        self.options = params.pop('OPTIONS').copy()
        super(Jinja2Engine, self).__init__(params)

        self.loaders = [
            jinja2.FileSystemLoader(self.template_dirs),
            ModelDirsLoader(self.app_dirname),
        ]
        loader = jinja2.loaders.ChoiceLoader(self.loaders)

        environment = self.options.pop('environment', {'jinja2.Environment': {}})
        assert len(environment) == 1, "Jinja2Engine option 'environment' should have only one key-value pair: {}".format(environment)
        env_cls, env = environment.popitem()
        env.setdefault('loader', loader)
        env.setdefault('autoescape', True)
        env.setdefault('auto_reload', settings.DEBUG)
        # env.setdefault('undefined', jinja2.DebugUndefined if settings.DEBUG else jinja2.StrictUndefined)
        env.setdefault('undefined', jinja2.DebugUndefined if settings.DEBUG else jinja2.Undefined)
        env_cls = import_string(env_cls)
        self.env = env_cls(**env)

    def from_string(self, template_code):
        return SignalingTemplate(self.env.from_string(template_code), self)

    def get_template(self, template_name):
        try:
            return SignalingTemplate(self.env.get_template(template_name), self)
        except jinja2.TemplateNotFound as exc:
            tried = []
            from django.template.base import Origin as DjangoOrigin
            for loader in self.loaders:
                try:
                    loader.get_source(self.env, template_name)
                except jinja2.TemplateNotFound as ex:
                    tried.append((DjangoOrigin(name=ex.name, template_name=ex.templates[0], loader=loader), ex.message))
            raise TemplateDoesNotExist(template_name, backend=self, tried=tried)

        except jinja2.TemplateSyntaxError as exc:  # pragma: no cover
            new = TemplateSyntaxError(exc.args)
            new.template_debug = get_exception_info(exc)
            six.reraise(TemplateSyntaxError, new, sys.exc_info()[2])

    @cached_property
    def context_processors(self):
        return tuple(import_string(path) for path in self.options['context_processors'])


def get_app_template_dirs_map(dirname):
    """
    Return an iterable of paths of directories to load app templates from.

    dirname is the name of the subdirectory containing templates inside
    installed applications.
    """
    template_dirs = OrderedDict()
    from django.apps import apps
    for app_config in apps.get_app_configs():
        if not app_config.path:  # pragma: no cover
            continue
        template_dir = os.path.join(app_config.path, dirname)
        if os.path.isdir(template_dir):
            template_dirs[app_config.name.rsplit(".", 1)[-1]] = upath(template_dir)
    return template_dirs


class SignalingTemplate(Template):
    @property
    def name(self):
        return self.template.name

    def render(self, context=None, request=None):
        context_processors = self.backend.context_processors
        context = self.process_context(request, context, context_processors)

        django_context = make_context(context, request)
        template_rendered.send(sender=self, template=self, context=django_context)
        return self.template.render(context)

    def process_context(self, request, context, context_processors):
        if context is None:  # pragma: no cover
            context = {}

        if request is not None:
            for processor in context_processors:
                context.update(processor(request))

        return context


class ModelDirsLoader(jinja2.loaders.BaseLoader):
    def __init__(self, template_folder, encoding='utf-8', followlinks=False):
        self.template_folder = template_folder
        self.app_template_dirs = get_app_template_dirs_map(template_folder)
        self.encoding = encoding
        self.followlinks = followlinks

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        app, pieces = pieces[0], pieces[1:]
        templates_dir = self.app_template_dirs.get(app)
        if templates_dir is None:
            apps = ", ".join(self.app_template_dirs.keys())
            raise TemplateNotFound(template,
                                   "Application '{}' does not have an AppConfig, valid applications are: {}, they all have a template folder named {}".format(app, apps, self.template_folder))
        pieces, file_name = pieces[:-1], pieces[-1]
        # logging.debug("pieces: %s" % pieces)
        # logging.debug("file_name: %s" % file_name)

        # if "_" in file_name:
        #     # "app/<model_name>_template.html => app/templates/<model_name>/template.html
        #     # TODO: Generic app/templates/template.html
        #     pieces += file_name.rsplit("_", 1)
        # else:  # pragma: no cover
        pieces += [file_name]

        logging.debug("pieces: %s" % pieces)
        logging.debug("templates_dir: %s" % templates_dir)
        filename = os.path.join(templates_dir, *pieces)
        logging.debug("filename: %s" % filename)
        f = open_if_exists(filename)
        if f is None:  # pragma: no cover
            raise TemplateNotFound(template, "File '{}' does exists".format(filename))
        try:
            contents = f.read().decode(self.encoding)
        finally:
            f.close()

        mtime = os.path.getmtime(filename)

        def uptodate():  # pragma: no cover
            try:
                return os.path.getmtime(filename) == mtime
            except OSError:
                return False

        return contents, filename, uptodate

    def list_templates(self):  # pragma: no cover
        found = set()
        for application, searchpath in self.app_template_dirs:
            walk_dir = os.walk(searchpath, followlinks=self.followlinks)
            for dirpath, dirnames, filenames in walk_dir:
                for filename in filenames:
                    template = os.path.join(dirpath, filename)[len(searchpath):].strip(os.path.sep).replace(os.path.sep, '/')
                    if template[:2] == './':
                        template = template[2:]
                    if template not in found:
                        found.add(template)
        return sorted(found)
