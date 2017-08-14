"""Parse arguments and call the appropiate commands."""
# TODO: Title for file (and subsections)
# TODO: Hash check for existing TODOs


import sys
import os
from os.path import join

from utils import TODO_STRING, FILE_EXTENSION, MD_TODO, GIT_LINK, MD_LINK


# TODO: Make this an array of arrays
ALL_TODOS = []
# TODO: Make regex ignore list from .gitignore
IGNORE = ['venv', 'build', 'dist']


def main():
    """Parse arguments."""
    # Check to make sure the current project is a git repo
    if '.git' not in os.listdir(os.getcwd()):
        raise Exception('Please run `todo` in a Git project only.')
        sys.exit()

    # Get all todo lines
    _list_dir(os.path.relpath(os.getcwd()))

    # Start generating the markdown
    _generate_markdown(ALL_TODOS)


def _get_git_config():
    # Read the git config file for user and repo name
    # TODO: Make this use git-config and get the active branch aswell
    with open(join('.git', 'config'), 'r') as fp:
        for line in fp.readlines():
            line = line.strip()
            if line.startswith('url'):
                line = line.split('=')[1]
                line = line.split(':')[1]
                user, repo = line.split('/')
                repo = repo[:-4]

                return user, repo


def _generate_markdown(todos):
    # TODO: Generate subsections for each file
    with open(join(os.getcwd(), 'TODO.md'), 'w') as fp:
        for todo in todos:
            index, text, fpath = todo
            fname = fpath.split('/')[-1]
            user, repo = _get_git_config()

            url = GIT_LINK.format(user, repo, fpath, index + 1)
            fp.write(MD_TODO.format(text, MD_LINK.format(fname, url)))


def _list_dir(path):
    for child in os.listdir(path):
        if child in IGNORE:
            continue
        full_child = join(path, child)
        if os.path.isdir(full_child):
            _list_dir(full_child)
        elif child.endswith(FILE_EXTENSION):
            _check_todo(full_child)


def _check_todo(file_path):
    with open(file_path, 'r') as fp:
        for index, line in enumerate(fp.readlines()):
            if line.strip().startswith(TODO_STRING):
                try:
                    _, todo = line.split(":")
                    # DEBUG
                    # print("%04d %s" % (index, todo)),
                    ALL_TODOS.append((index, todo.strip(), file_path))
                except:
                    pass


if __name__ == "__main__":
    main()
