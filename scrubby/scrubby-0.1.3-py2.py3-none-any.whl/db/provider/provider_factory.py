from .postgres_provider import PostgresProvider

class ProviderFactory(object):
    providers = {
        'postgres': PostgresProvider,
    }

    def create(connection_string):
        options = connection_string.split(';')
        provider = options.pop(0)

        if not provider in ProviderFactory.providers:
            raise Exception('Provider {provider} is not supported.'.format(
                provider=provider,
            ))

        return providers[provider](*options)