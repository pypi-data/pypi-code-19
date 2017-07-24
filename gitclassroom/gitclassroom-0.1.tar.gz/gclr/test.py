#!/usr/bin/env python3
'''Written by: Tri Cao
Note: This only works for Python3 please install Python3 and pip before use
      To install PyGithub with pip: pip install PyGithub
To not typing username and password multiple time consider cache your
information:
 git config --global credential.helper 'cache --timeout 7200'
 to Create token: need to install curl
'''

# BIG TODO: Use Docker to package???
# TODO: Fix the OK/late/Bad
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





def run(args, data):
    '''Run the program base on args and data
    '''
    operations = {'user': set_user, 'token': create_token,
                  'deadline': save_deadline, 'dir': save_dir,
                  'clone': clone, 'add': add_files}
    for task in list(filter(lambda key: getattr(args, key), args.__dict__.keys())):
        operations[task](data, args)

    write_file(data, "data.json")


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
        data = {'user': None, 'token': None, 'dir': './', 'deadline': None, 'commits' : 0}
    return data


def write_file(data, file_name, is_json=True, is_array=False):
    ''' Write Json data into a file
    '''
    with safe_open_w("./data/" + file_name) as file:
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


@authorize_user
def clone(orgs, data, args):
    ''' Set up some counters
    '''
    stat = {'count': 0, 'late': 0, 'invalid': 0}
    # Save the students information
    students = []
    # Save the inavalid folder (For late or not providing good information)
    invalid_submission = []
    names = []
    print("Getting repositories...", end="", flush=True)
    for repo in orgs.get_repos():
        if repo.name.startswith(args.clone):
            names.append(repo.name)
    print("DONE")
    print("Cloning ...")
    for name in tqdm(names):
        clone_repo(name, data['dir'])
        stat['count'] += 1
        path = os.path.abspath(data['dir'] + "submissions/" + name)

        ''' Get the time stamp of the last commit
        '''
        # Time in epoc-unix (integer)
        epoc_unix = Repo(path).head.commit.committed_date
        submitted_time = time.localtime(epoc_unix)

        ''' Write student information by reading the submit-01 file
        '''
        try:
            with open(path + '/submit-01', 'r') as file:
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
        except (EnvironmentError, BadInfoError):
            invalid_submission.append(name)
            stat['invalid'] += 1
        else:
            students.append(student)

    write_file(students, "students.json")

    print("There are total ", stat['count'], " submissions cloned (", stat['late'],
          " late submissions, ", stat['invalid'], " invalid submissions)")

    write_file(invalid_submission, "invalids", is_json=False, is_array=True)


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
    path = dir_path + "submissions/" + repo_name
    if not os.path.isdir(path):
        if not org_or_user:
            cloned_repo = Repo.clone_from("https://github.com/SCS-Carleton/" + repo_name +
                                          ".git", path)
        else:
            cloned_repo = Repo.clone_from("https://github.com/" + "/".join(org_or_user) +
                                          "/" + repo_name + ".git", path)
        return cloned_repo
    return Repo(dir_path + "submissions/" + repo_name)


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
            gitpy_repo = Repo("./submissions/" +repo.name)
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




@authorize_user
def send_feedback(orgs, data, args):
    ''' Send the graded rubik to students remote repo

    - TODO Create new "graded" branch
    - TODO Delete readme, change rubik into readme
    - Get the zip folders from TAs
    - unzip (can do it)
    -

    '''



def get_sha(repo, branch_name):
    ''' Get the sha from a branch

    Purpose: to create a new branch from this revision
    '''
    try:
        ref_object = repo.get_git_ref("heads/" + branch_name).object
    except GithubException:
        print("There is no such branch: ", branch_name)
        raise

    return ref_object.sha

def create_remote_branch(repo, name, sha):
    ''' Create a new remote branch of a Repo
    '''
    try:
        repo.create_git_ref("refs/heads/" + name, sha)
    except GithubException as err:
        print("Wrong SHA")
        raise

def delete_remote_branch(repo, branch_name):
    ''' Delete a remote branch
    '''
    try:
        repo.get_git_ref("heads/" + branch_name).delete()
    except GithubException:
        print("There is no such branch: ", branch_name)

def test_repo():
    git = Github("7e4dfad03d12ffd826ccf76fe6445c1c9ce87232")
    orgs = git.get_organization("SCS-Carleton")
    repo = orgs.get_repo("a1-test-TrCaM")
    # sha = get_sha(repo, "master")
    # delete_remote_branch(repo, "graged")
    # repo.create_git_ref("refs/heads/graded", sha)
    content = repo.get_readme()
    import base64
    print(base64.b64decode(content.content))

    # with open("./demo.md", "wb") as file:
        # file.write(base64.decodestring(content.content))

'''
def main():
    """ The main function of the script
        This function run as a starting point of the program
    """
    # Handle args first
    import export

    export.export("./submissions", "./", "rubric-01.md")

if __name__ == '__main__':
    main()
'''


def export_result():
    import export
    export.export("./submissions", "./", "rubric-01.md")
