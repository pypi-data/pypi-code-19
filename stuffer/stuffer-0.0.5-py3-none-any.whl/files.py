import shutil
import urllib.request
from pathlib import Path

from stuffer import content
from stuffer.core import Action


class Chmod(Action):
    """Set permissions for a file."""

    def __init__(self, permissions, path):
        self.permissions = permissions
        self.path = Path(path)
        super().__init__()

    def command(self):
        return "chmod {:o} {}".format(self.permissions, str(self.path))

    def __repr__(self):
        return "Chmod(permissions=0o{:o}, path={})".format(self.permissions, str(self.path))


class Chown(Action):
    """Set ownership for files."""

    def __init__(self, owner, path, group=None, recursive=False):
        self.owner = owner
        self.path = path
        self.group = group
        self.recursive = recursive
        super().__init__()

    def command(self):
        return "chown {} {}{} {}".format(
            "--recursive" if self.recursive else "",
            self.owner,
            "." + self.group if self.group else "",
            self.path)


class Content(Action):
    """Set the contents of a file."""

    def __init__(self, path, contents, make_dirs=False):
        self.path = Path(path)
        self.contents = content.supplier(contents)
        self.make_dirs = make_dirs
        super(Content, self).__init__()

    def run(self):
        write_file_atomically(self.path, self.contents(), make_dirs=self.make_dirs)


class DownloadFile(Action):
    """Download and install a single file from a URL."""

    def __init__(self, url, path):
        self.url = url
        self.path = Path(path)
        super().__init__()

    def run(self):
        local_file, _ = urllib.request.urlretrieve(self.url)
        shutil.move(local_file, str(self.path))


class Mkdir(Action):
    """Create a directory, unless it exists."""

    def __init__(self, path):
        self.path = path
        super().__init__()

    def command(self):
        return "mkdir -p {}".format(self.path)


class Transform(Action):
    """Transform the contents of a file"""

    def __init__(self, path, transform):
        self.path = Path(path)
        self.transform = transform
        super(Transform, self).__init__()

    def run(self):
        with self.path.open() as f:
            new_content = self.transform(f.read())
        write_file_atomically(self.path, new_content)


def write_file_atomically(path, contents, make_dirs=False, suffix=".stuffer_tmp"):
    tmp_file = path.with_suffix(path.suffix + suffix)
    if make_dirs:
        tmp_file.parent.mkdir(parents=True, exist_ok=True)
    with tmp_file.open('w') as tmp:
        tmp.write(contents)
    try:
        tmp_file.replace(path)
    except:
        if path.exists() and tmp_file.exists():
            tmp_file.unlink()
        raise
