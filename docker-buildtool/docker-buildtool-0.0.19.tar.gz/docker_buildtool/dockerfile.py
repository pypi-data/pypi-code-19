import logging
import os
import six
import yaml
import logging

from docker_buildtool import error, utils, git_version

logger = logging.getLogger(__name__)

class UserError(error.Error):
    pass

def assert_path(path, msg=None):
    if os.path.exists(path):
        return

    base = "Missing required path: {}".format(path)
    if msg is not None:
        base += '. {}'.format(msg)
    raise error.Error(base)

def path_from(file, *args):
    return os.path.join('.', os.path.dirname(file), *args)

def load_frontmatter(path):
    contents = []
    line_number = 0

    with open(path) as f:
        first = f.readline()
        line_number += 1
        if first != '# ---\n':
            return None, 'No frontmatter parsed from the head of {}. Must start with "# ---".'.format(path)

        for line in f:
            line_number += 1
            if line == '# ---\n':
                # Reached the end!
                break
            elif line[:2] == '# ':
                # Contents
                line = line[1:]
                contents.append(line)
            else:
                raise UserError('Malformed docker-buildtool frontmatter {}:{}: {!r} must start with "# ". Frontmatter ends when it sees this marker: "# ---"'.format(path, line_number, line))

    contents = ''.join(contents)
    return yaml.load(contents), None

def parse_include(includes):
    parsed = []
    for entry in includes:
        if isinstance(entry, six.string_types):
            include = StringInclude(entry)
        elif isinstance(entry, dict):
            path = entry['path']
            git = entry['git']
            setup = entry.get('setup')
            include = GitInclude(path, git, setup)
        else:
            raise error.Error('Bad include spec: {}'.format(include))
        parsed.append(include)
    return parsed

class StringInclude(object):
    installable = False

    def __init__(self, path):
        self.path = path
        self.installable = False

    def to_path(self, build_root):
        if '*' not in self.path: # don't try sanity checking patterns
            assert_path(os.path.join(build_root, self.path), '(While looking for specified include path {}.)'.format(self.path))
        return self.path

    def __str__(self):
        return '<StringInclude path={!r}>'.format(self.path)

class GitInclude(object):
    installable = True

    def __init__(self, path, git, setup):
        self.path = path
        self.git = git
        self.setup = setup

    def to_path(self, build_root):
        # Check if there's at least a directory there. (We can't
        # mandate anything about the actual git commit, since on
        # devboxes people may not sync their .git).
        fullpath = os.path.join(build_root, self.path)
        assert_path(fullpath, '(HINT: you can obtain this by running "git clone {} {}")'.format(self.git, fullpath))
        return self.path

    def install(self, dryrun, build_root):
        path = os.path.join(build_root, self.path)
        if not os.path.exists(path):
            utils.execute_command(dryrun, ['git', 'clone', self.git, path])
            utils.execute_command(dryrun, self.setup, cwd=path, shell=True)
        else:
            # Pull in everything!
            utils.execute_command(dryrun, ['git', 'pull', '--rebase'], cwd=path)

    def __str__(self):
        return '<GitInclude git={!r} path={!r}>'.format(self.git, self.path)

class DockerfileBuildSpec(object):
    def __init__(self, path):
        self.frontmatter, self.frontmatter_reason = load_frontmatter(path)
        if self.frontmatter is None:
            frontmatter = {'no_ignore_override': True}
            self.has_frontmatter = False
            self.include_version_file = False
        else:
            frontmatter = self.frontmatter
            self.has_frontmatter = True
            self.include_version_file = frontmatter.get('include_version_file', True) # default true on this one!

        self.dockerfile = path
        self._raw_build_root = frontmatter.get('build_root', '.')
        self.build_root = path_from(self.dockerfile, self._raw_build_root)
        include = frontmatter.get('include', [])
        include = parse_include(include)
        self.include = include
        self.ignore = frontmatter.get('ignore', [])
        self.workdir = frontmatter.get('workdir')
        self.default_ignore = frontmatter.get('default_ignore')
        self.setup = frontmatter.get('setup')
        self.no_ignore_override = frontmatter.get('no_ignore_override', False)

    def run_setup(self, dryrun):
        if self.setup is None:
            return
        # TODO: figure out how to bring this back. Most setups
        # probably would require 'sudo'.
        return
        utils.execute_command(dryrun, self.setup, cwd=path_from(self.dockerfile), shell=True)
