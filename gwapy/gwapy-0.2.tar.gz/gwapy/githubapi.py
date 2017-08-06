import json
import os.path

import requests

base_url = 'https://api.github.com'
credentials_file = '~/.ghpwd'


class GitHubApi:
    def __init__(self, repo_owner, repo_name):
        self.repoOwner = repo_owner
        self.repoName = repo_name

    def list_github_issues(self, labels, since):
        login, password = read_credentials()
        '''List an issue on github.com with given labels.'''
        # Our url to list issues via GET
        url = '%s/repos/%s/%s/issues' % (base_url, self.repoOwner, self.repoName)
        # Create an authenticated session to create the issue
        session = requests.session()
        session.auth = (login, password)
        r = session.get(url, params='labels=%s&since=%sT00:00:00Z&state=all' % (labels, since))
        if r.status_code == 200:
            return [i['body'] for i in json.loads(r.content.decode('utf-8'))]
        else:
            print('Could not find Issues for Labels "%s"' % labels)
            print('Response:', r.content)
            return None

    def create_github_issue(self, title, body=None, assignee=None, milestone=None, labels=None):
        login, password = read_credentials()
        '''Create an issue on github.com using the given parameters.'''
        # Our url to create issues via POST
        url = '%s/repos/%s/%s/issues' % (base_url, self.repoOwner, self.repoName)
        # Create an authenticated session to create the issue
        session = requests.session()
        session.auth = (login, password)
        # Create our issue
        issue = {'title': title,
                 'body': body,
                 'assignee': assignee,
                 'milestone': milestone,
                 'labels': labels}
        # Add the issue to our repository
        r = session.post(url, json.dumps(issue))
        if r.status_code == 201:
            return json.loads(r.content.decode('utf-8'))
        else:
            print('Could not create Issue "%s"' % title)
            print('Response:', r.content)

    def get_project_column_id(self, project_name, column_name):
        login, password = open(os.path.expanduser('~/.ghpwd')).read().split()
        url = '%s/repos/%s/%s/projects' % (base_url, self.repoOwner, self.repoName)
        session = requests.session()
        session.auth = (login, password)
        headers = {'Accept': 'application/vnd.github.inertia-preview+json'}
        r = session.get(url, headers=headers)
        result = None
        if r.status_code == 200:
            projects = {project_name: pid for (project_name, pid) in
                        [(i['name'], i['id']) for i in json.loads(r.content.decode('utf-8'))]}
            project_id = projects.get(project_name)
            if project_id is not None:
                url = '%s/projects/%s/columns' % (base_url, project_id)
                r = session.get(url, headers=headers)
                columns = {column_name: cid for (column_name, cid) in
                           [(i['name'], i['id']) for i in json.loads(r.content.decode('utf-8'))]}
                column_id = columns.get(column_name)
                if column_id is not None:
                    result = column_id
                else:
                    print('Could not find Project column %s for Project %s' % (project_name, column_name))
            else:
                print('Could not find Project Project %s' % project_name)
        else:
            print('Could not find Project column %s for Project %s' % (project_name, column_name))
            print('Response:', r.content)
        return result


def add_issue_to_project_column(issue_id, column_id):
    login, password = read_credentials()
    url = '%s/projects/columns/%s/cards' % (base_url, column_id)
    # Create an authenticated session to create the issue
    session = requests.session()
    session.auth = (login, password)
    headers = {'Accept': 'application/vnd.github.inertia-preview+json'}

    card = {'content_id': issue_id,
            'content_type': 'Issue'
            }
    r = session.post(url, json.dumps(card), headers=headers)
    if r.status_code == 201:
        return json.loads(r.content.decode('utf-8'))
    else:
        print('Could not add issue "%s" to project column' % issue_id)
        print('Response:', r.content)


def read_credentials():
    login, password = open(os.path.expanduser(credentials_file)).read().split()
    return login, password
