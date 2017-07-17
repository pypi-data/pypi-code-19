# coding=utf-8

from colorama import Fore, Style
from git import Repo

from mit.commands import Command
from mit.commands.printer import Printer


class Status(Command):

    __STATUS_MESSAGE_PATTERN_BY = " by "
    __STATUS_MESSAGE_PATTERN_COMMIT = " commit"

    def _run_for_each_repo(self, repo_name, repo_folder, print_msgs):

        git_repo = Repo(repo_folder)
        status = git_repo.git.status()
        branch_name = git_repo.active_branch.name

        message = Printer.get_prefix(repo_name) + Fore.LIGHTWHITE_EX + " (" + branch_name + ")" + Style.RESET_ALL + " - "

        if "behind" in status:
            message += Fore.LIGHTYELLOW_EX + self.__get_commits_count(status) + " behind"
        elif "diverged" in status:
            message += Fore.LIGHTRED_EX + "✘ diverged"
        elif "ahead" in status:
            message += Fore.LIGHTBLUE_EX + self.__get_commits_count(status) + " ahead"
        else:
            message += Fore.LIGHTGREEN_EX + "✓ updated"

        untracked_files_count = Status.__get_untracked_files_count(git_repo)
        if untracked_files_count > 0:
            message += Style.RESET_ALL + " - " + Fore.LIGHTWHITE_EX + "untracked(" + str(untracked_files_count) + ")"

        modified_files_count = Status.__get_modified_files_count(git_repo)
        if modified_files_count > 0:
            message += Style.RESET_ALL + " - " + Fore.LIGHTWHITE_EX + "modified(" + str(modified_files_count) + ")"

        if print_msgs:
            Printer.p(message)

    def __get_commits_count(self, status_message):
        message = status_message.split("\n")[1]
        by_counter = message.find(self.__STATUS_MESSAGE_PATTERN_BY)
        message = message[by_counter + len(self.__STATUS_MESSAGE_PATTERN_BY):]
        commit_counter = message.find(self.__STATUS_MESSAGE_PATTERN_COMMIT)
        return message[:commit_counter]

    @staticmethod
    def __get_untracked_files_count(git_repo):
        return len(git_repo.untracked_files)

    @staticmethod
    def __get_modified_files_count(git_repo):
        return len(git_repo.index.diff(None))
