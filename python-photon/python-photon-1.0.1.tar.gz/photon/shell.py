# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2017 Cisco Systems, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import click

import photon
from photon.config import Config, ConfigError
from photon.provisioner import Provisioner


@click.command()
@click.version_option(version=photon.__version__)
@click.argument('workflow')
@click.argument('az')
@click.option(
    '--config',
    default='photon.yml',
    type=click.Path(exists=True),
    help='path to the photon config')
@click.option(
    '--resume',
    default=1,
    help='playbook position to start at within workflow')
def main(az, workflow, resume, config):
    try:
        c = Config(az=az, workflow=workflow, config_file=config)
    except ConfigError as e:
        raise click.UsageError(str(e))

    p = Provisioner(c)
    p.run(resume)


if __name__ == '__main__':
    main()
