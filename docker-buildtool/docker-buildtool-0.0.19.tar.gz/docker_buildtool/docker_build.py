import datetime
import logging
import os
import platform
import re
import six
import subprocess
import tempfile
import time
import yaml

if six.PY2:
    import glob2 as glob
else:
    import glob

from docker_buildtool import error, utils, versioner

VERSIONFILE = '.docker-buildtool-versions'

logger = logging.getLogger(__name__)

def expand_include(paths, build_root):
    expanded = []
    for path in paths:
        matches = glob.glob(os.path.join(build_root, path), recursive=True)
        if '*' not in path:
            assert len(matches) > 0, 'No matches found for path'

        expanded += matches

    truncated = []
    for e in expanded:
        assert e.startswith(build_root+'/')
        truncated.append(e[len(build_root)+1:])
    return truncated

def expand_ignore(ignore, include_paths, build_root):
    # As a slight optimization, we explicitly ignore any directories
    # we're definitely not going to need. Seems to stop docker from
    # traversing those directories (and all the files in them would be
    # excluded via the * exclude.)
    included = set()
    for path in include_paths:
        base = path.split('/')[0]
        included.add(base)

    for d in os.listdir(build_root):
        if not os.path.isdir(d):
            continue
        d = os.path.basename(d)
        if d in included:
            continue
        ignore.append(d)
    return ignore

