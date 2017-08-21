
# Copyright 2017 The Regents of the University of California
#
# Licensed under the BSD-3-clause license (the "License"); you may not
# use this file except in compliance with the License.
# You are provided a copy of the license in LICENSE.md at the root of
# this project.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Command-line interface"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import click


@click.group()
def cli():
    pass

@cli.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.argument('bucket', default=None, required=True)
def analyze_bucket(bucket):
    """Align sequences to a reference."""
    pass

@cli.group()
def run():
    """Run an analytical workflow."""
    pass

@run.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.option('--config', default=None, required=True)
def alignment(config):
    """Align sequences to a reference."""
    from inquiry.toolkit.alignment.workflow import run
    run(config)

@run.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.option('--config', default=None, required=True)
def metabolomics(config):
    from inquiry.toolkit.metabolomics.workflow import run
    run(config)

@run.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.option('--config', default=None, required=True)
def assemble_plasmid(config):
    """Assemble a genome or other sequence."""
    from inquiry.toolkit.assemble.workflow import run
    run(config)

@run.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.option('--config', default=None, required=True)
def transcriptomics(config):
    """(Differential) quantification of transcript levels."""
    from inquiry.toolkit.rna_quantification.workflow import run
    run(config)

@run.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.option('--config', default=None, required=True)
def genotype(config):
    """Determine genotypes from sequence data."""
    from inquiry.toolkit.genotyper_gatk.workflow import run
    run(config)

@run.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.option('--config', default=None, required=True)
def transfer(config):
    """Coordinate complex data transfers."""
    from inquiry.toolkit.transfer.workflow import run
    run(config)

def main():
    cli(obj={})
