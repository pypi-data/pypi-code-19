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

import inquiry.framework as iq

def genotype(p, args):
    """Wrapper to simplify use."""
    return p | task.ContainerTaskRunner(CombinedSamtoolsGenotyper(args=args))


class CombinedSamtoolsGenotyper(iq.task.ContainerTask):

    def __init__(self, args):
        """Initialize a container task."""
        container = iq.task.ContainerTaskResources(
            disk=60, cpu_cores=4, ram=8,
            image='gcr.io/jbei-cloud/aligntools:0.0.1')
        super(CombinedSamtoolsGenotyper, self).__init__(
            task_label='pileup-genotyper', args=args, container=container)

    def process(self, file_path):

        ref_gs_stem = ref_fasta.split('.fa')[0]
        ref_files = gsutil_expand_stem(ref_gs_stem)

        output_raw_bcf = self.out_path + '/var.raw.bcf'
        output_filt_vcf = self.out_path + '/var.flt.vcf'

        inputs = [read_pair[0], read_pair[1]]
        inputs.extend(ref_files)

        cmd = util.Command(['bwa', 'mem',
                            '-t', cpu_cores,
                            localize(ref_fasta),
                            localize(read_pair[0]),
                            localize(read_pair[1]),
                            '>', self.out_path + '/aln.sam'])

        if generate_bam:

            cmd.chain(['samtools', 'view', '-u',
                       self.out_path + '/aln.sam'])
            cmd.pipe(['samtools', 'sort',
                              '-@', 12,
                              '-O', 'bam',
                              '-T', self.out_path + '/sorted.bam.sort_tmp',
                              '-o', self.out_path + '/sorted.bam',
                              '-'])

        # If we don't set mark_duplicates and run the de-duplication step the bam
        # used in subsequent gentyping will just be this sorted bam.
        bam = self.out_path + '/sorted.bam'

        if mark_duplicates:

            bam = self.out_path + '/sorted.deduped.bam'

            metrics_file = self.out_path + '/MarkDuplicates_metrics.txt'

            cmd.chain(['picard',
                       'MarkDuplicates',
                       'INPUT=%s/sorted.bam' % self.out_path,
                       'OUTPUT=%s' % bam,
                       'ASSUME_SORTED=true',
                       'CREATE_INDEX=true',
                       'MAX_RECORDS_IN_RAM=2000000',
                       'METRICS_FILE=%s' % metrics_file,
                       'REMOVE_DUPLICATES=false'])

        cmd.chain(['samtools', 'mpileup', '-uf', localize(ref_fasta), bam])
        cmd.pipe(['bcftools', 'view', '-O', 'b', '-', '>', output_raw_bcf])

        cmd.chain(['bcftools', 'view', output_raw_bcf])
        cmd.pipe(['vcfutils.pl', 'varFilter', '-D100', '>', output_filt_vcf])

        vcf_header = output_filt_vcf + '.header'
        vcf_body = output_filt_vcf + '.body'

        cmd.chain(["rm", "/mnt/data/output/aln.sam"])
        cmd.chain(["grep", "'^##'", output_filt_vcf, ">", vcf_header])
        cmd.chain(["grep", "-v", "'^##'", output_filt_vcf, ">", vcf_body])

        # TODO: So obviously will be refactoring this to be less repetitive.
        yield self.submit(cmd, inputs=[file_path],
                          expected_outputs=[{'name': 'var.flt.vcf.header',
                                             'type': 'header.vcf'},
                                            {'name': 'var.flt.vcf.body',
                                             'type': 'body.vcf'},
                                            {'name': 'var.flt.vcf',
                                             'type': 'vcf'},
                                            {'name': 'var.raw.bcf',
                                             'type': 'bcf'},
                                            {'name': 'metrics.txt',
                                             'type': 'metrics.txt'},
                                            {'name': 'sorted.deduped.bam',
                                             'type': 'bam'},
                                            {'name': 'sorted.deduped.bai',
                                             'type': 'bai'}])
