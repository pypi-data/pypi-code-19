#!/usr/bin/env python3

import argparse
import datetime
import os

def generate_post_file(title, location, disqus_name=None):
    title_line = "title: {}".format(title)
    filename = make_filename(title, get_date_formatted(datetime.date.today()))

    os.chdir(location) # switch to destination directory

    with open(filename, mode='x', encoding='utf-8') as actual_file:
        print('---', file=actual_file)
        print('layout: post', file=actual_file)
        print(title_line, file=actual_file)
        print('excerpt: Your excerpt goes here', file=actual_file)
        print('tags: tag1, tag2', file=actual_file)
        print('---', file=actual_file)
        print('Your post content goes here', file=actual_file)
    return filename

def make_filename(post_title, date_prefix):
    title_formatted = post_title.replace(' ', '-')
    filename = date_prefix + '-' + title_formatted + '.md'
    return filename

def get_date_formatted(date):
    """
    Return the date in the format: 'YEAR-MONTH-DAY'
    """

    year = str(date.year)
    month = str(date.month)
    day = str(date.day)

    single_digits = range(1, 10)

    if date.month in single_digits:
        month = '0' + month

    if date.day in single_digits:
        day = '0' + day

    return year + '-' + month + '-' + day

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('title', help='Post title')
    parser.add_argument('location', help='Destination directory')
    parser.add_argument('-dq', '--disqus', help='Disqus shortname')
    args = parser.parse_args()

    post_title = args.title.strip() # remove whitespaces that may be at
                                    # either ends.

    print(" Disqus shortname: ", args.disqus)
    print(" Post Title: ", post_title)

    try:
        filename = generate_post_file(post_title, args.location, args.disqus)
    except FileExistsError as err:
        print("\n\n", err)
    except FileNotFoundError as err:
        print("\n\n", err)
    except NotADirectoryError as err:
        print("\n\n", err)
    else:
        print(" New post created: ", filename)
        print(" Happy blogging!")

if __name__ == '__main__':
    main()
