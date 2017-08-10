# -*- coding: utf-8 -*-

"""Main module."""

import codecs
import io
import json
import logging
import os.path as P
import re
import time
import urllib

import lxml.etree
import requests
import requests_toolbelt
import xml.etree.ElementTree
import yaml

_LOGGER = logging.getLogger(__file__)
_LOGGER.addHandler(logging.NullHandler())

# USER_AGENT = "https://github.com/mpenkov/pyliveleak"
#
# We have to do this to prevent us getting redirected to the mobile site.
#
_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36"
_HTTP_HEADERS = {"User-Agent": _USER_AGENT}
_COOKIE_NAMES = ("PHPSESSID", "liveleak_safe_mode", "liveleak_use_old_player",
                 'liveleak_user_token', 'liveleak_user_password')
#
# Fields must be in the right order.
#
_MULTIPART_FIELDS = (
    "name", "key", "Filename", "acl", "Expires", "Content-Type",
    "success_action_status", "AWSAccessKeyId", "policy", "signature"
)
_CAPTURE_HTML = False
_CURR_DIR = P.dirname(__file__)
_TEXT_ENCODING = 'utf-8'


def load_categories():
    CURR_DIR = P.dirname(__file__)
    with open(P.join(CURR_DIR, 'categories.yml')) as fin:
        return yaml.load(fin)


CATEGORIES = load_categories()
DEFAULT_TITLE = 'title'
DEFAULT_BODY = 'body'
DEFAULT_CATEGORY = 'other'
DEFAULT_TAGS = 'liveleak.py'


class PyLiveleakException(RuntimeError):
    pass


def _capture_html(body, filename):
    if _CAPTURE_HTML:
        path = P.join(_CURR_DIR, 'test-data', filename)
        with codecs.open(path, 'w', _TEXT_ENCODING) as fout:
            fout.write(body)


def login(username, password):
    data = {"user_name": username, "user_password": password, "login": 1}
    post = requests.post("https://www.liveleak.com/index.php",
                         data=data, headers=_HTTP_HEADERS)
    if post.status_code != 200:
        raise PyLiveleakException("login failed (HTTP %d)" % post.status_code)

    cookies = {}
    for name in _COOKIE_NAMES:
        try:
            cookies[name] = post.cookies[name]
        except KeyError as err:
            raise PyLiveleakException('login failed (%r)', err)
    return IndexPage(post.text, cookies)


class IndexPage(object):
    """Represents a logged-in session with liveleak.com."""
    def __init__(self, html, cookies):
        self._html = html
        self._cookies = cookies
        _capture_html(self._html, 'index.html')

    def add_item(self, path, title=None, body=None,
                 tags=DEFAULT_TAGS, category=DEFAULT_CATEGORY):
        if title is None:
            title = P.basename(path)
        if body is None:
            body = P.basename(path)

        get = requests.get("http://www.liveleak.com/item?a=add_item",
                           cookies=self._cookies, headers=_HTTP_HEADERS)
        _LOGGER.debug("add_item GET status_code: %d", get.status_code)
        if get.status_code != 200:
            raise PyLiveleakException("bad HTTP response (%d)" % get.status_code)

        page = AddItemPage(get.text, self._cookies)
        aws_response = page.upload_to_aws(path)
        file_token = page.add_file(path, aws_response)
        item_token = page.publish(title=title, body=body, tags=tags, category=category)
        return file_token, item_token


