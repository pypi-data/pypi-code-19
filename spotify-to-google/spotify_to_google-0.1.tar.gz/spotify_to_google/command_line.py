import getpass
import argparse
from spotify_to_google import import_all_playlists

def main():
    # Set arguments
    parser = argparse.ArgumentParser(description='Imports playlists from ')
    parser.add_argument('-V', '--version', action="version",
                        version="%(prog)s 0.1.0")
    parser.add_argument('-g', '--google', type=str,
                        required=True, help='Google username')
    parser.add_argument('-s', '--spotify', type=str,
                        required=True, help='Spotify username')
    parser.add_argument('-v', '--verbose', action="count",
                        help="Output verbosity level")

    # Get arguments
    args = parser.parse_args()

    password = getpass.getpass("Enter password for user %s:\n" % (args.google))
    import_all_playlists(args.spotify, args.google, password)