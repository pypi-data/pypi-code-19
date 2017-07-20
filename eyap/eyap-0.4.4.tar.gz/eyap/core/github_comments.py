"""Module for working comments from GitHub backend.
"""

import doctest
import re
import json
import logging
import zipfile

import requests


try:
    from markdown import markdown
except ImportError as problem:
    logging.warning('\n'.join([
        'Could not import markdown package. Will render as plain.',
        'Install the markdown package if you want comments rendered as',
        'markdown.']))

    def markdown(text, *args, **kw):
        "Fake markdown by just return input text"
        dummy = args, kw
        return text

from eyap.core import comments, yap_exceptions


class GitHubAngry(Exception):
    """Exception to indicate something wrong with github API.
    """

    def __init__(self, msg, *args, **kw):
        Exception.__init__(self, msg, *args, **kw)


class GitHubCommentGroup(object):
    """Class to represent a group of github comments.
    """

    def __init__(self, owner, realm, topic_re,
                 user=None, token=None, max_threads=None):
        """Initializer.

        :arg owner:    String owner (e.g., the repository owner if using
                       GitHub as a backend).

        :arg realm:    The realm (e.g., repository name on GitHub).

        :arg topic_re: Regular expression for topics to include in group.

        :arg user:     String user name.

        :arg token:    Password or token to use to connect to backend.

        """
        self.owner = owner
        self.realm = realm
        self.topic_re = topic_re
        self.user = user
        self.token = token
        self.max_threads = max_threads
        self.base_url = 'https://api.github.com/repos/%s/%s' % (
            self.owner, self.realm)

    def get_thread_info(self):
        """Return a json list with information about threads in the group.
        """
        result = []
        my_re = re.compile(self.topic_re)
        url = '%s/issues' % (self.base_url)
        while url:
            kwargs = {} if not self.user else {'auth': (
                self.user, self.token)}
            my_req = requests.get(url, **kwargs)
            my_json = my_req.json()
            for item in my_json:
                if my_re.search(item['title']):
                    result.append(item)
                    if self.max_threads is not None and len(
                            result) >= self.max_threads:
                        logging.debug('Stopping after max_threads=%i threads.',
                                      len(result))
                        return result
            url = None
            if 'link' in my_req.headers:
                link = my_req.headers['link'].split(',')
                for thing in link:
                    potential_url, part = thing.split('; ')
                    if part == 'rel="next"':
                        url = potential_url.lstrip('<').rstrip('>')

        return result

    def export(self, out_filename):
        """Export desired threads as a zipfile to out_filename.
        """
        with zipfile.ZipFile(out_filename, 'w', zipfile.ZIP_DEFLATED) as arc:
            id_list = list(self.get_thread_info())
            for num, my_info in enumerate(id_list):
                logging.info('Working on item %i : %s', num, my_info['number'])
                my_thread = GitHubCommentThread(
                    self.owner, self.realm, my_info['title'], self.user,
                    self.token, thread_id=my_info['number'])
                csec = my_thread.get_comment_section()
                cdict = [item.to_dict() for item in csec.comments]
                my_json = json.dumps(cdict)
                arc.writestr('%i__%s' % (my_info['number'], my_info['title']),
                             my_json)

    @staticmethod
    def _test_export():
        """Simple regression test to make sure export works.

    NOTE: this test will hit the github web site unauthenticated. There are
          pretty tight rate limits for that so if you are re-running this
          test repeatedly, it will fail. To manually verify you can set
          user and token and re-run.

>>> user, token = None, None
>>> import tempfile, shlex, os, zipfile
>>> from eyap.core import github_comments
>>> group = github_comments.GitHubCommentGroup(
...    'octocat', 'Hello-World', '.', user, token, max_threads=3)
>>> fn = tempfile.mktemp(suffix='.zip')
>>> group.export(fn)
>>> zdata = zipfile.ZipFile(fn)
>>> len(zdata.filelist)
3
>>> data = zdata.read(zdata.infolist()[0].filename)
>>> len(data) > 10
True
>>> del zdata
>>> os.remove(fn)
>>> os.path.exists(fn)
False
"""


