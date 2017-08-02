"""Given a FASTQ file (or pair of) work out BQ and GC bias values.

BQ -> for each read, keeping track of pair1 or pair2, create a 2D array of BQ vs base position
      Output as both raw count matrices as well as a cumulative probablity distribution

GC -> For each read, keeping track of pair1 and pair2, compute GC content fraction and keep
      a count histogram. Also save this as a normalized distribution with 1.0 being the
      average coverage
"""
import time

import numpy as np
import pysam

import logging
logger = logging.getLogger(__name__)


def gcbq_fastq(fastq_name, max_bq=94, max_bp=300, gc_bins=100):
  fastq_fp = pysam.FastxFile(fastq_name)
  bq_mat = np.zeros((max_bp, max_bq), dtype=np.uint64)
  gc_mat = np.zeros(gc_bins, dtype=np.uint64)
  t0 = time.time()
  n = 0
  for n, r in enumerate(fastq_fp):
    bq = r.get_quality_array()
    bq_mat[:len(bq), bq] += 1

    seq = r.sequence
    gc_mat[int(gc_bins * float(seq.count('G') + seq.count('C')) / len(seq))] += 1
  t1 = time.time()

  logger.debug('Took {}s to parse {} reads ({} r/s)'.format(t1 - t0, n, n/(t1 - t0)))

  return bq_mat, gc_mat