class DockerBuild(object):
    def __init__(self, dockerfile, build_root, include, docker_repo, workdir=None, ignore=None, tag=None, default_ignore=None, include_version_file=False, variables=None, fetch=False, no_ignore_override=False, quiet=False, _raw_build_root=None):
        self._raw_build_root = _raw_build_root
        self.dockerfile = os.path.abspath(dockerfile)
        self.build_root = os.path.abspath(build_root or os.getcwd())
        self.workdir = workdir
        self.include = include
        self.docker_repo = docker_repo
        if tag is None:
            tag = 'latest'
        self.tag = tag
        self.ignore = ignore or []
        self.dockerignore = os.path.join(self.build_root, '.dockerignore')
        if variables is None:
            variables = {}
        self.variables = variables
        self.include_version_file = include_version_file
        self.fetch = fetch
        self.no_ignore_override = no_ignore_override
        self.quiet = quiet

        # TODO: phase this out
        if default_ignore or default_ignore is None:
            self.default_ignore = ['**/.git', '**/*.egg-info', '**/*.o']
        else:
            self.default_ignore = []

    def backup_dockerignore(self, dryrun):
        bak = None
        if os.path.exists(self.dockerignore):
            bak = os.path.join(self.build_root, '.dockerignore.tmp.{}'.format(time.time()))
            utils.rename(dryrun, self.dockerignore, bak)
        return bak

    def restore_dockerignore(self, dryrun, bak):
        if bak is None:
            utils.unlink(dryrun, self.dockerignore)
        else:
            utils.rename(dryrun, bak, self.dockerignore)

    def write_dockerignore(self, dryrun, lines):
        for line in lines:
            assert isinstance(line, str), 'Invalid dockerignore line type {}: {}'.format(type(line), line)

        contents = '# Auto-generated dockerignore by docker_build.py\n' + '\n'.join(lines) + '\n'
        utils.write(dryrun, self.dockerignore, contents)

    def write_dockerfile(self, dryrun):
        with open(self.dockerfile) as f:
            original = f.readlines()

        contents = []
        for line in original:
            transformed = False

            # Expand includes
            match = re.search('^#docker-buildtool:include (.*)$', line)
            if match is not None:
                transformed = True

                include_path = match.group(1)
                logger.info('Including into Dockerfile: path=%s', include_path)
                with open(os.path.join(self.build_root, include_path)) as f:
                    include = f.read()
                line = '''
# starting include from {}
{}
# ending include from {}
'''.format(include_path, include, include_path)

            # Expand variables, right now just supporting a single
            # word until end of line.
            match = re.search('^(.*)#docker-buildtool:variable ([\w-]*)$', line)
            if not transformed and match is not None:
                transformed = True

                prefix = match.group(1)
                variable = match.group(2)
                if variable not in self.variables:
                    raise error.UndefinedVariable('No such variable: {}'.format(variable))
                logger.info('Substituting variable: variable=%s', variable)
                line = "{}{}".format(prefix, self.variables[variable])
            contents.append(line.strip())


        # add versionfile build arg
        if self.include_version_file:
            contents.append("""
COPY {} /usr/local/dependency-versions.txt
""".format(VERSIONFILE))

        if self.workdir is not None:
            contents.append("""

# Ending auto-generated by docker_build.py
WORKDIR {}
""".format(self.workdir))

        tmpfile = utils.named_temporary_file(dryrun, dir=self.build_root)
        utils.write(dryrun, tmpfile.name, '\n'.join(contents))

        return tmpfile

    def write_version_string(self, outfile, timestamp, dryrun=False):
        v = versioner.Versioner(dockerfile=self.dockerfile)
        versions = v.run(fetch=(not dryrun and self.fetch))
        versions['timestamp'] = timestamp
        versions['iso_timestamp'] = datetime.datetime.fromtimestamp(timestamp).isoformat()
        utils.write(dryrun, outfile, yaml.dump(versions))

    def write_dockerfile_and_dockerignore(self, dryrun):
        include_paths = []
        for entry in self.include:
            path = entry.to_path(build_root=self.build_root)
            include_paths.append(path)

        # Run this before computing ignore, so we don't include it in the container
        custom_dockerfile = self.write_dockerfile(dryrun)

        # Empirically, dockerignore doesn't seem to expand negated
        # ** (or interior *) patterns. We expand these ourselves.
        include_paths = expand_include(include_paths, self.build_root)
        ignore_paths = expand_ignore(self.ignore, include_paths, self.build_root)

        # Ignore everything that's not whitelisted
        ignore = ['*'] + \
                 ['!'+include for include in include_paths] + \
                 ['!{}'.format(VERSIONFILE)] + \
                 ignore_paths + \
                 self.default_ignore

        if not self.no_ignore_override:
            bak = self.backup_dockerignore(dryrun)
            self.write_dockerignore(dryrun, ignore)
        else:
            bak = None
        return custom_dockerfile, bak

    def run(self, dryrun=False, docker_args=[]):

        custom_dockerfile = None
        backup_dockerignore = None
        versionfile = None

        try:
            custom_dockerfile, backup_dockerignore = self.write_dockerfile_and_dockerignore(dryrun)

            if self.docker_repo is not None:
                image = '{}:{}'.format(self.docker_repo, self.tag)
                tag = ['-t', image]
            else:
                tag = []

            if self.include_version_file:
                timestamp=int(time.time())
                versionfile = os.path.join(self.build_root, VERSIONFILE)
                logger.debug("Including version file. Temporary file at %s", versionfile)
                self.write_version_string(outfile=versionfile, timestamp=timestamp, dryrun=dryrun)

            kwargs = {}
            if self.quiet:
                kwargs = {'stdout': subprocess.DEVNULL}

            # In docker 1.13 and up, you can compress the build
            # context.
            compress = compress_arg()
            utils.execute_command(
                dryrun, ['docker', 'build', '-f', custom_dockerfile.name]
                + tag + compress + docker_args + [self.build_root], **kwargs)

        finally:
            if custom_dockerfile:
                custom_dockerfile.close()
            if versionfile:
                try:
                    utils.unlink(dryrun, versionfile)
                except OSError:
                    pass
            if not self.no_ignore_override:
                self.restore_dockerignore(dryrun, backup_dockerignore)

def docker_version():
    """Returns a triplet describing a docker version or None
    if we failed to determine it.
    """
    cmd_out = subprocess.check_output(["docker", "version"], universal_newlines=True)
    cmd_tokens = [w.lower() for w in cmd_out.replace(':', ' ').split() if len(w) > 0]

    tokens_to_find = ['client', 'version']

    version_string = None
    for token in cmd_tokens:
        if len(tokens_to_find) == 0:
            version_string = token
            break
        if token == tokens_to_find[0]:
            tokens_to_find = tokens_to_find[1:]

    try:
        a, b, c = version_string.split('.')
        return (int(a), int(b), int(c))
    except Exception:
        return None

def compress_arg():
    version = docker_version()
    if version is not None and version >= (1, 13, 0):
        return ['--compress=true']
    else:
        return []
