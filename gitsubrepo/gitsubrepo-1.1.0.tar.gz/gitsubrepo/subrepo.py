import os
import re
from typing import Callable, Tuple, NewType

from gitsubrepo._common import run
from gitsubrepo._git import requires_git, GIT_COMMAND, get_git_root_directory, get_directory_relative_to_git_root
from gitsubrepo.exceptions import UnstagedChangeException, NotAGitRepositoryException, RunException, \
    NotAGitReferenceException, NotAGitSubrepoException

_GIT_SUBREPO_COMMAND = "subrepo"
_GIT_SUBREPO_CLONE_COMMAND = "clone"
_GIT_SUBREPO_STATUS_COMMAND = "status"
_GIT_SUBREPO_PULL_COMMAND = "pull"
_GIT_SUBREPO_BRANCH_FLAG = "--branch"
_GIT_SUBREPO_VERBOSE_FLAG = "-v"
_GIT_LS_REMOTE_COMMAND = "ls-remote"

_DEFAULT_BRANCH = "master"

_GIT_AUTHOR_NAME_ENVIRONMENT_VARIABLE = "GIT_AUTHOR_NAME"
_GIT_AUTHOR_EMAIL_ENVIRONMENT_VARIABLE = "GIT_AUTHOR_EMAIL"

Branch = NewType("Branch", str)
Commit = NewType("Commit", str)
RepositoryLocation = NewType("RepositoryLocation", str)


@requires_git
def requires_subrepo(func: Callable) -> Callable:
    """
    Decorator that requires the `git subrepo` command to be accessible before calling the given function.
    :param func: the function to wrap
    :return: the wrapped function
    """
    def decorated(*args, **kwargs):
        try:
            run([GIT_COMMAND, _GIT_SUBREPO_COMMAND, "--version"])
        except RunException as e:
            raise RuntimeError("`git subrepo` does not appear to be working") from e
        return func(*args, **kwargs)

    return decorated


@requires_subrepo
def clone(location: str, directory: str, *, branch: str=None, tag: str=None, commit: str=None, author_name: str=None,
          author_email: str=None) -> Commit:
    """
    Clones the repository at the given location as a subrepo in the given directory.
    :param location: the location of the repository to clone
    :param directory: the directory that the subrepo will occupy (i.e. not the git repository root)
    :param branch: the specific branch to clone
    :param tag: the specific tag to clone
    :param commit: the specific commit to clone (may also require tag/branch to be specified if not fetched)
    :param author_name: the name of the author to assign to the clone commit (uses system specified if not set)
    :param author_email: the email of the author to assign to the clone commit (uses system specified if not set)
    :return: the commit reference of the checkout
    """
    if os.path.exists(directory):
        raise ValueError(f"The directory \"{directory}\" already exists")
    if not os.path.isabs(directory):
        raise ValueError(f"Directory must be absolute: {directory}")
    if branch and tag:
        raise ValueError(f"Cannot specify both branch \"{branch}\" and tag \"{tag}\"")
    if not branch and not tag and not commit:
        branch = _DEFAULT_BRANCH

    existing_parent_directory = directory
    while not os.path.exists(existing_parent_directory):
        assert existing_parent_directory != ""
        existing_parent_directory = os.path.dirname(existing_parent_directory)

    git_root = get_git_root_directory(existing_parent_directory)
    git_relative_directory = os.path.relpath(os.path.realpath(directory), git_root)

    if (branch or tag) and commit:
        run([GIT_COMMAND, "fetch", location, branch if branch else tag], execution_directory=git_root)
        branch, tag = None, None
    reference = branch if branch else (tag if tag else commit)

    execution_environment = os.environ.copy()
    if author_name is not None:
        execution_environment[_GIT_AUTHOR_NAME_ENVIRONMENT_VARIABLE] = author_name
    if author_email is not None:
        execution_environment[_GIT_AUTHOR_EMAIL_ENVIRONMENT_VARIABLE] = author_email

    try:
        run([GIT_COMMAND, _GIT_SUBREPO_COMMAND, _GIT_SUBREPO_CLONE_COMMAND, _GIT_SUBREPO_VERBOSE_FLAG,
             _GIT_SUBREPO_BRANCH_FLAG, reference, location, git_relative_directory], execution_directory=git_root,
            execution_environment=execution_environment)
    except RunException as e:
        if re.search("Can't clone subrepo. (Unstaged|Index has) changes", e.stderr) is not None:
            raise UnstagedChangeException(git_root) from e
        elif "Command failed:" in e.stderr:
            try:
                repo_info = run([GIT_COMMAND, _GIT_LS_REMOTE_COMMAND, location])
                if not branch and not tag and commit:
                    raise NotAGitReferenceException(
                        f"Commit \"{commit}\" not found (specify branch/tag to fetch that first if required)")
                else:
                    references = re.findall("^.+\srefs\/.+\/(.+)", repo_info, flags=re.MULTILINE)
                    if reference not in references:
                        raise NotAGitReferenceException(f"{reference} not found in {references}") from e

            except RunException as debug_e:
                if re.match("fatal: repository .* not found", debug_e.stderr):
                    raise NotAGitRepositoryException(location) from e
        raise e

    assert os.path.exists(directory)
    return status(directory)[2]


@requires_subrepo
def status(directory: str) -> Tuple[RepositoryLocation, Branch, Commit]:
    """
    Gets the status of the subrepo that has been cloned into the given directory.
    :param directory: the directory containing the subrepo
    :return: a tuple consisting of the URL the subrepo is tracking, the branch that has been checked out and the commit
    reference
    """
    if not os.path.exists(directory):
        raise ValueError(f"No subrepo found in \"{directory}\"")

    try:
        result = run([GIT_COMMAND, _GIT_SUBREPO_COMMAND, _GIT_SUBREPO_STATUS_COMMAND, _GIT_SUBREPO_VERBOSE_FLAG,
                      get_directory_relative_to_git_root(directory)],
                     execution_directory=get_git_root_directory(directory))
    except RunException as e:
        if "Command failed: 'git rev-parse --verify HEAD'" in e.stderr:
            raise NotAGitSubrepoException(directory) from e
        raise e

    if re.search("is not a subrepo$", result):
        raise NotAGitSubrepoException(directory)

    url = re.search("Remote URL:\s*(.*)", result).group(1)
    branch = re.search("Tracking Branch:\s*(.*)", result).group(1)
    commit = re.search("Pulled Commit:\s*(.*)", result).group(1)
    return url, branch, commit


@requires_subrepo
def pull(directory: str) -> Commit:
    """
    Pulls the subrepo that has been cloned into the given directory.
    :param directory: the directory containing the subrepo
    :return: the commit the subrepo is on
    """
    if not os.path.exists(directory):
        raise ValueError(f"No subrepo found in \"{directory}\"")
    try:
        result = run([GIT_COMMAND, _GIT_SUBREPO_COMMAND, _GIT_SUBREPO_PULL_COMMAND, _GIT_SUBREPO_VERBOSE_FLAG,
                      get_directory_relative_to_git_root(directory)],
                     execution_directory=get_git_root_directory(directory))
    except RunException as e:
        if "Can't pull subrepo. Working tree has changes" in e.stderr:
            raise UnstagedChangeException() from e
    return status(directory)[2]


