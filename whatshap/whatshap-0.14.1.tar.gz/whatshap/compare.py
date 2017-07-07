"""
Compare two or more phasings
"""
import sys
import logging
import math
from collections import defaultdict, namedtuple
from itertools import chain
from .vcf import VcfReader

logger = logging.getLogger(__name__)

count_width = 9

def add_arguments(parser):
	add = parser.add_argument
	add('--sample', metavar='SAMPLE', default=None, help='Name of the sample '
			'to process. If not given, use first sample found in VCF.')
	add('--names', metavar='NAMES', default=None, help='Comma-separated list '
			'of data set names to be used in the report (in same order as VCFs).')
	add('--tsv-pairwise', metavar='TSVPAIRWISE', default=None, help='Filename to write '
		'comparison results from pair-wise comparison to (tab-separated).')
	add('--tsv-multiway', metavar='TSVMULTIWAY', default=None, help='Filename to write '
		'comparison results from multiway comparison to (tab-separated).')
	add('--only-snvs', default=False, action="store_true", help='Only process SNVs '
		'and ignore all other variants.')
	add('--switch-error-bed', default=None, help='Write BED file with switch error positions '
		'to given filename.')
	add('--plot-blocksizes', default=None, help='Write PDF file with a block length histogram '
		'to given filename (requires matplotlib).')
	add('--longest-block-tsv', default=None, help='Write position-wise agreement of longest '
		'joint blocks in each chromosome to tab-separated file.')
	# TODO: what's the best way to request "two or more" VCFs?
	add('vcf', nargs='+', metavar='VCF', help='At least two phased VCF files to be compared.')


def validate(args, parser):
	if len(args.vcf) < 2:
		parser.error('At least two VCFs need to be given.')


class SwitchFlips:
	def __init__(self, switches=0, flips=0):
		self.switches = switches
		self.flips = flips
	def __iadd__(self, other):
		self.switches += other.switches
		self.flips += other.flips
		return self
	def __repr__(self):
		return 'SwitchFlips(switches={}, flips={})'.format(self.switches, self.flips)
	def __str__(self):
		return '{}/{}'.format(self.switches, self.flips)


class PhasingErrors:
	def __init__(self, switches=0, hamming=0, switch_flips=None):
		self.switches = switches
		self.hamming = hamming
		self.switch_flips = SwitchFlips() if switch_flips is None else switch_flips
	def __iadd__(self, other):
		self.switches += other.switches
		self.hamming += other.hamming
		self.switch_flips += other.switch_flips
		return self
	def __repr__(self):
		return 'PhasingErrors(switches={}, hamming={}, switch_flips={})'.format(self.switches, self.hamming, self.switch_flips)


def complement(s):
	t = { '0': '1', '1':'0' }
	return ''.join(t[c] for c in s)


def hamming(s0, s1):
	assert len(s0) == len(s1)
	return sum( c0!=c1 for c0, c1 in zip(s0, s1) )


def switch_encoding(phasing):
	return ''.join( ('0' if phasing[i-1]==phasing[i] else '1') for i in range(1,len(phasing)) )


def compute_switch_flips(phasing0, phasing1):
	assert len(phasing0) == len(phasing1)
	s0 = switch_encoding(phasing0)
	s1 = switch_encoding(phasing1)
	result = SwitchFlips()
	switches_in_a_row = 0
	for i, (p0, p1) in enumerate(zip(s0, s1)):
		if p0 != p1:
			switches_in_a_row += 1
		if (i + 1 == len(s0)) or (p0 == p1):
			result.flips += switches_in_a_row // 2
			result.switches += switches_in_a_row % 2
			switches_in_a_row = 0
	if False:
		print('switch_flips():')
		print('   phasing0={}'.format(phasing0))
		print('   phasing1={}'.format(phasing1))
		print('         s0={}'.format(s0))
		print('         s1={}'.format(s1))
		print('   switches={}, flips={}'.format(result.switches, result.flips))
	return result


