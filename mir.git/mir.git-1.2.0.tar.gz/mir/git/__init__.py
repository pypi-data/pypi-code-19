# Copyright (C) 2017 Allen Li
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Python interface to Git.

The main member of this module is the git() generic function.

The most general git() method is for GitEnv instances, which describes a
Git invocation environment.

Most users can use the string git() method, which will be interpreted as
the working tree for a standard non-bare Git repo.

If you have your own Git wrappers, you can register a git() method for
it so git() can accept them as environments transparently.

Members:

git() -- All-purpose generic function interface to Git
GitEnv -- Git invocation environment
default_encoding -- Default encoding for subprocesses

get_current_branch()
get_branches()
has_staged_changes()
has_unpushed_changes()
has_unstaged_changes()
save_branch()
save_worktree()
"""

import functools
import logging
import os
from pathlib import Path
import subprocess

__version__ = '1.2.0'

logger = logging.getLogger(__name__)
default_encoding = 'utf-8'


class GitEnv:

    """Environment for Git invocations."""

    def __init__(self, gitdir: 'PathLike', worktree: 'PathLike'):
        self.gitdir = Path(gitdir).expanduser()
        self.worktree = Path(worktree).expanduser()


@functools.singledispatch
def git(env, args, **kwargs):
    """Run a Git command.

    env is a Git environment, or some representation of a Git
    environment.  args and kwargs are passed to subprocess.run().

    Additional methods should be implemented by creating a suitable
    GitEnv instance and calling git() again with it.

    Returns a CompletedProcess.
    """
    raise NotImplementedError


@git.register(GitEnv)
def _git_gitenv(env, args, **kwargs):
    kwargs.setdefault('encoding', default_encoding)
    return subprocess.run(
        ['git', '--git-dir', str(env.gitdir),
         '--work-tree', str(env.worktree), *args],
        **kwargs)


@git.register(os.PathLike)
@git.register(str)
def _git_str(worktree, args, **kwargs):
    env = GitEnv(gitdir=Path(worktree) / '.git',
                 worktree=worktree)
    return git(env, args, **kwargs)


def has_unpushed_changes(env) -> bool:
    """Return True if the Git repo has unpushed changes."""
    result = git(env, ['rev-list', '-n', '1', 'HEAD@{u}..HEAD'],
                 stdout=subprocess.PIPE)
    return bool(result.stdout)


def has_staged_changes(env) -> bool:
    """Return True if the Git repo has staged changes."""
    result = git(env, ['diff-index', '--quiet', '--cached', 'HEAD'])
    return result.returncode != 0


def has_unstaged_changes(env) -> bool:
    """Return True if the Git repo has unstaged changes."""
    result = git(env, ['diff-index', '--quiet', 'HEAD'])
    return result.returncode != 0


def get_current_branch(env) -> str:
    """Return the current Git branch."""
    return git(env, ['rev-parse', '--abbrev-ref', 'HEAD'],
               stdout=subprocess.PIPE).stdout.rstrip()


def get_branches(env) -> list:
    """Return a list of a Git repository's branches."""
    proc = git(env, ['for-each-ref', '--format=%(refname)', 'refs/heads/'],
               check=True, stdout=subprocess.PIPE)
    output = proc.stdout.splitlines()
    start = len('refs/heads/')
    return [line.rstrip()[start:] for line in output]


class save_branch:

    """Context manager for saving and restoring the current Git branch."""

    def __init__(self, env):
        self._env = env
        self.starting_branch = None

    def __enter__(self):
        self.starting_branch = get_current_branch(self._env)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        git(self._env, ['checkout', '--quiet', '--force', self.starting_branch],
            check=True)


class save_worktree(save_branch):

    """Context manager for saving and restoring the worktree."""

    def __init__(self, env):
        super().__init__(env)
        self._stash = ''

    def __enter__(self):
        proc = git(self._env, ['stash', 'create'],
                   stdout=subprocess.PIPE)
        self._stash = proc.stdout.rstrip()
        logger.debug(f'Created stash {self._stash!r}')
        git(self._env, ['reset', '--hard', '--quiet', 'HEAD'])
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        if self._stash:
            git(self._env, ['stash', 'apply', '--quiet', self._stash])
