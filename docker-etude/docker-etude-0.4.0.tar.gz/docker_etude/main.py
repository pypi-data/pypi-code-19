"""
CLI entry point.

"""
from click import echo, group, option

from docker_etude.sources import ECSSource, LocalStackSource


@group()
def etude():
    """
    Generate a composition.

    """
    pass


@etude.command(name="ecs")
@option("--region", default="us-east-1")
@option("--profile")
@option("--cluster-pattern")
@option("--task-pattern")
@option("--service-pattern")
def ecs(region, profile, **kwargs):
    source = ECSSource(
        profile=profile,
        region=region,
        **kwargs
    )
    composition = source.load()
    echo(composition.to_yaml())


@etude.command(name="localstack")
@option("--region", default="us-east-1")
def localstack(region):
    source = LocalStackSource(
        region=region,
    )
    composition = source.load()
    echo(composition.to_yaml())