def compare_block(phasing0, phasing1):
	"""Input are two strings over {0,1}. Output is a PhasingErrors object."""
	return PhasingErrors(
		switches = hamming(switch_encoding(phasing0), switch_encoding(phasing1)),
		hamming = min(hamming(phasing0, phasing1), hamming(phasing0, complement(phasing1))),
		switch_flips = compute_switch_flips(phasing0, phasing1)
	)


def fraction2percentstr(nominator, denominator):
	if denominator == 0:
		return '--'
	else:
		return '{:.2f}%'.format(nominator*100.0/denominator)


def safefraction(nominator, denominator):
	if denominator == 0:
		return float('nan')
	else:
		return nominator/denominator


def create_bed_records(chromosome, phasing0, phasing1, positions, annotation_string):
	"""Determines positions of switch errors between two phasings
	and yields one BED record per switch error (encoded as a tuple).
	The annotation_string is added to each record."""
	assert len(phasing0) == len(phasing1) == len(positions)
	switch_encoding0 = switch_encoding(phasing0)
	switch_encoding1 = switch_encoding(phasing1)
	for i, (sw0, sw1) in enumerate(zip(switch_encoding0, switch_encoding1)):
		if sw0 != sw1:
			yield (chromosome, positions[i]+1, positions[i+1]+1, annotation_string)


def print_errors(errors, phased_pairs, print_hamming=False):
	print('    phased pairs of variants assessed:', str(phased_pairs).rjust(count_width))
	print('                        switch errors:', str(errors.switches).rjust(count_width))
	print('                    switch error rate:', fraction2percentstr(errors.switches, phased_pairs).rjust(count_width))
	print('            switch/flip decomposition:', str(errors.switch_flips).rjust(count_width) )
	print('                     switch/flip rate:', fraction2percentstr(errors.switch_flips.switches+errors.switch_flips.flips, phased_pairs).rjust(count_width))


pairwise_comparison_results_fields = [
	'intersection_blocks',
	'covered_variants',
	'all_assessed_pairs',
	'all_switches',
	'all_switch_rate',
	'all_switchflips',
	'all_switchflip_rate',
	'blockwise_hamming',
	'blockwise_hamming_rate',
	'largestblock_assessed_pairs',
	'largestblock_switches',
	'largestblock_switch_rate',
	'largestblock_switchflips',
	'largestblock_switchflip_rate',
	'largestblock_hamming',
	'largestblock_hamming_rate'
]
PairwiseComparisonResults = namedtuple('PairwiseComparisonResults', pairwise_comparison_results_fields)

BlockStats = namedtuple('BlockStats', ['variant_count', 'span'])

