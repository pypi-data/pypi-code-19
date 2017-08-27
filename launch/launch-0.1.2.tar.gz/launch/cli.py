# coding=utf-8
# Copyright 2017 Flowdas Inc. <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os

import click
import yaml

from .launch import Launch

__all__ = [
    'command',
    'main',
]

#
# command line interface
#

_LAUNCH_KEY = 'launch.' + __name__
_LaunchType = Launch


class Cli(click.Group):
    def invoke(self, ctx):
        root = os.getcwd()
        while True:
            if os.path.exists(os.path.join(root, _LaunchType.launch_file())):
                ctx.meta[_LAUNCH_KEY] = _LaunchType(root)
                break
            next_root = os.path.dirname(root)
            if root == next_root:
                click.echo("%s not found" % _LaunchType.launch_file())
                ctx.exit(-1)
            else:
                root = next_root
        super(Cli, self).invoke(ctx)


@click.command(cls=Cli, invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help(), color=ctx.color)
        ctx.exit()


def command(*args, **kwargs):
    """명령행 인터페이스에 명령을 추가하는 데코레이터.

    첫번째 positional 인자로 :py:class:`Launch` 인스턴스가 제공된다.
    그 외의 인자는 :py:func:`click.command` 의 정의를 따른다.

    Example:

        >>> import launch
        >>> import click
        >>>
        >>> @launch.command(help='Echo text')
        ... @click.argument('text')
        ... def echo(launch, text):
        ...     click.echo(text)

    Since version 0.1.
    """

    def deco(func):
        def wrapper(ctx, *args, **kwargs):
            func(ctx.meta[_LAUNCH_KEY], *args, **kwargs)

        wrapper.__name__ = func.__name__

        return cli.command(*args, **kwargs)(click.pass_context(wrapper))

    return deco


@command(help='Print version string.')
def version(launch):
    click.echo(launch.version())


@command(help='Verify configuration.')
@click.pass_context
def verify(ctx, launch):
    with open(os.path.join(launch.root, launch.launch_file()), 'rb') as f:
        filedata = yaml.safe_load(f) or {}
    confdata = launch.config.dump()
    for key in confdata:
        filedata.pop(key, None)
    if filedata:
        click.echo(yaml.dump(filedata, default_flow_style=False), nl=False)
        ctx.exit(-1)


def main(type=Launch):
    """명령 실행의 진입 지점.

    launch 를 다른 이름으로 변경하거나, Launch 를 확장하고자 할 때 사용된다.

    type 으로 Launch 를 계승하는 클래스를 전달한다.

    Since version 0.1.
    """
    global _LaunchType
    backup = _LaunchType
    _LaunchType = type
    try:
        cli()
    finally:
        _LaunchType = backup
