import requests
import json

from . import urls
from requests.auth import HTTPBasicAuth


class BrokerClient:

    def __init__(
        self,
        *,
        broker_url,
        pact_dir='.',
        user=None,
        password=None,
        authentication=False
    ):
        self.broker_url = broker_url.rstrip('/')
        self.username = user
        self.password = password
        self.pact_dir = pact_dir
        self.authentication = authentication
        self._auth = None

        if self.authentication:
            if not (self.username and self.password):
                raise ValueError(
                    'When authentication is True, username and password '
                    'must be provided.'
                )
            else:
                self._auth = HTTPBasicAuth(self.username, self.password)

    def pull_pact(
        self,
        *,
        provider,
        consumer,
        tag=''
    ):
        request_url = urls.PULL_PACT_URL.format(
            broker_url=self.broker_url,
            provider=provider,
            consumer=consumer,
            tag=tag
        )

        response = requests.get(
            request_url,
            auth=self._auth
        )
        response.raise_for_status()
        saved_pact_path = self._save_pact(
            pact_json=response.json(),
            consumer=consumer,
            provider=provider
        )

        return response, f'Pact saved to {saved_pact_path}'

    def push_pact(self, *, pact_file, provider, consumer, consumer_version):
        request_url = urls.PUSH_PACT_URL.format(
            broker_url=self.broker_url,
            provider=provider,
            consumer=consumer,
            consumer_version=consumer_version
        )

        with open(pact_file) as data_file:
            pact_json = json.load(data_file)

        response = requests.put(
            request_url,
            auth=self._auth,
            json=pact_json
        )
        response.raise_for_status()
        return response, (
            f'Pact between {consumer} and {provider} pushed.'
        )

    def tag_consumer(self, *, provider, consumer, consumer_version, tag):
        request_url = urls.TAG_CONSUMER_URL.format(
            broker_url=self.broker_url,
            consumer=consumer,
            consumer_version=consumer_version,
            tag=tag
        )
        response = requests.put(
            request_url,
            headers={'Content-Type': 'application/json'},
            auth=self._auth
        )
        response.raise_for_status()
        return response, (
            f'{consumer} version {consumer_version} tagged as {tag}'
        )

    def _save_pact(self, *, pact_json, consumer, provider):
        consumer = consumer.replace(' ', '_')
        provider = provider.replace(' ', '_')
        file_path = f'{self.pact_dir}/{provider}_{consumer}.json'.lower()

        with open(file_path, 'w') as pact_file:
            json.dump(pact_json, pact_file)

        return file_path
