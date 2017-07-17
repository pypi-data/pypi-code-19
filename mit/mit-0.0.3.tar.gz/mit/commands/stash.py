from enum import Enum
from git import Repo

from mit.commands import Command


class Stash(Command):

    class Type(Enum):
        STASH = 1
        POP = 2

    def __init__(self, stash_type):
        self.stash_type = stash_type

    def _run_for_each_repo(self, repo_name, repo_folder, print_msgs):

        git_repo = Repo(repo_folder)
        if self.stash_type == Stash.Type.STASH:
            git_repo.git.stash("save")
        else:
            git_repo.git.stash("pop")