def compare(chromosome, variant_tables, sample, dataset_names):
	"""
	Return a PairwiseComparisonResults object if the variant_tables has a length of 2.
	"""
	assert len(variant_tables) > 1
	variants = None
	for variant_table in variant_tables:
		het_variants = [ v for v, gt in zip(variant_table.variants, variant_table.genotypes_of(sample)) if gt == 1 ]
		if variants is None:
			variants = set(het_variants)
		else:
			variants.intersection_update(het_variants)
	print('         common heterozygous variants:', str(len(variants)).rjust(count_width))
	print('         (restricting to these below)')
	phases = []
	sorted_variants = sorted(variants, key=lambda v: v.position)
	for variant_table in variant_tables:
		p = [ phase for variant, phase in zip(variant_table.variants, variant_table.phases_of(sample)) if variant in variants ]
		assert [ v for v in variant_table.variants if v in variants ] == sorted_variants
		assert len(p) == len(variants)
		phases.append(p)

	blocks = [ defaultdict(list) for _ in variant_tables ]
	block_intersection = defaultdict(list)
	for variant_index in range(len(variants)):
		any_none = False
		for i in range(len(phases)):
			phase = phases[i][variant_index]
			if phase is None:
				any_none = True
			else:
				blocks[i][phase.block_id].append(variant_index)
		if not any_none:
			joint_block_id = tuple( phases[i][variant_index].block_id for i in range(len(phases)) )
			block_intersection[joint_block_id].append(variant_index)

	# create statistics on each block in each data set
	block_stats = []
	for i in range(len(variant_tables)):
		l = []
		for block_id, variant_indices in blocks[i].items():
			if len(variant_indices) < 2:
				continue
			span = sorted_variants[variant_indices[-1]].position - sorted_variants[variant_indices[0]].position
			l.append(BlockStats(len(variant_indices), span))
		block_stats.append(l)

	for i in range(len(phases)):
		print('non-singleton blocks in {}:'.format(dataset_names[i]).rjust(38), str(len([b for b in blocks[i].values() if len(b) > 1])).rjust(count_width))
		print('                 --> covered variants:', str(sum(len(b) for b in blocks[i].values() if len(b) > 1)).rjust(count_width))
	intersection_block_count = len([b for b in block_intersection.values() if len(b) > 1])
	intersection_block_variants = sum(len(b) for b in block_intersection.values() if len(b) > 1)
	print('    non-singleton intersection blocks:', str(intersection_block_count).rjust(count_width))
	print('                 --> covered variants:', str(intersection_block_variants).rjust(count_width))
	longest_block = 0
	longest_block_errors = PhasingErrors()
	longest_block_positions = []
	longest_block_agreement = []
	phased_pairs = 0
	bed_records = []
	if len(variant_tables) == 2:
		total_errors = PhasingErrors()
		total_compared_variants = 0
		for block in block_intersection.values():
			if len(block) < 2:
				continue
			phasing0 = ''.join( str(phases[0][i].phase) for i in block )
			phasing1 = ''.join( str(phases[1][i].phase) for i in block )
			block_positions = [ sorted_variants[i].position for i in block ]
			errors = compare_block(phasing0, phasing1)
			bed_records.extend(create_bed_records(chromosome, phasing0, phasing1, block_positions, '{}<-->{}'.format(*dataset_names)))
			total_errors += errors
			phased_pairs += len(block) - 1
			total_compared_variants += len(block)
			if len(block) > longest_block:
				longest_block = len(block)
				longest_block_errors = errors
				longest_block_positions = block_positions
				if hamming(phasing0, phasing1) < hamming(phasing0, complement(phasing1)):
					longest_block_agreement = [1*(p0 == p1) for p0, p1 in zip(phasing0,phasing1) ]
				else:
					longest_block_agreement = [1*(p0 != p1) for p0, p1 in zip(phasing0,phasing1) ]
		longest_block_assessed_pairs = max(longest_block - 1, 0)
		print('              ALL INTERSECTION BLOCKS:', '-'*count_width)
		print_errors(total_errors, phased_pairs)
		print('          Block-wise Hamming distance:', str(total_errors.hamming).rjust(count_width))
		print('      Block-wise Hamming distance [%]:', fraction2percentstr(total_errors.hamming, total_compared_variants).rjust(count_width))
		print('           LARGEST INTERSECTION BLOCK:', '-'*count_width)
		print_errors(longest_block_errors, longest_block_assessed_pairs)
		print('                     Hamming distance:', str(longest_block_errors.hamming).rjust(count_width))
		print('                 Hamming distance [%]:', fraction2percentstr(longest_block_errors.hamming, longest_block).rjust(count_width))
		return PairwiseComparisonResults(
			intersection_blocks = intersection_block_count,
			covered_variants = intersection_block_variants,
			all_assessed_pairs = phased_pairs,
			all_switches = total_errors.switches,
			all_switch_rate = safefraction(total_errors.switches, phased_pairs),
			all_switchflips = total_errors.switch_flips,
			all_switchflip_rate = safefraction(total_errors.switch_flips.switches+total_errors.switch_flips.flips, phased_pairs),
			blockwise_hamming = total_errors.hamming,
			blockwise_hamming_rate = safefraction(total_errors.hamming, total_compared_variants),
			largestblock_assessed_pairs = longest_block_assessed_pairs,
			largestblock_switches = longest_block_errors.switches,
			largestblock_switch_rate = safefraction(longest_block_errors.switches, longest_block_assessed_pairs),
			largestblock_switchflips = longest_block_errors.switch_flips,
			largestblock_switchflip_rate = safefraction(longest_block_errors.switch_flips.switches+longest_block_errors.switch_flips.flips, longest_block_assessed_pairs),
			largestblock_hamming = longest_block_errors.hamming,
			largestblock_hamming_rate = safefraction(longest_block_errors.hamming, longest_block)
		), bed_records, block_stats, longest_block_positions, longest_block_agreement, None
	else:
		histogram = defaultdict(int)
		total_compared = 0
		for block in block_intersection.values():
			if len(block) < 2:
				continue
			total_compared += len(block) - 1
			phasings = [ ''.join( str(phases[j][i].phase) for i in block ) for j in range(len(phases)) ]
			switch_encodings = [ switch_encoding(p) for p in phasings ]
			for i in range(len(block)-1):
				s = ''.join(switch_encodings[j][i] for j in range(len(switch_encodings)) )
				s = min(s, complement(s))
				histogram[s] += 1
		print('           Compared pairs of variants:', str(total_compared).rjust(count_width))
		bipartitions = list(histogram.keys())
		bipartitions.sort()
		multiway_results = {} # (dataset_list0, dataset_list1) --> count
		for i, s in enumerate(bipartitions):
			count = histogram[s]
			if i == 0:
				assert set(c for c in s) == set('0')
				print('                            ALL AGREE:')
			elif i == 1:
				print('                         DISAGREEMENT:')
			left, right = [], []
			for name, leftright in zip(dataset_names,s):
				if leftright == '0':
					left.append(name)
				else:
					right.append(name)
			print(
				('{%s} vs. {%s}:' % (','.join(left),','.join(right))).rjust(38),
				str(count).rjust(count_width),
				fraction2percentstr(count, total_compared).rjust(8)
			)
			multiway_results[(','.join(left),','.join(right))] = count
		return None, None, block_stats, None, None, multiway_results


