import tarfile
import urllib.request
import os
import hashlib
import json
from . import _config

base_path = os.path.expanduser(_config.BASE_PATH)

if not os.path.exists(base_path):
    os.mkdir(base_path)


def _download(dataset_url, download_path):
    print('Downloading dataset')
    urllib.request.urlretrieve(dataset_url, download_path)
    print('Downloading done')


def _get_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def load_json_from_url(url):
    req = urllib.request.Request(url)
    return json.loads(urllib.request.urlopen(req).read().decode('utf-8'))


def _extract(archive_path, target_path):
    print('Extracting dataset')
    with tarfile.open(archive_path) as f:
        f.extractall(target_path)


def _download_and_extract(url, title, archive_hash):
    download_path = os.path.join(base_path, os.path.basename(url))
    target_path = os.path.join(base_path, title)

    _download(url, download_path)

    if _get_hash(download_path) != archive_hash:
        raise Exception('Archive is corrupted')

    _extract(download_path, os.path.join(base_path, title))

    return target_path


def maybe_download_and_extract(url, title, archive_hash):
    download_path = os.path.join(base_path, os.path.basename(url))
    target_path = os.path.join(base_path, title)

    if os.path.exists(target_path):
        return target_path
    elif os.path.isfile(download_path):
        if _get_hash(download_path) != archive_hash:
            os.remove(download_path)
            _download_and_extract(url, title, archive_hash)
        else:
            _extract(download_path, target_path)
        return target_path
    else:
        _download_and_extract(url, title, archive_hash)
    return target_path
