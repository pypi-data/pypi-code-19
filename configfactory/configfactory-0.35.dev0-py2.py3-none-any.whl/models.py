from django.db import models
from django.utils.functional import cached_property

from configfactory.utils import json_dumps, json_loads


class Component(models.Model):

    name = models.CharField(max_length=64, unique=True)

    alias = models.SlugField(
        unique=True,
        help_text='Unique component alias'
    )

    settings_json = models.TextField(
        blank=True,
        null=True,
        default='{}'
    )

    schema_json = models.TextField(
        blank=True,
        null=True,
        default='{}'
    )

    require_schema = models.BooleanField(
        default=True,
        help_text='Use json schema validation'
    )

    is_global = models.BooleanField(
        default=False,
        help_text="Use only base environment"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    @cached_property
    def settings(self):
        return json_loads(self.settings_json)

    @property
    def schema(self):
        return json_loads(self.schema_json)

    @schema.setter
    def schema(self, value):
        self.schema_json = json_dumps(value)
