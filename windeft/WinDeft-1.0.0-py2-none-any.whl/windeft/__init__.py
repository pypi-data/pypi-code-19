# Copyright 2017 Alex Hadi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import click
import os
from subprocess import *
import sys


@click.command()
@click.option("-p", "-path", required=True, type=str, help="Specify path to scan.")
def cli(path):
    try:
        os.chdir("C:\\Program Files\\Windows Defender")
    except WindowsError:
        click.echo("Windows Defender does not exist!")
        sys.exit(1)

    try:
        os.path.exists(path)
    except WindowsError:
        click.echo("The path to scan is invalid!")

    # Checks Windows Defender command for non-zero exit code.
    try:
        cmd = check_output('MpCmdRun.exe -Scan -File "{0}"'.format(path))
        click.echo("The exit code is zero. The scan found nothing malicious.")
        sys.exit(0)
    except CalledProcessError as cpe:
        click.echo("A non-zero exit code was returned!")
        sys.exit(cpe.returncode)
