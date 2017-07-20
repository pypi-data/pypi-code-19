import click

from . import BrokerClient
from . import settings


@click.command()
@click.option('--broker_url', help='Pact Broker host.')
@click.option('--consumer', help='Consumer service name.')
@click.option('--provider', help='Provider service name.')
@click.option('--user', help='Pact Broker user.')
@click.option('--password', help='Pact Broker password.')
@click.option('--pact_dir', default='.', help='Directory to save Pacts to.')
@click.option('--pact_version', default='latest', help='Pact version to pull.')
@click.option(
    '--auth',
    default=False,
    is_flag=True,
    help='Indicates if Pact Broker is authenticated.'
)
def pull_pact(
    broker_url,
    consumer,
    provider,
    user,
    password,
    auth,
    pact_dir,
    pact_version
):

    broker_client = BrokerClient(
        broker_url=broker_url or settings.PACT_BROKER_URL,
        pact_dir=pact_dir or settings.PACT_DIR,
        user=user or settings.PACT_BROKER_USER,
        password=password or settings.PACT_BROKER_PASSWORD,
        authentication=auth
    )

    result = broker_client.pull_pact(
        consumer=consumer,
        provider=provider,
        pact_version=pact_version
    )

    click.echo(result[1])


@click.command()
@click.option('--broker_url', help='Pact Broker host.')
@click.option('--consumer', help='Consumer service name.')
@click.option('--provider', help='Provider service name.')
@click.option('--user', help='Pact Broker user.')
@click.option('--password', help='Pact Broker password.')
@click.option('--pact_file', help='Path to the Pact to push.')
@click.option('--consumer_version', help='Consumer application version.')
@click.option('--pact_dir', default='.', help='Directory to save Pacts to.')
@click.option(
    '--tag', required=True, help='Consumer version tag. eg "prod".'
)
@click.option(
    '--auth',
    default=False,
    is_flag=True,
    help='Pact Broker is authenticated.'
)
def push_pact(
    broker_url,
    consumer,
    provider,
    user,
    password,
    auth,
    pact_file,
    consumer_version,
    pact_dir,
    tag
):

    broker_client = BrokerClient(
        broker_url=broker_url or settings.PACT_BROKER_URL,
        pact_dir=pact_dir or settings.PACT_DIR,
        user=user or settings.PACT_BROKER_USER,
        password=password or settings.PACT_BROKER_PASSWORD,
        authentication=auth
    )

    push_pact_result = broker_client.push_pact(
        consumer=consumer,
        provider=provider,
        pact_file=pact_file,
        consumer_version=consumer_version
    )
    click.echo(push_pact_result[1])

    tag_consumer_result = broker_client.tag_consumer(
        consumer=consumer,
        provider=provider,
        consumer_version=consumer_version,
        tag=tag
    )
    click.echo(tag_consumer_result[1])
