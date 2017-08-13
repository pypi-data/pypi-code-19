''' cminfc.py: Command-line interfacing functions '''

import argparse


def warnCm(*args):
    print('bibreduce: Warning:', *args)


def parseCmArgs():
    ''' Parse command-line args specific for bibreduce

        Returns:
            (obj): processed arguments structure
    '''
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description='''\
        Process bibtex files to reduce records. Flags specify what to include.
        All other fields will be included (i.e. journal, issue are always included).

        If either -d or -u are specified, it will attempt to fill missing links from the other field.
        The format of links in the document is determined by \\bibliographystyle.

        Example 1:
            $ python-bibreduce -c myManuscript.bib myReducedBibliography.bib
        Creates "myReducedBibliography.bib" with no titles, links, or abstract

        Example 2:
            $ python-bibreduce -d myManuscript.aux
        1) bibexport to produce "myManuscript.bib", and
        2) reduction to produce "myManuscript_proc.bib";
            - no coauthors or titles, and DOIs are linked.
        ''')

    # File in and out arguments
    parser.add_argument('infile', type=argparse.FileType('r'), help='This can be a bib or aux file')
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=None, help='Default: infile - "(.bib, .aux)" + "_proc.bib"')

    # Processing options
    parser.add_argument('-t', '--title', action='store_true')
    parser.add_argument('-c', '--coauthors', action='store_true')
    parser.add_argument('-d', '--doiLinks', action='store_true')
    parser.add_argument('-u', '--urlLinks', action='store_true', help='urlLinks overrides doiLinks if both are flagged')
    parser.add_argument('-a', '--abstract', action='store_true')

    args = parser.parse_args()
    args.infilename = args.infile.name
    if args.outfile is not None:
        args.outfilename = args.outfile.name
    else:
        args.outfilename = None

    return args
