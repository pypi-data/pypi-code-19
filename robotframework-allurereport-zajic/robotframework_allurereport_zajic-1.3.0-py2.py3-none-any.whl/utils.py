import time
import hashlib
import os

from six import text_type, binary_type


def uid(name):
    """
    Generates UID uniquely for name by the means of hash function,
    since allure requests that.
    """
    return hashlib.sha256(name).hexdigest()


def sec2ms(sec):
    return int(round(sec * 1000.0))

def now():
    """
    Return current time in the allure-way representation.
    """
    return sec2ms(time.time())

def unicode_helper(text):
    if isinstance(text, text_type):
        return text
    elif isinstance(text, binary_type):
        return text.decode('utf-8', 'replace')
    else:
        return text_type(text)

def clear_directory(path):
    for the_file in os.listdir(path):
        file_path = os.path.join(path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

def copy_dir_contents(old_path, new_path):
    for the_file in os.listdir(old_path):
        file_path = os.path.join(old_path, the_file)
        try:
            if os.path.isfile(file_path):
                os.rename(file_path, os.path.join(new_path, the_file))
        except Exception as e:
            print(e)