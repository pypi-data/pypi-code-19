from colorama import Fore
from git import Repo

from mit.commands import Command
from mit.commands.printer import Printer


class Checkout(Command):

    def __init__(self, branch):
        self.branch = branch

    def _run_for_each_repo(self, repo_name, repo_folder, print_msgs):
        git_repo = Repo(repo_folder)

        message = Printer.get_prefix(repo_name)

        if self.branch == git_repo.active_branch.name:
            message += Fore.LIGHTWHITE_EX + " already on " + self.branch
        else:
            branch_exists = False
            for branch in git_repo.branches:
                if branch.name == self.branch:
                    self.branch = branch.name
                    branch_exists = True
                    break

            if not branch_exists:
                for branch in git_repo.branches:
                    if branch.name.startswith(self.branch):
                        self.branch = branch.name
                        branch_exists = True
                        break

            if branch_exists:
                git_repo.git.checkout(self.branch)
                message += Fore.LIGHTGREEN_EX + " now on " + self.branch + ""
            else:
                message += Fore.LIGHTYELLOW_EX + " does not have this branch"

        Printer.p(message)
