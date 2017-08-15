import os

from django.forms.renderers import BaseRenderer
from django.template.backends.django import DjangoTemplates
from django.utils.functional import cached_property

ROOT = os.path.dirname(__file__)


class FoundationTemplates(BaseRenderer):
    """
    Load Django templates from the built-in widget templates in
    this application's 'templates' directory.
    """
    backend = DjangoTemplates

    def get_template(self, template_name):
        return self.engine.get_template(template_name)

    @cached_property
    def engine(self):
        return self.backend({
            'APP_DIRS': True,
            'DIRS': [os.path.join(ROOT, self.backend.app_dirname)],
            'NAME': 'foundationforms',
            'OPTIONS': {},
        })
