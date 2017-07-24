#!/usr/bin/env python3
'''Written by: Tri Cao
   Contributed by: Trung Dinh
Note: This only works for Python3 please install Python3 and pip before use
      To install PyGithub with pip: pip install PyGithub
To not typing username and password multiple time consider cache your
information:
 git config --global credential.helper 'cache --timeout 7200'
 to Create token: need to install curl
'''

# BIG TODO: Use Docker to package???
# TODO: How to receive the marks from other TAs and combine
# TODO: Deduct the mark base on the status
# TODO: Generating CSV file to upload
# TODO: Send feedback back to students' github repo

# TODO: Mark with Tester, fully automated

import subprocess
import getpass
import argparse
import os
import os.path
import json
import errno
import time
import re
import sys
from functools import wraps
from github import Github, GithubException
from tqdm import tqdm
from git import Repo

'''
def main():
    """ The main function of the script
        This function run as a starting point of the program
    """
    # Handle args first
    args = args_handle()
    # Get user saved data
    data = get_data()
    # Run the program base on args and data
    run(args, data)
'''

def get_assignment():
    
    # Handle args first
    args = args_handle()
    # Get user saved data
    data = get_data()
    # Run the program base on args and data
    run(args, data)

def run(args, data):
    '''Run the program base on args and data
    '''
    operations = {'user': set_user, 'token': create_token,
                  'deadline': save_deadline, 'dir': save_dir,
                  'clone': clone, 'add': add_files, 'info': show_data}
    for task in list(filter(lambda key: getattr(args, key), args.__dict__.keys())):
        operations[task](data, args)

    write_file("./data", data, "data.json")


def args_handle():
    ''' Handle input options via command line arguments
    '''
    parser = argparse.ArgumentParser(prog='GiT_AnD_MaRk')
    parser.add_argument("-u", "--user", help="authorize with github username")
    parser.add_argument("-t", "--token", action="store_true",
                        help="authorize by creating OAuth token")
    parser.add_argument("-c", "--clone", metavar='prefix', help="clone all \
                        repository in SCS-Carleton beginning with the pattern")
    parser.add_argument("-d", "--dir", metavar='directory', help="the \
                        directory path to save the clone folder")
    parser.add_argument("-a", "--add", metavar='prefix and files ', nargs='*',
                        help="Commit files to the remote \
                        repositories of all students")
    parser.add_argument("-dl", "--deadline", metavar="YYYY-MM-DD-H:M",
                        help="specify the deadline for current assignment")
    parser.add_argument("-i", "--info", action="store_true",
                        help="Show some information")
    args = parser.parse_args()
    return args


def get_data():
    ''' Read user saved data from "/data/data.json"
    '''
    try:
        with open("./data/data.json", "r") as file:
            data = json.load(file)
        assert data
    except (IOError, AssertionError):
        data = {'user': None, 'token': None,
                'dir': './', 'deadline': None, 'commits': 0}
    return data


def write_file(out_dir, data, file_name, is_json=True, is_array=False):
    ''' Write Json data into a file
    '''
    with safe_open_w("%s/%s" % (out_dir, file_name)) as file:
        if is_json:
            json.dump(data, file, ensure_ascii=False, sort_keys=True, indent=4)
        elif is_array:
            file.write("\n".join(data))


def set_user(data, args):
    ''' Set the user if provided
    '''
    data['user'] = args.user


def save_deadline(data, args):
    ''' Save the specified into data objects
    '''
    try:
        data['deadline'] = time.mktime(time.strptime(args.deadline,
                                                     "%Y-%m-%d-%H-%M"))
    except ValueError as err:
        print(err)


def save_dir(data, args):
    ''' Save the specified directory path to clone
    '''
    dir_path = args.dir
    if os.path.isdir(dir_path):
        data['dir'] = os.path.abspath(dir_path)
    else:
        print("Unfound directory!")


