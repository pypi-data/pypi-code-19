import os
from typing import Callable

from gitsubrepo._common import run
from gitsubrepo.exceptions import NotAGitRepositoryException, RunException

GIT_COMMAND = "git"


def requires_git(func: Callable) -> Callable:
    """
    Decorator to ensure `git` is accessible before calling a function.
    :param func: the function to wrap
    :return: the wrapped function
    """
    def decorated(*args, **kwargs):
        try:
            run([GIT_COMMAND, "--version"])
        except RunException as e:
            raise RuntimeError("`git` does not appear to be working") from e
        return func(*args, **kwargs)

    return decorated


@requires_git
def get_git_root_directory(directory: str):
    """
    Gets the path of the git project root directory from the given directory.
    :param directory: the directory within a git repository
    :return: the root directory of the git repository
    :exception NotAGitRepositoryException: raised if the given directory is not within a git repository
    """
    try:
        return run([GIT_COMMAND, "rev-parse", "--show-toplevel"], directory)
    except RunException as e:
        if " Not a git repository" in e.stderr:
            raise NotAGitRepositoryException(directory) from e


def get_directory_relative_to_git_root(directory: str):
    """
    Gets the path to the given directory relative to the git repository root in which it is a subdirectory.
    :param directory: the directory within a git repository
    :return: the path to the directory relative to the git repository root
    """
    return os.path.relpath(os.path.realpath(directory), get_git_root_directory(directory))
