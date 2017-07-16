import argparse
import json
import sys

from .tokeniz import tokenize


def get_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('document_file',
                            type=argparse.FileType(),
                            default=sys.stdin)
    arg_parser.add_argument('-l', '--language', help='Follow ISO 639-1.')
    return arg_parser.parse_args()


def main():
    args = get_args()

    print(json.dumps(tokenize(args.document_file.read(),
                              language=args.language),
                     ensure_ascii=False,
                     indent="\t"))


if __name__ == "__main__":
    main()
