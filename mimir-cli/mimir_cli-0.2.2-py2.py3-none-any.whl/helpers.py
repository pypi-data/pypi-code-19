import errno
import getpass
import json
import os
import requests
import sys
import zipfile
from mimir_cli.strings import (
    API_URL,
    MIMIR_DIR,
    ERR_INVALID_CRED,
    EMAIL_PROMPT,
    PROJECT_PROMPT,
    PROJECT_ERR_0_TO_N,
    ERR_INVALID_FILE,
    CLASSROOM_URL
)

INPUT_FUNCTION = None


# managing both versions of python
if sys.version_info >= (3, 0):
    INPUT_FUNCTION = input
else:
    INPUT_FUNCTION = raw_input


def mkdir(path):
    '''creates a folder if it doesnt exist'''
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def login(email, password):
    '''logs into the platform api'''
    # print('login 0')
    login_request = requests.post(
        '{}/lms/user_sessions'.format(API_URL),
        data={
            'email': email,
            'password': password
        }
    )
    # print('login 1')
    # print(login_request)
    data = json.loads(login_request.text)
    # print('login 2')
    if data['success']:
        authentication_token = data['auth_token']
        write_credentials(authentication_token)
    return data['success']


def read_credentials():
    '''reads the user credentials from the mimir directory'''
    mkdir(MIMIR_DIR)
    credentials_path = '{}.credentials'.format(MIMIR_DIR)
    if os.path.isfile(credentials_path):
        mimir_credentials_file = open(credentials_path, 'r')
        return json.loads(mimir_credentials_file.read())
    else:
        return {}


def write_credentials(auth_token):
    '''writes the user credentials to the mimir directory'''
    mkdir(MIMIR_DIR)
    credentials_path = '{}.credentials'.format(MIMIR_DIR)
    mimir_credentials_file = open(credentials_path, 'w')
    credentials = json.dumps({'auth_token': auth_token})
    mimir_credentials_file.write(credentials)
    mimir_credentials_file.close()


def continuous_prompt():
    '''prompts for a login repeatedly'''
    while True:
        if prompt_login():
            return True
        else:
            sys.stderr.write('\n{}\n'.format(ERR_INVALID_CRED))
    return False


def prompt_login():
    '''prompts for a login'''
    email = INPUT_FUNCTION(EMAIL_PROMPT)
    password = getpass.getpass()
    return login(email, password)


def get_projects_list():
    '''gets the projects list for a user'''
    url = '{}/lms/projects'.format(API_URL)
    credentials = read_credentials()
    if 'auth_token' in credentials:
        headers = {'Authorization': credentials['auth_token']}
        projects_request = requests.get(url, headers=headers)
        result = json.loads(projects_request.text)
        return result['projects']
    else:
        continuous_prompt()
        return get_projects_list()


def prompt_for_project(projects):
    '''prompts for which project'''
    for x, project in enumerate(projects):
        sys.stdout.write('{}: {}\n'.format(str(x), project['name']))
    choice = -1
    while choice < 0 or choice >= len(projects):
        try:
            choice = int(INPUT_FUNCTION(PROJECT_PROMPT))
        except ValueError:
            sys.stderr.write(PROJECT_ERR_0_TO_N.format(str(len(projects) - 1)))
    return projects[choice]


def zipdir(ziph, path):
    '''zips a directory up for submission'''
    abs_src = os.path.abspath(path)
    for dirname, subdirs, files in os.walk(path):
        for file in files:
            absname = os.path.abspath(os.path.join(dirname, file))
            arcname = absname[len(abs_src) + 1:]
            ziph.write(file, arcname)


def submit(filename, project_id):
    '''submits file(s) to the mimir platform'''
    url = '{}/lms/projects/{}/project_submissions'.format(API_URL, project_id)
    credentials = read_credentials()
    if 'auth_token' in credentials:
        data = {'project_submission[project_id]': project_id}
        headers = {'Authorization': credentials['auth_token']}
        submission_file = None
        if filename.lower().endswith('.zip'):
            submission_file = open(filename, 'rb')
        else:
            zipfilename = '{}current_submission.zip'.format(MIMIR_DIR)
            try:
                os.remove(zipfilename)
            except OSError:
                pass
            if os.path.isdir(filename):
                new_submission_zip = zipfile.ZipFile(zipfilename, 'w')
                zipdir(new_submission_zip, filename)
                new_submission_zip.close()
                submission_file = open(zipfilename, 'rb')
            else:
                submission_file = open(filename, 'rb')
        if not submission_file:
            sys.stderr.write(ERR_INVALID_FILE)
            return
        files = {'files[]': submission_file}
        sys.stdout.write('Submitting...\n')
        submission_request = requests.post(url, files=files, data=data, headers=headers)
        result = json.loads(submission_request.text)
        submission_file.close()
        if 'project_submission' in result:
            sys.stdout.write(
                'Submission sucessful! Click here for your results: {}/project_'
                'submissions/{}\n'.format(
                    CLASSROOM_URL,
                    result['project_submission']['id']
                )
            )
        else:
            sys.stderr.write(ERR_INVALID_CRED)
            continuous_prompt()
            submit(filename, project_id)
    else:
        sys.stderr.write(ERR_INVALID_CRED)
        continuous_prompt()
        submit(filename, project_id)
