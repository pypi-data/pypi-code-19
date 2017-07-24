import argparse
import sys
import subprocess

from ngramgraphs.graph import make_ngram_graph


def draw_graph(graph, filename):  # pragma: no cover
    graph.layout('circo')
    graph.draw(filename)


def prompt(prompt):
    """Ask for some value, keep asking until an answer is given
    (whitespace is stripped).

    """
    while True:
        try:
            ret = input(prompt)
        except KeyboardInterrupt:
            print()
            return ''
        else:
            if ret.strip():
                break
    return ret


def parse_args(args):
    fileout_help = 'The filename for the output (allowed filename ' + \
                   'extensions are PNG, JPG, PDF and more) (default: out.pdf)'
    parser = argparse.ArgumentParser(description='Draw an NGram Graph')
    parser.add_argument(
        'document', help='The input that will be converted to an N-Gram Graph')
    parser.add_argument(
        '-n', type=int, default=3,
        help='use 2 for bigrams, 3 for trigrams, etc. (default: 3)')
    parser.add_argument('--file-out', default='out.pdf', help=fileout_help)
    parser.add_argument(
        '--by-words', action='store_true',
        help='Build N-Grams by words (default: by characters)')
    return parser.parse_args(args)


def main(args):
    parsed_args = parse_args(args)
    graph = make_ngram_graph(
        parsed_args.document, parsed_args.n, parsed_args.by_words)
    draw_graph(graph, parsed_args.file_out)
    subprocess.call(['xdg-open', parsed_args.file_out])


if __name__ == '__main__':
    main(sys.argv[1:])
