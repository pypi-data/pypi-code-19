import argparse

import pdupes

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action="version",
                        version=pdupes.__version__,
                        help='print the version of pdupes and exit')
    parser.add_argument('paths', nargs="+", help="Paths to search")
    args = parser.parse_args()

    finder = pdupes.DuplicateFinder(args.paths)
    finder.find_duplicates()

    print("Duplicates:")
    for (hash_, size), duplicates in finder.duplicates.items():
        print(f"\n{size:,} bytes with hash {hash_}:")
        for duplicate in duplicates:
            print(f"    {duplicate.resolve()}")
