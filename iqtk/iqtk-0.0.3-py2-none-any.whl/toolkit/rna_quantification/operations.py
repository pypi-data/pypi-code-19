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
import logging

from inquiry.framework import task
from inquiry.framework import util
from inquiry.framework.util import localize
from inquiry.framework.util import localize_set
from inquiry.framework import gcp
from inquiry.framework import bq
from google.cloud.bigquery import SchemaField


class TopHat(task.ContainerTask):

    def __init__(self, args, ref_fasta, genes_gtf, tag=None):
        """Initialize a containerized task."""
        self.ref_fasta = ref_fasta
        self.genes_gtf = genes_gtf
        container = task.ContainerTaskResources(
            disk=60, cpu_cores=4, ram=8,
            image='gcr.io/jbei-cloud/tophat:0.0.1')
        super(TopHat, self).__init__(task_label='tophat',
                                     args=args,
                                     container=container)

    def process(self, read_pair):

        prefix = task.Prefixer()

        ref_local_stem = localize(self.ref_fasta).split('.')[0]
        ref_gs_stem = self.ref_fasta.split('.fa')[0]
        ref_files = util.gsutil_expand_stem(ref_gs_stem)

        genes_gtf = localize(self.genes_gtf)
        read_1 = localize(read_pair[0])
        read_2 = localize(read_pair[1])

        output_bam = localize('accepted_hits.bam', self.out_path)
        align_summary = localize('align_summary.txt', self.out_path)
        deletions_bed = localize('junctions.bed', self.out_path)
        insertions_bed = localize('junctions.bed', self.out_path)
        junctions_bed = localize('junctions.bed', self.out_path)

        inputs = list(set().union([self.genes_gtf, read_pair[0], read_pair[1]],
                                  ref_files))

        # If the bowtie2 reference indexes are not present, generate them.
        logging.info([thing for thing in ref_files if thing.endswith('.bt2l')])
        if len([thing for thing in ref_files if thing.endswith('.bt2l')]) == 0:
            logging.error('The provided reference must be accompanied by '
                          'bowtie2 index files sharing the same stem '
                          'as the provided reference path, i.e. '
                          '%s' % ref_gs_stem)
            # TODO: Conditionally perform the indexing if the right indexes
            # are not present.

        cmd = util.Command(['tophat',
                          '-p', self.container.cpu_cores,
                          '-G', genes_gtf,
                          '-o', self.out_path,
                          ref_local_stem,
                          read_1,
                          read_2])

        tmp = output_bam
        output_bam = prefix.apply(output_bam)
        cmd.chain(['mv', tmp, output_bam])

        yield task.submit(self, cmd.txt, inputs=inputs,
                          expected_outputs=[{'name': prefix.apply('accepted_hits.bam'),
                                             'file_type': 'bam'},
                                            {'name': 'align_summary.txt',
                                             'file_type': 'txt'},
                                            {'name': 'deletions.bed',
                                             'file_type': 'bed'},
                                            {'name': 'insertions.bed',
                                             'file_type': 'bed'},
                                            {'name': 'junctions.bed',
                                             'file_type': 'bed'},
                                            {'name': 'prep_reads.info',
                                             'file_type': 'info'}])


class Cufflinks(task.ContainerTask):

    def __init__(self, args):
        """Initialize a containerized task."""
        container = task.ContainerTaskResources(
            disk=60, cpu_cores=4, ram=8,
            image='quay.io/iqtk/cufflinks:0.0.3')
            #image='quay.io/biocontainers/cufflinks')
            #image='ubuntu:16.04')
            #image='gcr.io/jbei-cloud/cufflinks:0.0.2')
        super(Cufflinks, self).__init__(task_label='cufflinks',
                                        args=args,
                                        container=container)

    def process(self, file_path):

        #cmd = util.Command(['tree /mnt/data/input'])
        # cmd = util.Command(['which cufflinks'])

        cmd = util.Command(['cufflinks',
                       '-p', self.container.cpu_cores,
                       '-o', self.out_path,
                       util.localize(file_path)])

        # cmd.chain(['tree /mnt/data/input'])

        inputs = list(set().union(file_path))
        # inputs = []

        yield task.submit(self, cmd.txt, inputs=inputs,
                          expected_outputs=[{'name': 'genes.fpkm_tracking',
                                             'file_type': 'fpkm'},
                                            {'name': 'genes.fpkm_tracking',
                                             'file_type': 'fpkm'},
                                            {'name': 'skipped.gtf',
                                             'file_type': 'skipped.gtf'},
                                            {'name': 'transcripts.gtf',
                                             'file_type': 'transcripts.gtf'}])

