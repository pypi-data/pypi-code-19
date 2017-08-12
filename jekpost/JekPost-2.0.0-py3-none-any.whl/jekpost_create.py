#!/usr/bin/env python3

import argparse
import shutil
import os
import datetime

from string import Template

def read_template_file(template_file):
    """
    Read a template file, and return it as a Template object
    """

    with open(template_file, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def generate_post_file(title, location, disqus_name=None):

    print(" Generating post file...", end="")
    filename = make_filename(title, get_date_formatted(datetime.date.today()))

    src_path = os.path.abspath(__file__)

    # go two levels up
    src_dir = os.path.dirname(os.path.dirname(src_path))

    template_dir = os.path.join(src_dir, "templates")
    post_template_path = os.path.join(template_dir, "post.template")
    disqus_template_path = os.path.join(template_dir, "disqus.template")

    post_template = read_template_file(post_template_path)
    actual_file_content = post_template.substitute(post_title=title)

    os.chdir(location) # switch to destination directory

    with open(filename, 'x', encoding='utf-8') as actual_file:
        actual_file.write(actual_file_content)
        if disqus_name is not None:
            t = read_template_file(disqus_template_path)
            disqus_script = t.substitute(disqus_shortname=disqus_name)
            actual_file.write(disqus_script)

    print(" done!")
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
