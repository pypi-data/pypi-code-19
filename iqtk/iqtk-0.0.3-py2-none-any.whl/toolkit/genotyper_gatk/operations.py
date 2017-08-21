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

from inquiry.framework.util import localize
from inquiry.framework.util import gsutil_expand_stem
from google.cloud.bigquery import SchemaField
from inquiry.framework import task
from inquiry.framework import util
from inquiry.framework import bq


class CombinedSamtoolsGenotyper(task.ContainerTask):

    def __init__(self, args, ref_fasta, generate_bam=True, mark_duplicates=True):
        """Initialize a container task."""
        self.ref_fasta = ref_fasta
        self.generate_bam = generate_bam
        self.mark_duplicates = mark_duplicates
        container = task.ContainerTaskResources(
            disk=60, cpu_cores=4, ram=8,
            image='gcr.io/jbei-cloud/aligntools:0.0.1')
        super(CombinedSamtoolsGenotyper, self).__init__(
            task_label='pileup-genotyper', args=args, container=container)

    def process(self, read_pair):

        prefix = task.Prefixer()

        local_read_1 = localize(read_pair[0])
        local_read_2 = localize(read_pair[1])

        ref_gs_stem = self.ref_fasta.split('.fa')[0]
        ref_files = gsutil_expand_stem(ref_gs_stem)

        intermediate_sam = self.out_path + '/aln.sam'
        intermediate_bam_sort = self.out_path + '/sorted.bam.sort_tmp'

        output_raw_bcf = prefix.apply(self.out_path + '/var.raw.bcf')
        output_filt_vcf = prefix.apply(self.out_path + '/var.flt.vcf')
        output_vcf_header = output_filt_vcf + '.header'
        output_vcf_body = output_filt_vcf + '.body'
        output_bam = prefix.apply(self.out_path + '/sorted.bam')

        inputs = [read_pair[0], read_pair[1]]
        inputs.extend(ref_files)
        ref_dir = self.out_path + '/ref'

        cmd = util.Command(['mkdir', ref_dir])
        for i in ref_files:
            cmd.chain(['cp', localize(i), ref_dir])

        local_ref = localize(self.ref_fasta, ref_dir)

        cmd.chain(['bwa', 'mem',
                   '-t', self.container.cpu_cores,
                   local_ref,
                   local_read_1,
                   local_read_2,
                   '>', intermediate_sam])

        if self.generate_bam:
            cmd.chain(['samtools', 'view', '-u',
                       self.out_path + '/aln.sam'])
            cmd.pipe(['samtools', 'sort',
                              '-@', 12,
                              '-O', 'bam',
                              '-T', intermediate_bam_sort,
                              '-o', output_bam,
                              '-'])

        if self.mark_duplicates:

            tmp_sorted_bam = prefix.apply(
                self.out_path + '/sorted.deduped.bam')
            metrics_file = prefix.apply(
                self.out_path + '/MarkDuplicates_metrics.txt')

            cmd.chain(['picard',
                       'MarkDuplicates',
                       'INPUT=%s' % output_bam,
                       'OUTPUT=%s' % tmp_sorted_bam,
                       'ASSUME_SORTED=true',
                       'CREATE_INDEX=true',
                       'MAX_RECORDS_IN_RAM=2000000',
                       'METRICS_FILE=%s' % metrics_file,
                       'REMOVE_DUPLICATES=false'])

            cmd.chain(['cp', tmp_sorted_bam, output_bam])

        cmd.chain(['samtools', 'mpileup', '-uf', local_ref, output_bam])
        cmd.pipe(['bcftools', 'view', '-O', 'b', '-', '>', output_raw_bcf])

        cmd.chain(['bcftools', 'view', output_raw_bcf])
        cmd.pipe(['vcfutils.pl', 'varFilter', '-D100', '>', output_filt_vcf])

        vcf_header = output_filt_vcf + '.header'
        vcf_body = output_filt_vcf + '.body'

        #for i in intermediates:
        cmd.chain(["rm", intermediate_sam])

        cmd.chain(["grep", "'^##'", output_filt_vcf,
                   ">", output_vcf_header])

        cmd.chain(["grep", "-v", "'^##'", output_filt_vcf,
                   ">", output_vcf_body])

        cmd.chain([
            'cat', output_vcf_body,
            '| tr "," ";" | tr "\t" "," | tail -n +2',
            '>', output_vcf_body + '.csv'
        ])

        yield task.submit(self, cmd.txt, inputs=inputs,
                          expected_outputs=[{'name': output_vcf_header,
                                             'file_type': 'VCFHeader'},
                                            {'name': output_vcf_body + '.csv',
                                             'file_type': 'VCFBody'},
                                            {'name': output_filt_vcf,
                                             'file_type': 'vcf'},
                                            {'name': output_raw_bcf,
                                             'file_type': 'bcf'},
                                            {'name': 'metrics.txt',
                                             'file_type': 'metrics.txt'},
                                            {'name': output_bam,
                                             'file_type': 'bam'}])


class GenotypeBQUpload(bq.BQUpload):

    def __init__(self, dataset_name, table_name):

        SCHEMA = [
            SchemaField('refname', 'STRING', mode='required'),
            SchemaField('start', 'INTEGER', mode='required'),
            SchemaField('id', 'STRING', mode='required'),
            SchemaField('refbases', 'STRING', mode='required'),
            SchemaField('altbases', 'STRING', mode='required'),
            SchemaField('quality', 'FLOAT', mode='required'),
            SchemaField('filter', 'STRING', mode='required'),
            SchemaField('info', 'STRING', mode='required'),
            SchemaField('format', 'STRING', mode='required'),
            SchemaField('balance', 'STRING', mode='required')
        ]

        super(GenotypeBQUpload, self).__init__(SCHEMA, dataset_name, table_name)
