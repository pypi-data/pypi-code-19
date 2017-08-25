from django.apps import AppConfig


class ThorsonWikiConfig(AppConfig):

    name = 'thorson_wiki'

    def ready(self):

        import thorson_wiki.signals

        super(ThorsonWikiConfig, self).ready()