def authorize_user(func):
    """ Get the github object that connect to the github account

    User should provide token or username to authorize:
    if username is provided then program will prompt to write the password
    """
    # get the git with authorization
    @wraps(func)
    def wrapper(data, args):
        ''' The wrapper that helps authorize github user
        '''
        print("Conecting with github...", end="", flush=True)
        if data['token']:
            git = Github(data['token'])
        else:
            login = data['user'] if data['user'] else input(
                "Enter your user name: ")
            password = getpass.getpass()
            git = Github(login, password)
        try:
            orgs = git.get_organization("SCS-Carleton")
            print("Athorized")
            return func(orgs, data, args)
        except GithubException:
            print("Error: Bad (expired) token or wrong username|password")
            sys.exit()
    return wrapper


def make_dir(out_path):
    ''' Smart making the output folder
    '''
    try:
        os.makedirs(out_path)
        out = out_path
    except FileExistsError:
        count = 1
        while True:
            try:
                out = "%s-%d" % (out_path, count)
                os.makedirs(out)
                break
            except FileExistsError:
                count += 1
                continue
    return out


@authorize_user
def clone(orgs, data, args):
    ''' Set up some counters
    '''
    stat = {'count': 0, 'late': 0, 'invalid': 0}
    # Save the students information
    students = {}
    names = []
    invalids = []
    print("Getting repositories...", end="", flush=True)
    for repo in orgs.get_repos():
        if repo.name.startswith(args.clone):
            names.append(repo.name)
    print("DONE")
    print("Cloning ...")
    out_dir = make_dir(data['dir'] + "submissions")
    for name in tqdm(names):
        clone_repo(name, out_dir)
        stat['count'] += 1

        path = os.path.abspath("%s/%s" % (out_dir, name))

        ''' Get the time stamp of the last commit
        '''
        # Time in epoc-unix (integer)
        epoc_unix = Repo(path).head.commit.committed_date
        submitted_time = time.localtime(epoc_unix)
        student = {}
        ''' Write student information by reading the submit-01 file
        '''
        try:
            with open(path + '/submit-01', 'r') as file:
                username = re.search(r'(\w+-)((?:\w+-)*\w+)$', name).group(2)
                student = {'id': file.readline().strip(),
                           'email': file.readline().strip(),
                           'name': file.readline().strip(),
                           'username': file.readline().strip(),
                           'repo_path': path,
                           'submit-time': time.strftime("%H:%M %d %b %Y", submitted_time)
                          }
            check_info(student)
            student['status'] = "OK" if check_time(stat,
                                                   epoc_unix,
                                                   data['deadline']) else "LATE"
            username = student['username']
            add_information_to_rubric(username, student, "rubric-01.md")
        except FileNotFoundError:
            invalids.append(name)
        except (EnvironmentError, BadInfoError):
            student['status'] = "BAD"
            stat['invalid'] += 1
            add_information_to_rubric(username, student, "rubric-01.md")


        if student:
            if student['status'] != "OK":
                student['repo_path'] = path + "-" + student['status']
                os.rename(path, student['repo_path'])
            students[username] = student

    write_file(out_dir, students, "students.json")

    print("There are total ", stat['count'], " submissions cloned (", stat['late'],
          " late submissions, ", stat['invalid'], " invalid submissions)")
    print("There are", len(invalids), " unknown submissions:")
    print("\n".join(invalids))

class TokenCreateException(Exception):
    ''' Error when token were created for this username
    '''
    pass


class ValidationException(Exception):
    ''' Error when provided username and password do not match
    '''
    pass

# pylint: disable=W0613


def create_token(data, *args):
    """ Create the OAuth token for authorization
        "IMPORTANT": having curl installed
    """
    try:
        login = data['user']
        if not login:
            login = input("Please enter your username: ")
        completed_process = subprocess.run(['curl', '-u', login, '-d',
                                            '{"scopes": ["repo", "user"],\
                                             "note": "getting-started"}',
                                            'https://api.github.com/authorizations'],
                                           stdout=subprocess.PIPE, universal_newlines=True)

        result = json.loads(completed_process.stdout)
        if 'token' in result:
            print(result['token'])
            data['token'] = result['token']
        else:
            if 'errors' in result:
                raise TokenCreateException("You already have a token")
            else:
                raise ValidationException("Wrong username|password")
    except TokenCreateException:
        print("You already have a token, consider deleting it")
        return
    except ValidationException as err:
        print(err)
        return


