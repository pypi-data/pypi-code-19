"""A simple TV show renamer, no TVDB required

Args:
    file (str): Path to the file you want to rename
    -s / --silent (bool): Program will run without any messages
        (except unknown exceptions).

Attributes:
    SHOWNAMES_DICT_FILEPATH (str): showname match dictionary JSON filepath
"""
import re
import argparse
import os
import json


SHOWNAMES_DICT_FILENAME = "shownames.json"
SHOWNAMES_DICT_FILEPATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), SHOWNAMES_DICT_FILENAME
)

def fix_episode(episode):
    """Processes episode section of filename

    Args:
        episode (str): Episode section of filename

    Returns:
        str: Processed episode (daily/seasonal as appropriate)

    Raises:
        ValueError: on invalid episode string
    """
    return_value = episode
    pattern_string_seasonal = r"(?:s|\[)(\d{1,2})(?:e|x)(\d{1,2})"
    pattern_seasonal = re.compile(pattern_string_seasonal, flags=re.IGNORECASE)
    match_seasonal = pattern_seasonal.search(return_value)
    pattern_string_daily = r".*?(\d{4}).+?(\d{2}).+?(\d{2}).*?$"
    pattern_daily = re.compile(pattern_string_daily)
    match_daily = pattern_daily.search(return_value)
    if match_seasonal:
        season_num, episode_num = match_seasonal.groups()
        season_num = season_num.zfill(2)
        return_value = "[{}x{}]".format(season_num, episode_num)
    elif match_daily:
        year, month, day = match_daily.groups()
        month = month.zfill(2)
        day = day.zfill(2)
        return_value = "[{}-{}-{}]".format(year, month, day)
    else:
        raise ValueError
    return return_value


def fix_title(showname, shownames_dict):
    """Processes showname section of filename

    Args:
        showname (str): Showname section of filename
        shownames_dict (dict): Matches raw showname to real showname

    Returns:
        str: Processed showname
    """
    return_value = showname
    return_value = re.sub(r'\W+', '', return_value)
    return_value = return_value.lower()
    return_value = shownames_dict[return_value]
    return return_value


def tvregex(filename, shownames_dict):
    """Main program flow

    Args:
        filename (str): Path to the file you want to rename
        shownames_dict (dict): Matches raw showname to real showname

    Returns:
        str: Renamed filename
    """
    return_value = filename
    pattern_string = (
        r"(.+)\." +
        "((?:s\d{2}e\d{2})|(?:\d{4}\.\d{2}\.\d{2}))" +
        ".+\.(.+)"
    )
    pattern = re.compile(pattern_string, flags=re.IGNORECASE)
    match = pattern.search(filename)
    showname, episode, extension = match.groups()
    showname = fix_title(showname, shownames_dict)
    episode = fix_episode(episode)
    return_value = "{} - {}.{}".format(showname, episode, extension)
    return return_value


def main():
    """Takes in args
    Passes to real main program flow in tvregex()
    Outputs to file system
    """
    shownames_dict = {}
    with open(SHOWNAMES_DICT_FILEPATH) as f:
        shownames_dict = json.load(f)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        help="Path to the file you want to rename"
    )
    parser.add_argument(
        "-s", "--silent",
        help="Program will run without any messages" +
        " (except unknown exceptions). " +
        "(If set, this won't ask for matches)",
        action="store_true"
    )
    program_args = parser.parse_args()
    silent = program_args.silent
    filepath = program_args.file
    if os.path.isfile(filepath):
        folder = os.path.dirname(filepath)
        old_filename = os.path.basename(filepath)
        try:
            new_filename = tvregex(old_filename, shownames_dict)
            new_filepath = os.path.join(folder, new_filename)
            os.rename(filepath, new_filepath)
        except KeyError as ke:
            if not silent:
                raw_showname = ke.args[0]
                print(
                    "The filename was processed to give {}".format(
                        raw_showname
                    )
                )
                print("No show name match is known.")
                print("Type the show name that matches this")
                good_showname = input(
                    "(or just press Enter if there's no match):"
                )
                if good_showname != "":
                    shownames_dict[raw_showname] = good_showname
                    with open(SHOWNAMES_DICT_FILEPATH, "w") as f:
                        json.dump(shownames_dict, f, indent=4)
                    print("Thanks! Please run me again with this file!")
                    # Can I just run main() again?
        except ValueError as ve:
            if not silent:
                print("Cannot read episode number or date for this file")
        except AttributeError as ae:
            if not silent:
                print("Cannot read file name as TV show")
    else:
        if not silent:
            print("No file at file path")


if __name__ == '__main__':
    main()
