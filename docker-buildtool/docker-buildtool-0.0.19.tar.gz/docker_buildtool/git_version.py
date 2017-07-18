import os
import sys
import subprocess
import logging

logger = logging.getLogger(__name__)

def _check_output(command, cwd):
    stdout = subprocess.check_output(command, cwd=cwd, universal_newlines=True,
                               stderr=subprocess.PIPE)
    return stdout.strip()

def _get_success(command, cwd):
    try:
        subprocess.check_call(command, cwd=cwd, universal_newlines=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def _is_git_repo(cwd=None):
    return _get_success(['stat', '.git'], cwd=cwd)

def repo_name(cwd=None):
    git_top_level = _check_output(['git', 'rev-parse', '--show-toplevel'], cwd=cwd)
    return os.path.basename(git_top_level)

def version_number(cwd=None):
    version_number = None
    if _get_success(['cat', 'VERSION'], cwd=cwd):
        version_number = _check_output(['cat', 'VERSION'], cwd=cwd)
    return version_number

def is_versionable(fullpath):
    return (os.path.exists(fullpath) and
            os.path.isdir(fullpath) and
            _is_git_repo(cwd=fullpath))

def _split_nonempty(string):
    if string is None or len(string) == 0:
        return None
    else:
        return [s.strip() for s in string.split('\n')]

def git_version(fetch=True, cwd=None):
    # If requested, attempt to fetch remote
    version = {}
    version['fetch'] = fetch
    if fetch:
        command = ['git', 'fetch']
        logger.info('Running %s in %s', ' '.join(command), cwd)
        fetch_success = _get_success(command, cwd=cwd)
        version['fetch_success'] = fetch_success
    else:
        version['fetch_success'] = None
    version['branch_name'] = _check_output(['git', 'name-rev', 'HEAD', '--name-only'], cwd=cwd)
    version['short_hash'] = _check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=cwd)

    # Does this branch have a remote equivalent at origin?
    try:
        version['symbolic_ref'] = _check_output(['git', 'symbolic-ref', '--q', 'HEAD'], cwd=cwd)
    except subprocess.CalledProcessError as e:
        # Generally happens when not on a branch
        logger.warn('WARNING: Could not determine your branch name: %s', e)
        has_remote_branch = False
    else:
        version['remote_branch'] = _check_output(['git', 'for-each-ref', '--format=%(upstream:short)',
                                                  version['symbolic_ref']], cwd=cwd)
        has_remote_branch = _get_success(['git', 'rev-parse', '--verify',
                                          version['remote_branch']], cwd=cwd)

    if has_remote_branch:
        # If so, how does the local committed state differ from the remote state?
        version['additional_remote_commits'] = _split_nonempty(_check_output(['git', 'log', '{}..{}'.format(
            version['branch_name'], version['remote_branch']), '--decorate', '--oneline'], cwd=cwd))
        version['additional_local_commits'] = _split_nonempty(_check_output(['git', 'log', '{}..{}'.format(
            version['remote_branch'], version['branch_name']), '--decorate', '--oneline'], cwd=cwd))

    version['uncommitted_changes'] = _split_nonempty(_check_output(['git', 'status', '--porcelain'], cwd=cwd))
    version['submodules'] = _split_nonempty(_check_output(['git', 'submodule'], cwd=cwd))
    return version

def pretty_string(version):
    # Build a string to print out!
    version_string = ''
    if not version['fetch']:
        if 'branch_name' in version:
            version_string += '{} {} (Not fetched)\n'.format(version['branch_name'], version['short_hash'])
        else:
            version_string += version['message']
    else:
        if version['fetch_success']:
            version_string += '{} {} (Fetched)\n'.format(version['branch_name'], version['short_hash'])
        else:
            version_string += '{} {} (Failed to fetch)\n'.format(version['branch_name'], version['short_hash'])
    if version.get('additional_remote_commits', None) is not None:
        for s in version['additional_remote_commits']:
            version_string += 'Unmerged remote: {}\n'.format(s)
    if version.get('additional_local_commits', None) is not None:
        for s in version['additional_local_commits']:
            version_string += 'Unpushed local: {}\n'.format(s)
    if version.get('uncommitted_changes', None) is not None:
        for s in version['uncommitted_changes']:
            version_string += '{}\n'.format(s)
    if version.get('submodules', None) is not None:
        for s in version['submodules']:
            version_string += 'Submodule: {}\n'.format(s)

    return version_string.strip()
