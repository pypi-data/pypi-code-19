from easydev import execute, shellcmd
import os


class Simulator(object):
    """A simple wrapper of art_illumina to generate simulated reads


    Here, we hard*coded the HiSeq2500 but one can chnage the length, coverage,
    standard deviation, paired or not. One can also generate the reads based
    on the coverage or the number of reads.

    Finally, one can also generate a mix of species using
    :meth:`generate_mixture`.

    """
    def __init__(self):
        pass

    def generate(self, fasta_file, outfile, length=150, coverage=10, stdev=10,
            paired=True, nreads=100000, method="coverage"):
        """

        """
        cmd = "art_illumina -ss HS25 -sam "
        cmd += " -i %s " % fasta_file
        cmd += "  -l %s " % length
        if method == "coverage":
            cmd += " -f %s " % coverage
        elif method == "nreads":
            cmd += " -c %s " % nreads

        cmd += " -m 200" 
        cmd += " -s %s " % stdev
        cmd += " -o %s" % outfile
        if paired: cmd += " -p"
        execute(cmd, verbose=False)

    def generate_mixture(self, fasta_files, outfile="mixture", length=150, 
            coverage=10, stdev=10, paired=True, method="nreads", nreads=100000):
        """

        .. todo:: give a list of ratio 
        .. todo:: cleanup

        """

        for i, fasta in enumerate(fasta_files):
            assert os.path.exists(fasta)
            self.generate(fasta, "test_%s_" % i, length=length,
                coverage=coverage, stdev=stdev, paired=paired, method=method,
                nreads=nreads)

        # Finally concat all the files into the outfile
        # The execute command fails because it uses the stdout and somehow
        # interfers with the cat command ?
        _ = shellcmd("cat test_*_1.fq > %s_1.fq" % "mixture", show=True)
        if paired is True:
            _ = shellcmd("cat test_*_2.fq > %s_2.fq" % "mixture", show=True)
        # TODO cleanup: remove sam, aln files
