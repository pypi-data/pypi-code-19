from git import Repo

from mit.commands import Command
from mit.commands.status import Status


class Fetch(Command):

    def _run_for_each_repo(self, repo_name, repo_folder, print_msgs):
        Repo(repo_folder).git.fetch()
        Status()._run_for_each_repo(repo_name, repo_folder, print_msgs)
