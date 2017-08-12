import logging
import os
import sys
import re
from flickrsync.log import Log

APPLICATION_NAME = 'flickrsync'

logger = logging.getLogger(Log.NAME)

# Flickr stores dates in MySQL format = 2004-11-29 16:01:26
# Exif data stores dates in ISO format = 2004:11:29 16:01:26
# remove all non numeric characters from the date so that they can be compared equally
def get_flat_date(datestring):
    return re.sub('[^0-9]', '', datestring)

# from photo title remove extension (if exists)
# this is because Flickr does not always maintain the file extension during upload
# as it is dependent on the upload client used
def get_short_name(filename, flickrtitle=None):
    return flickrtitle if flickrtitle else os.path.splitext(filename.lower())[0]

def get_flickr_title(filename, flickrtitle):
    return flickrtitle if flickrtitle else os.path.splitext(filename)[0]

def list_from_rows(rows):
    a_list = []
    for row in rows:
        a_list.append(row[0])

    logger.debug(a_list)
    return a_list

def list_to_csv(thelist):
    return ','.join(str(v) for v in thelist)

def remove_tag_from_tags(tags, thestring):
    tagslist = tags.split(' ')
    newtagslist = list(tagslist)

    logger.debug('tagslist<%s>' % tagslist)

    for item in tagslist:
        if item.find(thestring) >=0:
            logger.debug('removing<%s>' % item)
            newtagslist.remove(item)

    logger.debug('return<%s>' % newtagslist)
    return ' '.join(newtagslist)

# remove root directory from path
# replace path separator with spaces
# remove leading spaces
def get_photoset_name(directory, rootpath):
    photosetname = directory.replace(rootpath, '').replace(os.path.sep, ', ').lstrip(',')

    if photosetname == "":
        photosetname = APPLICATION_NAME

    logger.debug('photosetname<%s>' % photosetname)

    return photosetname

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def tuple_list_from_rows(rows):
    a_list = []
    for row in rows:
        a_list.append(tuple(row))
    return a_list

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
