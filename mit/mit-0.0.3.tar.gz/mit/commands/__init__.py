import os
from abc import ABCMeta, abstractmethod


class Command(object):

    __metaclass__ = ABCMeta

    __GIT_FOLDER_NAME = ".git"

    def run(self, print_msgs=True):
        for repo_name, repo_folder in self._get_git_folders().items():
            self._run_for_each_repo(repo_name, repo_folder, print_msgs=print_msgs)

    @abstractmethod
    def _run_for_each_repo(self, repo_name, repo_folder, print_msgs):
        raise NotImplementedError("You MUST implement this method!")

    @classmethod
    def _get_git_folders(cls):
        current_folder = os.getcwd()
        repo_folders = {}

        if os.path.exists(os.path.join(current_folder, cls.__GIT_FOLDER_NAME)):
            repo_name = os.path.split(current_folder)[1]
            repo_folders[repo_name] = current_folder
        else:
            for repo_name in os.listdir(current_folder):
                repo_folder = os.path.join(current_folder, repo_name)
                package_git_folder = os.path.join(repo_folder, cls.__GIT_FOLDER_NAME)
                if os.path.exists(package_git_folder):
                    repo_folders[repo_name] = repo_folder
        return repo_folders