class AddItemPage(object):
    """Performs the hard work for adding a video to liveleak.com.

    That is a three-stage process:
        1. Upload the video file to liveleak's AWS S3 bucket.
        2. Add the file to liveleak, yielding a file token.
        3. Specify metadata and publish the video."""
    def __init__(self, html, cookies):
        self._html = html
        self._cookies = cookies
        _capture_html(self._html, 'add_item.html')

    @property
    def multipart_params(self):
        """Parse the multipart_params dict from the JavaScript in the page.

        We need these params to upload the file to AWS."""
        return _extract_multipart_params(self._html)

    @property
    def connection(self):
        """Parse the connection number from the page.

        This is unique for each page load."""
        #
        # <input type="hidden" value="6a7_1502274736" name="connection" />
        #
        logging.debug('%s', self._html)
        root = lxml.etree.parse(io.StringIO(self._html), lxml.etree.HTMLParser())
        connection = root.xpath("//input[@name='connection']")
        return connection[0].get("value")

    @property
    def connect_string(self):
        """Parse the connect_string from the page.

        This is unique for each page load."""
        return re.search("connect_string=(?P<cs>[^&]+)", self._html).group("cs")

    def upload_to_aws(self, path):
        """Upload a file to AWS.
        Raises Exception on failure.
        Returns a file_token in case of successs."""
        headers, data = _encode_fields(path, self.multipart_params)
        post = requests.post("https://llbucs.s3.amazonaws.com/",
                             cookies=self._cookies, headers=headers, data=data)
        _LOGGER.debug("POST status_code: %d", post.status_code)
        _LOGGER.debug("add_item POST response: %s", post.text)

        assert post.status_code == 201, "couldn't upload to AWS"
        _capture_html(post.text, 'llbucs.html')

        root = xml.etree.ElementTree.fromstring(post.text)
        aws_response = {}
        for key in ["Location", "Bucket", "Key", "ETag"]:
            aws_response[key] = root.find(key).text
        aws_response['text'] = post.text
        _LOGGER.debug("aws_response: %r", aws_response)
        return aws_response

    def add_file(self, path, aws_response):
        filename = P.basename(path)
        query_params = {
            "a": "add_file",
            "ajax": 1,
            "connect_string": self.connect_string,
            "s3_key": aws_response["Key"],
            "fn": urllib.quote(filename),
            "resp": urllib.quote(aws_response['text'])
        }

        _LOGGER.debug("query_params: %s", query_params)

        get = requests.get("http://www.liveleak.com/file", params=query_params,
                           cookies=self._cookies, headers=_HTTP_HEADERS)
        _capture_html(get.text, 'file.html')
        _LOGGER.debug("GET status_code: %d", get.status_code)
        _LOGGER.debug("GET response: %s", get.text)

        try:
            obj = json.loads(get.text)
        except ValueError:
            raise PyLiveleakException("unable to decode JSON from response")

        if obj["success"] != 1:
            raise PyLiveleakException(obj["msg"])

        return obj["file_token"]

    def publish(self, title=DEFAULT_TITLE, body=DEFAULT_BODY,
                tags=DEFAULT_TAGS, category=DEFAULT_CATEGORY):
        category_num = CATEGORIES.get(category.lower(), CATEGORIES[DEFAULT_CATEGORY])
        data = {
            "title": title,
            "body_text": body,
            "tag_string": tags,
            "category_array[]": category_num,
            "address": "",
            "location_id": 0,
            "is_private": 0,
            "disable_risky_commenters": 0,
            "content_rating": "MA",
            "occurrence_date_string": "",
            "enable_financial_support": 0,
            "financial_support_paypal_email": "",
            "financial_support_bitcoin_address": "",
            "agreed_to_tos": "on",
            "connection": self.connection
        }

        post = requests.post("https://www.liveleak.com/item?a=add_item&ajax=1",
                             data=data, cookies=self._cookies, headers=_HTTP_HEADERS)
        _capture_html(post.text, 'add_item.json')
        _LOGGER.debug("add_item POST status_code: %d", post.status_code)
        _LOGGER.debug("add_item POST response: \n%s", post.text)

        try:
            obj = json.loads(post.text)
            if obj["success"] != 1:
                raise PyLiveleakException('unable to publish item: %r', obj["msg"])
        except ValueError as err:
            raise PyLiveleakException('unable to publish item: %r', err)

        return obj["item_token"]


def _scrub_filename(path):
    #
    # Mangle the filename (add timestamp, remove special characters).
    # This is similar to what the JS in the add_item form does.
    # It isn't exactly the same, but it's good enough.
    #
    filename = P.basename(path)
    fixed_file_name_part, extension = P.splitext(filename)
    fixed_file_name_part = "".join([ch for ch in fixed_file_name_part if ch.isalnum()])
    #
    # Filename must be a raw Python string (not unicode)
    #
    timestamp = time.time()
    return str(fixed_file_name_part + "_" + str(timestamp) + extension)


def _encode_fields(path, params):
    params["name"] = _scrub_filename(path)
    params["key"] = params["key"].replace("${filename}", params['name'])

    fields = [(name, params[name]) for name in _MULTIPART_FIELDS]
    fields.append(("file", ("filename", open(path, "rb"), "video/mp4")))
    _LOGGER.debug("fields: %s", str(fields))

    #
    # http://toolbelt.readthedocs.org/en/latest/user.html#uploading-data
    #
    data = requests_toolbelt.MultipartEncoder(fields=fields)
    headers = {
        "Origin": "http://www.liveleak.com",
        "Accept-Encoding": "gzip,deflate,sdch",
        "Host": "llbucs.s3.amazonaws.com",
        "Accept-Language": "en-US,en;q=0.8,ja;q=0.6,ru;q=0.4",
        "User-Agent": _USER_AGENT,
        "Content-Type": data.content_type,
        "Accept": "*/*",
        "Referer": "http://www.liveleak.com/item?a=add_item",
        "Connection": "keep-alive"
    }
    return headers, data


def _extract_multipart_params(html):
    """Extract the multipart_params dict from the add_item.html.
    Returns a dictionary on success, None on failure."""
    multipart_params = {}
    ptn = re.compile("'(?P<key>%s)' *: *'(?P<value>[^']+)'" % "|".join(_MULTIPART_FIELDS))
    found_params = False
    for line in [l.strip() for l in html.split("\n")]:
        if found_params and line.startswith("},"):
            break
        elif found_params:
            match = ptn.search(line)
            if not match:
                continue
            multipart_params[match.group("key")] = match.group("value")
        elif line.startswith("multipart_params: {"):
            found_params = True
            continue
    for k in _MULTIPART_FIELDS:
        if k not in multipart_params and k != 'name':
            logging.error("missing key: %s", k)
            return None
    return multipart_params