def create_blocksize_histogram(filename, block_stats, names):
	try:
		import matplotlib
		import numpy
		matplotlib.use('pdf')
		from matplotlib import pyplot
		from matplotlib.backends.backend_pdf import PdfPages
	except ImportError:
		logger.error('To use option --plot-blocksizes, you need to have numpy and matplotlib installed.')
		sys.exit(1)

	assert len(block_stats) == len(names)
	
	color_list = ['#ffa347','#0064c8','#b42222','#22a5b4','#b47c22','#6db6ff']
	if len(color_list) < len(block_stats):
		color_count = len(block_stats)
		color_list = pyplot.cm.Set1([n/color_count for n in range(color_count)])
	colors = color_list[:len(block_stats)]


	with PdfPages(filename) as pdf:
		for what, xlabel in [ (lambda stats: stats.variant_count, 'variant count'), (lambda stats: stats.span, 'span [bp]') ]:
			pyplot.figure(figsize=(10, 8))
			max_value = max(what(stats) for stats in chain(*block_stats))
			common_bins = numpy.logspace(0, math.ceil(math.log10(max_value)), 50)
			for l, name, color in zip(block_stats, names, colors):
				x = [what(stats) for stats in l]
				n, bins, patches = pyplot.hist(x, bins=common_bins, alpha=0.6, color=color, label=name)
			pyplot.xlabel(xlabel)
			pyplot.ylabel('Number of blocks')
			pyplot.gca().set_xscale("log")
			pyplot.gca().set_yscale("log")
			pyplot.grid(True)
			pyplot.legend()
			pdf.savefig()
			pyplot.close()

			pyplot.figure(figsize=(10, 8))
			common_bins = numpy.logspace(0, math.ceil(math.log10(max_value)), 25)
			x = [[what(stats) for stats in l] for l in block_stats]
			n, bins, patches = pyplot.hist(x, bins=common_bins, alpha=0.6, color=colors, label=names)
			pyplot.xlabel(xlabel)
			pyplot.ylabel('Number of blocks')
			pyplot.gca().set_xscale("log")
			pyplot.gca().set_yscale("log")
			pyplot.grid(True)
			pyplot.legend()
			pdf.savefig()
			pyplot.close()
	
	

