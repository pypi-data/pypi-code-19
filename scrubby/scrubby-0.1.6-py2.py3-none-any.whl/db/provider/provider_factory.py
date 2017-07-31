from .postgres_provider import PostgresProvider

class ProviderFactory(object):
    providers = {
        'postgres': PostgresProvider,
    }

    def create(self, connection_string):
        providers = ProviderFactory.providers

        options = connection_string.split(';')
        provider = options.pop(0)

        if not provider in providers:
            raise Exception('Provider {provider} is not supported.'.format(
                provider=provider,
            ))

        return providers[provider](*options)