class CuffMerge(task.ContainerTask):

    def __init__(self, args, ref_fasta, genes_gtf):
        """Initialize a containerized task."""
        self.ref_fasta = ref_fasta
        self.genes_gtf = genes_gtf
        container = task.ContainerTaskResources(
            disk=60, cpu_cores=4, ram=8,
            image='quay.io/iqtk/cufflinks:0.0.3')
        super(CuffMerge, self).__init__(task_label='cuffmerge',
                                        args=args,
                                        container=container)

    def process(self, assemblies):

        assemblies_txt = '%s/assemblies.txt' % self.out_path

        cmd = util.Command(['cp', localize(self.ref_fasta), self.out_path])

        inputs = list(set().union([self.genes_gtf, self.ref_fasta]))

        for assembly in assemblies:
            cmd.chain(['echo', localize(assembly), '>>',
                                   assemblies_txt])
            inputs.extend([assembly])

        cmd.chain(['cuffmerge',
                   '-g', localize(self.genes_gtf),
                   '-s', localize(self.ref_fasta, local_stem=self.out_path),
                   '-p', 8,
                   '-o', self.out_path,
                   assemblies_txt])

        yield task.submit(self, cmd.txt, inputs=inputs,
                          expected_outputs=[{'name': 'merged.gtf',
                                             'file_type': 'gtf'}])


class CuffDiff(task.ContainerTask):
    def __init__(self, args):
        """Initialize a containerized task."""
        container = task.ContainerTaskResources(
            disk=60, cpu_cores=4, ram=8,
            image='quay.io/iqtk/cufflinks:0.0.3')
        super(CuffDiff, self).__init__(task_label='cuffdiff',
                                       args=args,
                                       container=container)


def cuffdiff(pc, args, ref_fasta, cond_a_bams, cond_b_bams, label="cuffdiff",
             tag=None, debug=False):
    label = util.update_label_if_tag(label, tag)
    res = (pc
           | util.dev_ladd(label, 'crun') >> beam.FlatMap(_cuffdiff_fn,
                                                  ref_fasta=ref_fasta,
                                                  args=args,
                                                  cond_a_bams=cond_a_bams,
                                                  cond_b_bams=cond_b_bams)
           | util.dev_ladd(label, 'wait') >> beam.FlatMap(gcp.poll_until_complete)
           | util.dev_ladd(label, 'verify') >> beam.FlatMap(gcp.verify))
    return res


def _cuffdiff_fn(genes_gtf, ref_fasta, args, cond_a_bams, cond_b_bams,
                 output_tag='cuffout', cpu_cores=8, ram=8, subset=None,
                 disk=20):

    cd_task = CuffDiff(args)

    inputs = util.prepare_inputs([util.gsutil_expand_stem(ref_fasta),
                                  cond_a_bams, cond_b_bams, genes_gtf])

    cond_a = ','.join(util.localize_set(cond_a_bams))
    cond_b = ','.join(util.localize_set(cond_b_bams))

    cmd = util.Command(['cp', localize(ref_fasta), cd_task.out_path])
    cmd.chain(['cuffdiff',
               '-o', cd_task.out_path,
               '-b', localize(ref_fasta, local_stem=cd_task.out_path),
               '-p', cpu_cores,
               '-L', 'C1,C2',
               '-u',  localize(genes_gtf),
               cond_a, cond_b])

    cmd.chain([
        'cat', cd_task.out_path + '/gene_exp.diff',
        '| tr "," ";" | tr "\t" "," | tail -n +2',
        '>', cd_task.out_path + '/gene_exp.diff.csv'
    ])

    yield task.submit(cd_task, cmd.txt, inputs, expected_outputs=[
        {'name': 'genes.count_tracking'},
        {'name': 'genes.fpkm_tracking'},
        {'name': 'genes.read_group_tracking'},
        {'name': 'read_groups.info'},
        {'name': 'run.info'},
        {'name': 'gene_exp.diff',
         'file_type': 'differentialExpression'},
        {'name': 'gene_exp.diff.csv',
         'file_type': 'differentialExpressionCSV'}
        ])


class DiffExBQUpload(bq.BQUpload):

    def __init__(self, dataset_name, table_name):

        SCHEMA = [
            SchemaField('id', 'STRING', mode='required'),
            SchemaField('geneid', 'STRING', mode='required'),
            SchemaField('gene', 'STRING', mode='required'),
            SchemaField('locus', 'STRING', mode='required'),
            SchemaField('sample1', 'STRING', mode='required'),
            SchemaField('sample2', 'STRING', mode='required'),
            SchemaField('status', 'STRING', mode='required'),
            SchemaField('expression1', 'FLOAT', mode='required'),
            SchemaField('expression2', 'FLOAT', mode='required'),
            SchemaField('lnFoldChange', 'FLOAT', mode='required'),
            SchemaField('testStatistic', 'FLOAT', mode='required'),
            SchemaField('pValue', 'FLOAT', mode='required'),
            SchemaField('qValue', 'FLOAT', mode='required'),
            SchemaField('significant', 'BOOLEAN', mode='required')
        ]

        super(DiffExBQUpload, self).__init__(SCHEMA, dataset_name, table_name)
