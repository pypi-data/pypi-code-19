import sys, getopt
from .lib import *

def main():
    source_file = ""
    target_file = ""
    output_file = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:t:o:",["source=", "target=", "output="])
    except getopt.GetoptError:
        print('Charcheck -s<source file path> -t<target file path> -o<output file path>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Charcheck -s<source file path> -t<target file path> -o<output file path>')
            sys.exit()
        elif opt in ("-s", "--source"):
            source_file = arg
        elif opt in ("-t", "--target"):
            target_file = arg
        elif opt in ("-o","--output"):
            output_file = arg
    if source_file != "" or target_file != "":
        if output_file == "":
            process(source_file, target_file)
        else:
            process(source_file, target_file, output_file)
    else:
        print("You are missing target or source file name.")
        sys.exit()

