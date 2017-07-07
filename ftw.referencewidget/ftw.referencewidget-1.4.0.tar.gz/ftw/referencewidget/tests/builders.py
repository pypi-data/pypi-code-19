from ftw.builder import registry
from ftw.builder.dexterity import DexterityBuilder


class SampleContentBuilder(DexterityBuilder):
    portal_type = 'SampleContent'

registry.builder_registry.register(
    'refwidget sample content', SampleContentBuilder)
