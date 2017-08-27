# coding=utf-8
# Copyright 2017 Flowdas Inc. <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os

from click.testing import CliRunner as _CliRunner

from . import cli

__all__ = [
    'simulate_command',
]


def simulate_command(*args, chdir=None, type=None):
    """명령 실행을 시뮬레이트한다.

    chdir 을 제공하면 디렉토리를 변경한 상태에서 실행한 후 돌아온다.

    :py:func:`main` 에 launch_type 을 제공하는 상황도, launch_type 로 시뮬레이트할 수 있다.

    :param args: 명령행 인자들.
    :param chdir: 명령을 실행할 디렉토리.
    :param type: 새로 정의한 Launch 형.
    :return: :py:class:`click.testing.Result` 인스턴스.

    Since version 0.1.
    """

    def run(args):
        os.environ.setdefault('LC_CTYPE', 'ko_KR.UTF-8')
        runner = _CliRunner()
        if type:
            backup = cli._LaunchType
            cli._LaunchType = type
        else:
            backup = None
        try:
            return runner.invoke(cli.cli, args)
        finally:
            if type:
                cli._LaunchType = backup

    if chdir:
        cwd = os.getcwd()
        os.chdir(chdir)
        try:
            return run(args)
        finally:
            os.chdir(cwd)
    else:
        return run(args)
