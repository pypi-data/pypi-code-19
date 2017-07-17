from git import Repo

from mit.commands import Command
from mit.commands.printer import Printer


class Rebase(Command):

    def __init__(self, from_branch, to_branch):
        self.from_branch = from_branch
        self.to_branch = to_branch

    def _run_for_each_repo(self, repo_name, repo_folder, print_msgs):
        message = Printer.get_prefix(repo_name)
        git_repo = Repo(repo_folder)

        from_branch_found = False
        to_branch_found = False
        can_rebase = False

        for branch in git_repo.branches:
            if branch.name == self.from_branch:
                from_branch_found = True
            elif branch.name == self.to_branch:
                to_branch_found = True

            if from_branch_found and to_branch_found:
                can_rebase = True
                break

        if can_rebase:
            git_repo.git.rebase(self.from_branch + " " + self.to_branch)

        Printer.p(message)