def run_compare(vcf, names=None, sample=None, tsv_pairwise=None, tsv_multiway=None, only_snvs=False, switch_error_bed=None, plot_blocksizes=None, longest_block_tsv=None):
	vcf_readers = [VcfReader(f, indels=not only_snvs, phases=True) for f in vcf]
	if names:
		dataset_names = names.split(',')
		if len(dataset_names) != len(vcf):
			logger.error('Number of names given with --names does not equal number of VCFs.')
			sys.exit(1)
	else:
		dataset_names = ['file{}'.format(i) for i in range(len(vcf))]
	longest_name = max(len(n) for n in dataset_names)

	all_samples = set()
	sample_intersection = None
	for vcf_reader in vcf_readers:
		if sample_intersection is None:
			sample_intersection = set(vcf_reader.samples)
		else:
			sample_intersection.intersection_update(vcf_reader.samples)
		all_samples.update(vcf_reader.samples)

	if sample:
		sample_intersection.intersection_update([sample])
		if len(sample_intersection) == 0:
			logger.error('Sample %r requested on command-line not found in all VCFs', sample)
			sys.exit(1)
		sample = sample
	else:
		if len(sample_intersection) == 0:
			logger.error('None of the samples is present in all VCFs')
			sys.exit(1)
		elif len(sample_intersection) == 1:
			sample = list(sample_intersection)[0]
		else:
			logger.error('More than one sample is present in all VCFs, please use --sample to specify which sample to work on.')
			sys.exit(1)

	if tsv_pairwise:
		tsv_pairwise_file = open(tsv_pairwise, 'w')
	else:
		tsv_pairwise_file = None

	if tsv_multiway:
		tsv_multiway_file = open(tsv_multiway, 'w')
		print('#sample', 'chromosome', 'dataset_list0', 'dataset_list1', 'count', sep='\t', file=tsv_multiway_file)
	else:
		tsv_multiway_file = None

	if longest_block_tsv:
		longest_block_tsv_file = open(longest_block_tsv, 'w')
		print('#dataset_name0', 'dataset_name1', '#sample', 'chromosome', 'position', 'phase_agreeing', sep='\t', file=longest_block_tsv_file)
	else:
		longest_block_tsv_file = None

	print('Comparing phasings for sample', sample)

	chromosomes = None
	vcfs = []
	for reader, filename in zip(vcf_readers, vcf):
		# create dict mapping chromsome names to VariantTables
		m = dict()
		logger.info('Reading phasing from %r', filename)
		for variant_table in reader:
			m[variant_table.chromosome] = variant_table
		vcfs.append(m)
		if chromosomes is None:
			chromosomes = set(m.keys())
		else:
			chromosomes.intersection_update(m.keys())
	if len(chromosomes) == 0:
		logger.error('No chromosome is contained in all VCFs. Aborting.')
		sys.exit(1)

	logger.info('Chromosomes present in all VCFs: %s', ', '.join(sorted(chromosomes)))

	if tsv_pairwise_file:
		fields = ['#sample', 'chromosome', 'dataset_name0', 'dataset_name1', 'file_name0', 'file_name1']
		fields.extend(pairwise_comparison_results_fields)
		fields.extend(['het_variants0', 'only_snvs'])
		print(*fields, sep='\t', file=tsv_pairwise_file)

	switch_error_bedfile = None
	if switch_error_bed:
		switch_error_bedfile = open(switch_error_bed, 'w')

	print('FILENAMES')
	for name, filename in zip(dataset_names, vcf):
		print(name.rjust(longest_name+2), '=', filename)

	width = max(longest_name, 15) + 5

	all_block_stats = [ [] for _ in vcfs ]
	def add_block_stats(block_stats):
		assert len(block_stats) == len(all_block_stats)
		for big_list, new_list in zip(all_block_stats, block_stats):
			big_list.extend(new_list)

	for chromosome in sorted(chromosomes):
		print('---------------- Chromosome {} ----------------'.format(chromosome))
		all_bed_records = []
		variant_tables = [ vcf[chromosome] for vcf in vcfs ]
		all_variants_union = set()
		all_variants_intersection = None
		het_variants_union = set()
		het_variants_intersection = None
		het_variant_sets = []
		het_variants0 = None
		print('VARIANT COUNTS (heterozygous / all): ')
		for variant_table, name in zip(variant_tables, dataset_names):
			all_variants_union.update(variant_table.variants)
			het_variants = [ v for v, gt in zip(variant_table.variants, variant_table.genotypes_of(sample)) if gt == 1 ]
			if het_variants0 is None:
				het_variants0 = len(het_variants)
			het_variants_union.update(het_variants)
			if all_variants_intersection is None:
				all_variants_intersection = set(variant_table.variants)
				het_variants_intersection = set(het_variants)
			else:
				all_variants_intersection.intersection_update(variant_table.variants)
				het_variants_intersection.intersection_update(het_variants)
			het_variant_sets.append(set(het_variants))
			print('{}:'.format(name).rjust(width), str(len(het_variants)).rjust(count_width), '/', str(len(variant_table.variants)).rjust(count_width))
		print('UNION:'.rjust(width), str(len(het_variants_union)).rjust(count_width), '/', str(len(all_variants_union)).rjust(count_width))
		print('INTERSECTION:'.rjust(width), str(len(het_variants_intersection)).rjust(count_width), '/', str(len(all_variants_intersection)).rjust(count_width))

		for i in range(len(vcfs)):
			for j in range(i+1, len(vcfs)):
				print('PAIRWISE COMPARISON: {} <--> {}:'.format(dataset_names[i],dataset_names[j]))
				results, bed_records, block_stats, longest_block_positions, longest_block_agreement, multiway_results = compare(chromosome, [variant_tables[i], variant_tables[j]], sample, [dataset_names[i], dataset_names[j]])
				if len(vcfs) == 2:
					add_block_stats(block_stats)
				all_bed_records.extend(bed_records)
				if tsv_pairwise_file:
					fields = [sample, chromosome, dataset_names[i], dataset_names[j], vcf[i], vcf[j]]
					fields.extend(results)
					fields.extend([het_variants0, int(only_snvs)])
					print(*fields, sep='\t', file=tsv_pairwise_file)
				if longest_block_tsv_file:
					assert len(longest_block_positions) == len(longest_block_agreement)
					for position, phase_agreeing in zip(longest_block_positions, longest_block_agreement):
						print(dataset_names[i], dataset_names[j], sample, chromosome, position, phase_agreeing, sep='\t', file=longest_block_tsv_file)

		# if requested, write all switch errors found in the current chromosome to the bed file
		if switch_error_bedfile:
			all_bed_records.sort()
			for record in all_bed_records:
				print(*record, sep='\t', file=switch_error_bedfile)

		if len(vcfs) > 2:
			print('MULTIWAY COMPARISON OF ALL PHASINGS:')
			results, bed_records, block_stats, longest_block_positions, longest_block_agreement, multiway_results = compare(chromosome, variant_tables, sample, dataset_names)
			add_block_stats(block_stats)
			if tsv_multiway_file:
				for (dataset_list0, dataset_list1), count in multiway_results.items():
					print(sample, chromosome, '{'+dataset_list0+'}', '{'+dataset_list1+'}', count, sep='\t', file=tsv_multiway_file)

	if plot_blocksizes:
		create_blocksize_histogram(plot_blocksizes, all_block_stats, dataset_names)

	if tsv_pairwise:
		tsv_pairwise_file.close()

	if tsv_multiway:
		tsv_multiway_file.close()

	if switch_error_bed:
		switch_error_bedfile.close()

	if longest_block_tsv_file:
		longest_block_tsv_file.close()


def main(args):
	run_compare(**vars(args))
