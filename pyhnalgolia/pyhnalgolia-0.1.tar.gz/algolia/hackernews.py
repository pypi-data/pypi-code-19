import datetime
import json
import sys

import requests
from .settings import supported_api_versions

class InvalidItemID(Exception):
    pass


class InvalidUserID(Exception):
    pass


class InvalidAPIVersion(Exception):
    pass


class HTTPError(Exception):
    pass


class HackerNews(object):
    def __init__(self, version='v1'):
        """
        Args:
            version (string): specifies Angolia Hacker News API version. 
            Default is `v1`.
        Raises:
            InvalidAPIVersion: If Hacker News version is not supported.
        """
        try:
            self.base_url = supported_api_versions[version]
        except KeyError:
            raise InvalidAPIVersion

    def _get(self, url):
        """Internal method used for GET requests
        Args:
            url (string): URL to send GET.
        Returns:
            requests' response object
        Raises:
          HTTPError: If HTTP request failed.
        """
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            return response
        else:
            raise HTTPError

    def _get_page(self, page):
        return self._get('{0}{1}.json'.format(self.base_url, page))

    def _get_page_param(self, page, param):
        return self._get('{0}{1}/{2}.json'.format(self.base_url, page, param))

    def get_item(self, item_id):
        """Returns Hacker News `Item` object.
        Args:
            item_id (int or string): Unique item id of Hacker News story, comment etc.
        Returns:
            `Item` object representing Hacker News item.
        Raises:
          InvalidItemID: If corresponding Hacker News story does not exist.
        """

        response = self._get_page_param('items', item_id).json()

        if not response:
            raise InvalidItemID

        return Item(response)

    def get_user(self, username):
        """Returns Hacker News `User` object.
        Args:
            username (string): unique user id of a Hacker News user.
        Returns:
            `User` object representing a user on Hacker News.
        Raises:
          InvalidUserID: If no such user exists on Hacker News.
        """
        response = self._get_page_param('users', username).json()

        if not response:
            raise InvalidUserID

        return User(response)


class Item(object):
    """
    Represents stories, comments, jobs, Ask HNs and polls
    """

    def __init__(self, data):
        self.item_id = data.get('id')
        self.created_at = data.get('created_at')
        self.author = data.get('author')
        self.title = data.get('title')
        self.url = data.get('url')
        self.text = data.get('text')
        self.points = data.get('points')
        self.parent_id = data.get('parent_id')
        self.children = data.get('children')

    def __repr__(self):
        retval = '<hackernews.Item: {0} - {1}>'.format(
            self.item_id, self.title)
        # For older versions of Python
        if sys.version_info.major < 3:
            return retval.encode('utf-8', errors='backslashreplace')
        return retval


class User(object):
    """
    Represents a hacker i.e. a user on Hacker News
    """

    def __init__(self, data):
        self.username = data.get('username')
        self.about = data.get('about')
        self.karma = data.get('karma')

    def __repr__(self):
        retval = '<hackernews.User: {0}>'.format(self.username)
        if sys.version_info.major < 3:
            return retval.encode('utf-8', errors='backslashreplace')
        return retval