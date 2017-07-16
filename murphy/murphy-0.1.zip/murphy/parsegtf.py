# Copyright 2016 Suzy M. Stiegelmeyer
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
'''
parsegtf is a set of utilities that use the intervaltree algorithm to
place a gtf file or bed file into the interval overlap tree.
'''
# Version history
# 2016-05-12	S. Stiegelmeyer	Initial version
# 2017-01-05	S. Stiegelmeyer	Add some comments
# 2017-07-15    C. Calloway     Flake8
# 2017-07-15    S. Stiegelmeyer Add document strings

import numpy
import matplotlib.pyplot

from murphy import attributehandler
from murphy.Tree import intervalTree

matplotlib.style.use('ggplot')


def getKeySort(item):
    '''
    Return the first item in a tuple to be used for sorting
    Input:
    item - tuple or list
    Output:
    first element of item
    '''
    return item[0]


def makeintrons(elist):
    """
    From a list of exon coordinates [(start,end), ...], create the list
    of introns
    Input:
    elist - a list of exon coordinates tuples, i.e., [(start,end), ...]
    Output:
    Returns a list of intron coordinate tuples
    """
    ilist = []
    elist = sorted(elist, key=getKeySort)
    for i in list(range(len(elist)-1)):
        isrt = elist[i][1]+1
        istp = elist[i+1][0]-1
        ilist.append((isrt, istp))
    return ilist


def makeExonIntronTree(gtf, pchrom):
    '''
    Make an interval overlap tree from a GTF file where the users would like to
    identify whether or not a region overlaps with a coding region or a non
    coding region of a gene. First transcripts will be formed by extracting the
    exons that belong to the same transcript. The transcript list will be
    sorted and then genomic coordinates for the intron regions will be
    calculated. Individual interval trees will be created for each chromosome
    in the gtf file.  This function then returns a dictionary containing the
    root of the chromosome trees indexed by chromosome.
    Input:
        gtf - gene annotation file in gtf format.  Transcript_id and gene_id
              are required in the gtf attribute field.
        pchrom - chromosome or None.  If not None then only annotations for the
                 specified chromosome will be returned in a tree.
    Output:
        dictionary of interval trees where the key is the chromosome and the
        value is the root of the interval tree
    '''
    gfh = open(gtf, "rU")
    genes = {}
    for line in gfh:
        fields = line.strip().split('\t')
        chrom = fields[0]
        if pchrom is not None and pchrom != chrom:
            continue
        posstrt = int(fields[3])
        posstop = int(fields[4])
        strand = fields[6]
        attributes = attributehandler.parseAttributesGTF(fields[8])
        genenm = attributes['gene_id']
        transcript = attributes['transcript_id']
        genes.setdefault(transcript, dict()).setdefault('exon', list()) \
             .append((posstrt, posstop))
        genes.setdefault(transcript, dict()).setdefault('chrom', chrom)
        genes.setdefault(transcript, dict()).setdefault('strand', strand)
        genes.setdefault(transcript, dict()).setdefault('gene', genenm)
    gfh.close()
    treeroots = {}
    for transcript in genes:
        elist = genes[transcript]['exon']
        elist = sorted(elist, key=getKeySort)
        ilist = makeintrons(elist)
        chrom = genes[transcript]['chrom']
        if chrom in treeroots:
            root = treeroots[chrom]
        else:
            root = None
        for i, exon in enumerate(elist):
            if genes[transcript]['strand'] == '+':
                exord = 'exon' + str(i)
            else:
                exord = 'exon' + len(elist)-i-1
            node = intervalTree.Tree(mi=exon[0],
                                     ma=exon[1],
                                     name=transcript,
                                     name2=genes[transcript]['gene'],
                                     strand=genes[transcript]['strand'],
                                     misc=exord)
            root = node.insertTree(root)
            treeroots[chrom] = root
        for i, intron in enumerate(ilist):
            if genes[transcript]['strand'] == '+':
                inord = 'intron' + str(i)
            else:
                inord = 'intron' + len(ilist)-1-i
            node = intervalTree.Tree(mi=intron[0],
                                     ma=intron[1],
                                     name=transcript,
                                     name2=genenm,
                                     strand=genes[transcript]['strand'],
                                     misc=inord)
            root = node.insertTree(root)
            treeroots[chrom] = root
    return treeroots


