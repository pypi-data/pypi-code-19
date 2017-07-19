import sys, os
import pysam

def main():
    args = " ".join(sys.argv[1:])
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.system("snakemake -s {s}".format(s=os.path.join(dir_path, "Snakefile ")) + args)
