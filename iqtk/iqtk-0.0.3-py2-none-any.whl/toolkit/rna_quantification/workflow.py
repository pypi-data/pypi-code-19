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
"""Containerized transcriptome analysis pipeline."""

from __future__ import absolute_import

from apache_beam.pvalue import AsList
import apache_beam as beam

import inquiry.toolkit.rna_quantification.operations as ops
from inquiry.framework.workflow import Workflow
from inquiry.framework import util
from inquiry.framework import task


class TranscriptomicsWorkflow(Workflow):
    """Quantify transcript levels using the Tophat/Cufflinks/Cuffdiff pipeline."""

    def __init__(self):
        """Initialize a workflow."""
        self.tag = 'tuxedo-transcriptomics'
        self.arg_template = {
            'ref_fasta': {
                'help': 'a reference fasta'
            },
            'genes_gtf': {
                'help': 'a genes gtf file'
            },
            'cond_a_pairs': {
                'help': 'read pairs for condition a'
            },
            'cond_b_pairs': {
                'help': 'read pairs for condition b'
            },
            'bq_dataset_name': {
                'help': 'the name of a bigquery dataset'
            },
            'bq_table_name': {
                'help': 'the name of a bigquery table'
            }
        }

        super(TranscriptomicsWorkflow, self).__init__()

    def define(self):
        """Define the transcriptome analysis workflow.

        Perform split-read alignment, assemble transcripts, and obtain differential
        abundance measures of features across conditions.

        Args:
            ref_fasta (string): Path to a reference sequence file.
            genes_gtf (string): Path to a reference gene annotation.
            cond_a_pairs (list): A list of read pairs for the A condition.
            cond_b_pairs (list): A list of read pairs for the B condition

        Todo:
            * Tutorial on docs site.

        .. _Trapnell et al. (2012):
           http://www.nature.com/nprot/journal/v7/n3/full/nprot.2012.016.html
        """
        p, args = self.p, self.args

        # For each condition, create a PCollection to store the input read pairs.
        reads_a = util.fc_create(p, args.cond_a_pairs)
        reads_b = util.fc_create(p, args.cond_b_pairs)

        # For each pair of reads, use tophat to perform split-read alignment.
        # Condition A.
        th_a = (reads_a | task.ContainerTaskRunner(
            ops.TopHat(args=args,
                       ref_fasta=args.ref_fasta,
                       genes_gtf=args.genes_gtf,
                       tag='cond_a')
            ))

        th_b = (reads_b | task.ContainerTaskRunner(
            ops.TopHat(args=args,
                       ref_fasta=args.ref_fasta,
                       genes_gtf=args.genes_gtf,
                       tag='cond_b')
            ))

        # Subset the outputs of the tophat steps to obtain only the bam (alignment)
        # files. Then combine the collections.
        align_a = util.match(th_a, {'file_type': 'bam'})
        align_b = util.match(th_b, {'file_type': 'bam'})
        align = util.combine(p, (align_a, align_b))

        # For each set of reads, perform a transcriptome assembly with cufflinks,
        # yielding one gtf feature annotation for each input read set.
        cl = (align | task.ContainerTaskRunner(
            ops.Cufflinks(args=args)
            ))

        # Perform a single `cuffmerge` operation to merge all of the gene
        # annotations into a single annotation.
        cm = (util.union(util.match(cl, {'file_type': 'transcripts.gtf'}))
              | task.ContainerTaskRunner(
                  ops.CuffMerge(args=args,
                                ref_fasta=args.ref_fasta,
                                genes_gtf=args.genes_gtf)
                  ))

        # Run a single cuffdiff operation comparing the prevalence of features in
        # the input annotatio across conditions using reads obtained for those
        # conditions.
        cd = ops.cuffdiff(util.match(cm, {'file_type': 'gtf'}),
                          ref_fasta=args.ref_fasta,
                          args=args,
                          cond_a_bams=AsList(align_a),
                          cond_b_bams=AsList(align_b))

        (util.match(cd, {'file_type': 'differentialExpressionCSV'})
        | 'bq-upload' >> beam.ParDo(
             ops.DiffExBQUpload(args.bq_dataset_name, args.bq_table_name)
             ))

        return cd


def run(config=None):
    """Run as a Dataflow."""
    TranscriptomicsWorkflow().run(config)

if __name__ == '__main__':
    run(sys.argv[1])
