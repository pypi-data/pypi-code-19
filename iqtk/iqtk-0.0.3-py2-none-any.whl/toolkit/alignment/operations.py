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

import apache_beam as beam

import math
import datetime
import pprint

import inquiry.framework as iqf
from inquiry.framework import bq


def bwa_mem(p, args):
    """Wrapper to simplify use."""
    return p | iqf.task.ContainerTaskRunner(BWAMem(args=args))


class BWAMem(iqf.task.ContainerTask):

    def __init__(self, args):
        """Initialize a container task."""
        container = iqf.task.ContainerTaskResources(
            disk=60, cpu_cores=4, ram=8,
            image='gcr.io/jbei-cloud/aligntools:0.0.1')
        super(BWAMem, self).__init__(task_label='bwa_mem', args=args,
                                        container=container)

    def process(self, file_path, ref_fasta):

        ref_files = gsutil_expand_stem(ref_fasta.split('.fa')[0])

        inputs = [read_pair[0], read_pair[1]]
        inputs.extend(ref_files)

        cmd = util.Command(['bwa', 'mem',
                            '-t', self.container.cpu_cores,
                            f.localize(ref_fasta),
                            f.localize(read_pair[0]),
                            f.localize(read_pair[1]),
                            '>', self.out_path + '/aln.sam'
                            ])

        if generate_bam:

            cmd.chain(['samtools', 'view', '-u',
                              self.out_path + '/aln.sam'])
            cmd.pipe(['samtools', 'sort',
                              '-@', 12,
                              '-O', 'bam',
                              '-T', self.out_path + '/sorted.bam.sort_tmp',
                              '-o', self.out_path + '/sorted.bam',
                              '-'])

        if mark_duplicates:
            metrics_file = self.out_path + '/MarkDuplicates_metrics.txt'
            java_mem = str(int(math.floor(ram)))
            # picard_path = '/home/biodocker/bin/picard.jar'
            picard_path = 'picard'
            cmd.chain([picard_path,
                       'MarkDuplicates',
                       'INPUT=%s/sorted.bam' % self.out_path,
                       'OUTPUT=%s/sorted.deduped.bam' % self.out_path,
                       'ASSUME_SORTED=true',
                       'CREATE_INDEX=true',
                       'MAX_RECORDS_IN_RAM=2000000',
                       'METRICS_FILE=%s' % metrics_file,
                       'REMOVE_DUPLICATES=false'])


        yield self.submit(cmd.txt, inputs=[read_pair[0], read_pair[1]].extend(ref_files),
                          expected_outputs=[{'name': 'sorted.bam', 'type': 'bam'},
                                            {'name': 'aln.sam', 'type': 'sam'},
                                            {'name': 'sorted.deduped.bam', 'type': 'deduped.sam'}])



class AlignmentBQUpload(bq.BQUpload):

    def __init__(self, dataset_name, table_name):

        SCHEMA = [
            # SchemaField('refname', 'STRING', mode='required'),
            # SchemaField('start', 'INTEGER', mode='required'),
            # SchemaField('id', 'STRING', mode='required'),
            # SchemaField('refbases', 'STRING', mode='required'),
            # SchemaField('altbases', 'STRING', mode='required'),
            # SchemaField('quality', 'FLOAT', mode='required'),
            # SchemaField('filter', 'STRING', mode='required'),
            # SchemaField('info', 'STRING', mode='required'),
            # SchemaField('format', 'STRING', mode='required'),
            # SchemaField('balance', 'STRING', mode='required')
        ]

        super(AlignmentBQUpload, self).__init__(SCHEMA, dataset_name, table_name)