def makeExonIntronTreePos(gtf, pchrom):
    '''
    Make an interval overlap tree from a GTF file where the users would like to
    identify whether or not a region overlaps with a coding region or a non
    coding region of a gene. In addition, first, middle and last exon/intron is
    identified in the node.misc field. First transcripts will be formed by
    extracting the exons that belong to the same transcript. The transcript
    list will be sorted and then genomic coordinates for the intron regions
    will be calculated. Individual interval trees will be created for each
    chromosome in the gtf file.  This function then returns a dictionary
    containing the root of the chromosome trees indexed by chromosome.
    Input:
        gtf - gene annotation file in gtf format.  Transcript_id and gene_id
              are required in the gtf attribute field.
        pchrom - chromosome or None.  If not None then only annotations for the
                 specified chromosome will be returned in a tree.
    Output:
        dictionary of interval trees where the key is the chromosome and the
        value is the root of the interval tree.  The misc field of the node
        contains a tuple in the format (position, first, last).
            position - first exon, middle exon, last exon, first, middle last
            first - coordinate of 5' end of first exon or intron
            last - coordinate of 3' end of last exon or intron
    '''
    gfh = open(gtf, "rU")
    genes = {}
    for line in gfh:
        fields = line.strip().split('\t')
        chrom = fields[0]
        if pchrom is not None and pchrom != chrom:
            continue
        feature = fields[2]
        posstrt = int(fields[3])
        posstop = int(fields[4])
        strand = fields[6]
        attributes = attributehandler.parseAttributesGTF(fields[8])
        genenm = attributes['gene_id']
        transcript = attributes['transcript_id']
        if feature == 'exon':
            genes.setdefault(transcript, dict()).setdefault('exon', list()) \
                 .append((posstrt, posstop))
            genes.setdefault(transcript, dict()).setdefault('chrom', chrom)
            genes.setdefault(transcript, dict()).setdefault('strand', strand)
            genes.setdefault(transcript, dict()).setdefault('gene', genenm)
    gfh.close()
    treeroots = {}
    for transcript in genes:
        elist = genes[transcript]['exon']
        elist = sorted(elist, key=getKeySort)
        ilist = makeintrons(elist)
        chrom = genes[transcript]['chrom']
        if chrom in treeroots:
            root = treeroots[chrom]
        else:
            root = None
        for i, exon in enumerate(elist):
            if genes[transcript]['strand'] == '+':
                if i == 0:
                    exord = 'first exon'
                elif i == len(elist)-1:
                    exord = 'last exon'
                else:
                    exord = 'middle exon'
            else:
                if i == 0:
                    exord = 'last'
                elif i == len(elist)-1:
                    exord = 'first'
                else:
                    exord = 'middle'
            node = intervalTree.Tree(mi=exon[0],
                                     ma=exon[1],
                                     name=transcript,
                                     name2=genes[transcript]['gene'],
                                     strand=genes[transcript]['strand'],
                                     misc=[exord, (elist[0][0], elist[-1][1])])
            root = node.insertTree(root)
            treeroots[chrom] = root
        for i, intron in enumerate(ilist):
            if genes[transcript]['strand'] == '+':
                if i == 0:
                    inord = 'first intron'
                elif i == len(ilist)-1:
                    inord = 'last intron'
                else:
                    inord = 'middle intron'
            else:
                if i == 0:
                    inord = 'last intron'
                elif i == len(ilist)-1:
                    inord = 'first intron'
                else:
                    inord = 'middle intron'
            node = intervalTree.Tree(mi=intron[0],
                                     ma=intron[1],
                                     name=transcript,
                                     name2=genenm,
                                     strand=genes[transcript]['strand'],
                                     misc=[inord, (ilist[0][0], ilist[-1][1])])
            root = node.insertTree(root)
            treeroots[chrom] = root
    return treeroots