def clone_repo(repo_name, dir_path, *org_or_user):
    """Clone a remote repository

    Initiate a subprocess that call git to be launched and clone the specified
    repo_name

    Args:
        repo_name: the name of the repository
        dir_path : the directories that user wants to clone into
        org_or_user: the name of the organization or user that the repo belongs
        to (Default: "SCS-Caleton")

    """
    path = "%s/%s" % (dir_path, repo_name)
    if not os.path.isdir(path):
        if not org_or_user:
            cloned_repo = Repo.clone_from("https://github.com/SCS-Carleton/" + repo_name +
                                          ".git", path)
        else:
            cloned_repo = Repo.clone_from("https://github.com/" + "/".join(org_or_user) +
                                          "/" + repo_name + ".git", path)
        return cloned_repo
    return Repo(path)


# Taken from https://stackoverflow.com/a/600612/119527


def mkdir_p(path):
    ''' Create repository with specified path
    '''
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

# Taken from https://stackoverflow.com/questions/23793987/python-write-file-to-
# directory-doesnt-exist


def safe_open_w(path):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    mkdir_p(os.path.dirname(path))
    return open(path, 'w')


@authorize_user
def add_files(orgs, data, args):
    ''' Push the new commit and files to remote repos
    '''
    file_list = list(filter(os.path.isfile, args.add[1:]))
    prefix = args.add[0]
    count = 0
    commit_message = 'Added files: ' + ','.join(file_list)
    for repo in orgs.get_repos():
        if repo.name.startswith(prefix):
            count += 1
            gitpy_repo = Repo("./submissions/" + repo.name)
            gitpy_repo.index.add(file_list)
            gitpy_repo.index.commit(commit_message)
            origin = gitpy_repo.remote('origin')
            origin.push()
    print("There are total " + str(count) + " commits  done")
    data['commits'] += count


class BadInfoError(Exception):
    ''' Error occured when the info students provide does not match the
        requirement
    '''
    pass


def check_info(student):
    ''' Check the provided information in submit-01 file
    '''
    email_p = re.compile(r'\w+@cmail.carleton.ca')
    id_p = re.compile(r'\d{9}')
    name_p = re.compile(r'^(\w+\s)+\w+$')
    username_p = re.compile(r'\w+')
    error = []
    if not email_p.match(student['email']):
        error.append('email')
    if not id_p.match(student['id']):
        error.append('id')
    if not name_p.match(student['name']):
        error.append('name')
    if not username_p.match(student['username']):
        error.append('username')
    if error:
        message = "Invalid or lack information: " + ", ".join(error)
        raise BadInfoError(message)


def check_time(stat, current, deadline):
    ''' Check if the submit time of the assignment (last commit time) is before
        the deadline
    '''
    if not deadline or current <= deadline:
        return True
    stat['late'] += 1
    return False

# pylint: disable=W0613


def show_data(data, *args):
    ''' Show the data stored
    '''
    print(json.dumps((data), indent=4))


def create_remote_branch(repo, name):
    pass


def comment_wrap(message):
    ''' Put wrap the message with comment pattern in markdown file
    '''
    return "<!-- " + message + " -->"


def add_information_to_rubric(username, student, rubric_file_name):
    ''' Add the student's information to the rubric file

    This help for collecting the marks after marking done
    '''
    message = "{}\n{}\n{}\n".format(comment_wrap("PUT MARK HERE"),
                                    comment_wrap(student['id']),
                                    comment_wrap(username))
    try:
        with open(student['repo_path'] + '/' + rubric_file_name, 'r+') as file:
            file.write(message)
    except FileNotFoundError:
        print("Unable to find the file!")
        raise

'''
if __name__ == '__main__':
    main()
'''