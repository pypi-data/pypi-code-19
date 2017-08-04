import os

from invoke import task


@task(default=True)
def build(ctx, tag=None):
    ctx.run("docker build -t %s --pull --force-rm ." % (tag or ctx.docker.tag))


@task
def rebuild(ctx, tag=None):
    ctx.run("docker build -t %s --pull --force-rm --no-cache ." % (tag or ctx.docker.tag))
