"""Parse arguments and call the appropiate commands."""


import sys
import os
from os.path import join

from utils import TODO_STRING, FILE_EXTENSION, GIT_LINK
from utils import MD_TODO, MD_LINK, MD_TITLE


ALL_TODOS = []
IGNORE = ['venv', 'build', 'dist', '.git']


def main():
    """Parse arguments."""
    # Check to make sure the current project is a git repo
    if '.git' not in os.listdir(os.getcwd()):
        raise Exception('Please run `todo` in a Git project only.')
        sys.exit()

    # Get all todo lines
    _list_dir(os.path.relpath(os.getcwd()))

    # Start generating the markdown
    _generate_markdown()


def _get_gitignore():
    regex = []
    with open('.gitignore', 'r') as fp:
        for line in fp.readlines():
            line = line.strip()
            if not line.startswith('#'):
                regex.append(_gitignore_to_regex(line))


def _gitignore_to_regex(string):
    return string.replace('*', '')


def _get_git_config():
    # Read the git config file for user and repo name
    with open(join('.git', 'config'), 'r') as fp:
        for line in fp.readlines():
            line = line.strip()
            if line.startswith('url'):
                line = line.split('=')[1]
                line = line.split(':')[1]
                user, repo = line.split('/')
                repo = repo[:-4]

                return user, repo


def _list_dir(path):
    for child in os.listdir(path):
        if child in IGNORE:
            continue
        full_child = join(path, child)
        if os.path.isdir(full_child):
            _list_dir(full_child)
        elif child.endswith(FILE_EXTENSION):
            _extract_todo(full_child)


def _extract_todo(file_path):
    # Read source file
    with open(file_path, 'r') as fp:
        # Read each line
        for index, line in enumerate(fp.readlines()):
            # Check for todo tag
            line = line.strip()
            if line.startswith(TODO_STRING):
                # Try to split it
                try:
                    _, todo = line.split(":")
                except:
                    todo = line
                ALL_TODOS.append((index, todo, file_path))


def _generate_markdown():
    with open(join(os.getcwd(), 'TODO.md'), 'w') as fp:
        user, repo = _get_git_config()
        # Write the title
        fp.write(MD_TITLE.format(repo))

        for todo in ALL_TODOS:
            index, text, fpath = todo
            fname = fpath.split('/')[-1]
            user, repo = _get_git_config()

            url = GIT_LINK.format(user, repo, fpath, index + 1)
            fp.write(MD_TODO.format(text, MD_LINK.format(fname, url)))


if __name__ == "__main__":
    main()