class GitHubCommentThread(comments.CommentThread):
    """Sub-class of CommentThread using GitHub as a back-end.
    """

    # Base url to use in searching for issues.
    search_url = 'https://api.github.com/search/issues'
    url_extras = ''  # useful in testing to add things to URL

    def __init__(self, *args, **kw):
        """Initializer.

        :arg *args, **kw:  As for CommentThread.__init__.

        """
        comments.CommentThread.__init__(self, *args, **kw)
        self.base_url = 'https://api.github.com/repos/%s/%s' % (
            self.owner, self.realm)

    def lookup_thread_id(self):
        """Lookup thread id as required by CommentThread.lookup_thread_id.

        This implementation will query GitHub with the required parameters
        to try and find the topic for the owner, realm, topic, etc., specified
        in init.
        """

        query_string = '%s?q=in:title+%%3A%s%%3A+repo:%s/%s' % (
            self.search_url, self.topic, self.owner, self.realm)
        kwargs = {} if not self.user else {'auth': (
            self.user, self.token)}
        my_req = requests.get(query_string, **kwargs)
        if my_req.status_code != 200:
            raise GitHubAngry(
                'Bad status code %s finding topic %s because %s' % (
                    my_req.status_code, self.topic, my_req.reason))

        data = my_req.json()
        if data['total_count'] == 1:  # unique match
            return data['items'][0]['number']
        if data['total_count'] > 1:  # multiple matches since github doesn't
            searched_data = [        # have unique search we must filter it
                item for item in data['items'] if item['title'] == self.topic]
            if len(searched_data) > 1:
                raise yap_exceptions.UnableToFindUniqueTopic(
                    self.topic, data['total_count'], '')
            else:
                assert len(searched_data) == 1, (
                    'Confused searching for topic "%s"' % str(self.topic))
                return searched_data[0]['number']
        else:
            return None

    def raw_pull(self, topic):
        """Do a raw pull of data for given topic down from github.

        :arg topic:    String topic (i.e., issue title).

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:      Result of request data from github API.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:       Encapsulate call that gets raw data from github.

        """
        kwargs = {} if not self.user else {'auth': (self.user, self.token)}
        my_req = requests.get('%s/issues/%s' % (
            self.base_url, topic), **kwargs)
        return my_req

    def lookup_comment_list(self):
        """Lookup list of comments for an issue.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:  The pair (ISSUE, COMMENTS) where ISSUE is a dict for the
                   main issue and COMMENTS is a list of comments on the issue.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Do the work of getting data from github, handling paging,
                   and so on.

        """
        if self.thread_id is None:
            return None, None

        # Just pulling a single issue here so pagination shouldn't be problem
        my_req = self.raw_pull(self.thread_id)
        if my_req.status_code != 200:
            raise GitHubAngry('Bad status code %s because %s' % (
                my_req.status_code, my_req.reason))
        issue_json = my_req.json()
        comments_url = issue_json['comments_url'] + self.url_extras
        kwargs = {} if not self.user else {'auth': (self.user, self.token)}
        comments_json = []
        while comments_url:
            logging.debug('Pulling comments URL: %s', comments_url)
            c_req = requests.get(comments_url, **kwargs)
            my_json = c_req.json()
            assert isinstance(my_json, list)
            comments_json.extend(my_json)
            comments_url = None
            if 'link' in c_req.headers:  # need to handle pagination.
                logging.debug('Paginating in lookup_comment_list')
                link = c_req.headers['link'].split(',')
                for thing in link:
                    potential_url, part = thing.split('; ')
                    if part == 'rel="next"':
                        comments_url = potential_url.lstrip('<').rstrip('>')

        return issue_json, comments_json

    def lookup_comments(self, reverse=False):
        if self.thread_id is None:
            self.thread_id = self.lookup_thread_id()
        issue_json, comment_json = self.lookup_comment_list()
        if issue_json is None and comment_json is None:
            return comments.CommentSection([])
        cthread_list = [comments.SingleComment(
            issue_json['user']['login'], issue_json['updated_at'],
            issue_json['body'], issue_json['html_url'],
            markup=markdown(issue_json['body'], extensions=[
                'fenced_code', 'tables']))]

        for item in comment_json:
            comment = comments.SingleComment(
                item['user']['login'], item['updated_at'], item['body'],
                item['html_url'], markup=markdown(
                    item['body'], extensions=['fenced_code', 'tables']))

            cthread_list.append(comment)

        if reverse:
            cthread_list = list(reversed(cthread_list))

        return comments.CommentSection(cthread_list)

    def add_comment(self, body, allow_create=False):
        """Implement as required by CommentThread.add_comment.

        :arg body:    String/text of comment to add.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:     Response object indicating whether added succesfully.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:      This uses the GitHub API to try to add the given comment
                      to the desired thread.

        """
        if self.thread_id is None:
            self.thread_id = self.lookup_thread_id()
        data = json.dumps({'body': body})
        result = requests.post('%s/issues/%s/comments' % (
            self.base_url, self.thread_id), data, auth=(self.user, self.token))
        if result.status_code != 201:
            if result.reason == 'Not Found' and allow_create:
                return self.create_thread(body)
            else:
                raise GitHubAngry(
                    'Bad status %s add_comment on %s because %s' % (
                        result.status_code, self.topic, result.reason))

        return result

    def create_thread(self, body):
        data = json.dumps({'body': body, 'title': self.topic})
        result = requests.post('%s/issues' % (self.base_url),
                               data, auth=(self.user, self.token))
        if result.status_code != 201:
            raise GitHubAngry(
                'Bad status %s in create_thread on %s because %s' % (
                    result.status_code, self.topic, result.reason))

        return result

    @staticmethod
    def _regr_test_lookup():
        """
    NOTE: this test will hit the github web site unauthenticated. There are
          pretty tight rate limits for that so if you are re-running this
          test repeatedly, it will fail. To manually verify you can set
          user and token and re-run.

>>> user, token = None, None
>>> import tempfile, shlex, os, zipfile
>>> from eyap.core import github_comments
>>> t = github_comments.GitHubCommentThread(
...     'emin63', 'eyap', '.', user, token, thread_id='1')
>>> i, c = t.lookup_comment_list()
>>> t.url_extras = '?per_page=1'
>>> more_i, more_c = t.lookup_comment_list()
>>> i == more_i and c == more_c
True
>>> t.url_extras = ''
        """

if __name__ == '__main__':
    doctest.testmod()
    print('Finished tests')
