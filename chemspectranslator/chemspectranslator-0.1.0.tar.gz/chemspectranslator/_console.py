import sys

def _translateParser():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='chemical mechanism species translator.')
    parser.add_argument('species', nargs=1,
                       help='One or several (comma-separated) species names to be translated')
    parser.add_argument('source', nargs=1,
                       help='Mechanism shortcut from which to translate.')
    parser.add_argument('dest', nargs=1,
                       help='Mechanism shortcut to which to translate.')
    return parser

def translate(args=None):

    if args is None:
        args = sys.argv[1:]

    parser = _translateParser()

    args = parser.parse_args()

    import chemspectranslator

    translator  = chemspectranslator.Translator()

    for spec in args.species[0].split(","):
        res = translator.translate(spec, args.source[0], args.dest[0])
        print spec + ": " + str(res)

