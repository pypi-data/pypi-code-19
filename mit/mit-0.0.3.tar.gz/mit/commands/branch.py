from colorama import Fore, Style
from git import Repo

from mit.commands import Command
from mit.commands.printer import Printer


class Branch(Command):

    def _run_for_each_repo(self, repo_name, repo_folder, print_msgs):
        message = Printer.get_prefix(repo_name)
        git_repo = Repo(repo_folder)
        current_branch_name = git_repo.active_branch.name
        first_branch = True
        for branch in git_repo.branches:
            if first_branch:
                first_branch = False
            else:
                message += "\n\t"
            branch_name = branch.name
            fore_color = Fore.LIGHTGREEN_EX if branch_name == current_branch_name else Fore.LIGHTWHITE_EX
            message += fore_color + branch_name + Style.RESET_ALL
        Printer.p(message)
