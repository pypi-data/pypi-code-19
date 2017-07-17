# coding=utf-8

from colorama import Fore
from git import Repo
from git.exc import GitCommandError

from mit.commands import Command
from mit.commands.printer import Printer
from mit.commands.status import Status


class Pull(Command):

    def _run_for_each_repo(self, repo_name, repo_folder, print_msgs):
        git_repo = Repo(repo_folder)
        try:
            git_repo.git.pull("--rebase")
            Status()._run_for_each_repo(repo_name, repo_folder, print_msgs)
        except GitCommandError:
            branch_name = git_repo.active_branch.name
            message = Printer.get_prefix(repo_name) + Fore.LIGHTWHITE_EX + " (" + branch_name + ")"
            message += " - " + Fore.LIGHTRED_EX + "✘ could not pull rebase!"
            Printer.p(message)