def makeGeneTreeFromExons(gtf, pchrom):
    '''
    Make an interval overlap tree from a GTF file by placing only the exons
    into the tree. First transcripts will be formed by extracting the exons
    that belong to the same transcript. The transcript list will be sorted.
    Individual interval trees will be created for each chromosome in the gtf
    file. This function then returns a dictionary containing the root of the
    chromosome trees indexed by chromosome.
    Input:
        gtf - gene annotation file in gtf format.  Transcript_id and gene_id
              are required in the gtf attribute field.
        pchrom - chromosome or None.  If not None then only annotations for the
                 specified chromosome will be returned in a tree.
    Output:
        dictionary of interval trees where the key is the chromosome and the
        value is the root of the interval tree
    '''
    gfh = open(gtf, "rU")
    genes = {}
    for line in gfh:
        fields = line.strip().split('\t')
        chrom = fields[0]
        if pchrom is not None and pchrom != chrom:
            continue
        posstrt = int(fields[3])
        posstop = int(fields[4])
        strand = fields[6]
        attributes = attributehandler.parseAttributesGTF(fields[8])
        genenm = attributes['gene_name'] \
            if 'gene_name' in attributes \
            else attributes['gene_id']
        transcript = attributes['transcript_name'] \
            if 'transcirpt_name' in attributes \
            else attributes['gene_name']
        genes.setdefault(transcript, dict()).setdefault('exon', list()) \
             .append((posstrt, posstop))
        genes.setdefault(transcript, dict()).setdefault('chrom', chrom)
        genes.setdefault(transcript, dict()).setdefault('strand', strand)
        genes.setdefault(transcript, dict()).setdefault('gene', genenm)
    gfh.close()
    treeroots = {}
    for transcript in genes:
        elist = genes[transcript]['exon']
        elist = sorted(elist, key=getKeySort)
        strt = elist[0][0]
        end = elist[-1][1]
        # ilist = makeintrons(elist)
        chrom = genes[transcript]['chrom']
        # strnd = genes[transcript]['strand']
        if chrom in treeroots:
            root = treeroots[chrom]
        else:
            root = None
        # for i, exon in enumerate(elist):
        node = intervalTree.Tree(mi=strt,
                                 ma=end,
                                 name=transcript,
                                 name2=genes[transcript]['gene'],
                                 strand=genes[transcript]['strand'])
        root = node.insertTree(root)
        treeroots[chrom] = root
    return treeroots


def getGeneLengthDistribution(gtf, limit=None):
    '''
    The gene length histogram is created from a GTF file containing gene
    annotations.  The set of exons associated with each transcript is
    extracted and the gene length is calculated from the position of the first
    nucleotide on the 5' end to the last nucleotide on the 3' end.  It is
    plotted using matplotlib
    Input:
        gtf - gene annotations in GTF format; gene_id and transcript_id must
              exist in the attribute field
        limit - tuple; (lower, upper) bounds for histogram bins; None default
    Output:
        png file of the histogram named glen.png in the current directory
    '''
    gfh = open(gtf, "rU")
    genes = {}
    for line in gfh:
        fields = line.strip().split('\t')
        chrom = fields[0]
        posstrt = int(fields[3])
        posstop = int(fields[4])
        strand = fields[6]
        attributes = attributehandler.parseAttributesGTF(fields[8])
        genenm = attributes['gene_id']
        transcript = attributes['transcript_id']
        genes.setdefault(transcript, dict()).setdefault('exon', list()) \
             .append((posstrt, posstop))
        genes.setdefault(transcript, dict()).setdefault('chrom', chrom)
        genes.setdefault(transcript, dict()).setdefault('strand', strand)
        genes.setdefault(transcript, dict()).setdefault('gene', genenm)
    gfh.close()
    glen = []
    for transcript in genes:
        elist = genes[transcript]['exon']
        elist = sorted(elist, key=getKeySort)
        strt = elist[0][0]
        end = elist[-1][1]
        glen.append(end - strt + 1)
    matplotlib.pyplot.figure(figsize=(6, 6))
    matplotlib.pyplot.hist(numpy.array(glen, dtype=float),
                           range=limit,
                           bins=100,
                           color='lightskyblue')
    matplotlib.pyplot.xlim(limit)
    matplotlib.pyplot.savefig("glen.png")
    matplotlib.pyplot.close()


def makeTreeFromBed(bed):
    '''
    Create an interval overlap tree from a bed file. Bed files are 0-based
    coordinates.  Positions are converted to 1-based coordinates.
    Input:
        bed - genomic coordinates in BED format; if the optional fields are
              supplied; only the strand field is used if the BED file extends
              to the strand field.
    Output:
        a dictionary is returned where the keys are chromosomes and the values
        are the roots of the interval overlap trees by chromosome.
    '''
    bfh = open(bed, 'rU')
    roots = {}
    for line in bfh:
        fields = line.strip().split('\t')
        chrom = fields[0]
        start = int(fields[1])+1
        end = int(fields[2])+1
        strand = '+'
        if len(fields) >= 6:  # custom bed
            strand = fields[5]
        if chrom in roots:
            root = roots[chrom]
        else:
            root = None
        node = intervalTree.Tree(mi=start, ma=end, strand=strand)
        roots[chrom] = node.insertTree(root)
    return roots
