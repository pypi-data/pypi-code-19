#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 Tim Santor
#
# This file is part of proprietary software and use of this file
# is strictly prohibited without written consent.
#
# @author  Tim Santor  <tsantor@xstudios.agency>

"""Provides a lazy way to recursively `git status|pull|push` all repos.
Use with caution."""

# -----------------------------------------------------------------------------

import argparse
import fnmatch
import io
import json
import logging
import os
import re
import subprocess
import sys

# 3rd Party
from bashutils import logmsg
import six.moves.configparser as configparser

# -----------------------------------------------------------------------------

repo_list = []


def get_parser():
    """Returns the Argument Parser."""

    parser = argparse.ArgumentParser(
        description="Does bulk status|push|pull operations on git repos."
    )

    # required arguments
    parser.add_argument("--method", "-m", help="method to call",
                        choices=['status', 'push', 'pull'])

    # optional arguments
    parser.add_argument("--add", "-a", help="add a repo")
    parser.add_argument("--remove", "-r", help="removed a repo")
    parser.add_argument("--ignore", "-i", help="ignore a repo", default=False, action="store_true")

    parser.add_argument("--update_origins", help="update all repo origins", action="store_true")
    parser.add_argument("--find", help="find all repos", action="store_true")
    parser.add_argument("--sync", help="sync all repos", action="store_true")

    return parser


def exec_cmd(cmd):
    """Executes a command and returns its output."""
    try:
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                       shell=True)
    except subprocess.CalledProcessError:
        logmsg.error('Command failed: %s' % cmd)


def get_dirs(search):
    """Return the dir paths we're interested in."""
    dirs = []
    for mydir in search:
        mydir = os.path.join(os.path.expanduser(mydir), '')
        dirs.append(mydir)

    return dirs


def find_repos(dirpath, repo_users=[]):
    """Walk directory and find git repo directories."""
    logmsg.header('Searching: %s ...' % dirpath)
    for root, dirnames, filenames in os.walk(dirpath):
        for dirname in fnmatch.filter(dirnames, '.git'):

            dirpath = os.path.join(root, os.path.dirname(dirname))
            repo_info = get_repo_info(dirpath)
            for repo_user in repo_users:
                if repo_user in repo_info['url']:
                    if not repo_exists(dirpath):
                        if logmsg.confirm('Would you like to add "%s"' % dirpath):
                            repo_list.append(get_repo_info(dirpath))
                        else:
                            repo_list.append(get_repo_info(dirpath, True))

    return repo_list


def sync_repos():
    """Clone any repos that are not on this system."""
    for obj in repo_list:
        if 'ignore' in obj and obj['ignore'] is True:
            continue
        if not os.path.exists(obj['path']):
            if logmsg.confirm('"%s" does not exist, create it' % obj['path']):
                os.makedirs(obj['path'])
                output = exec_cmd('git clone %s "%s"' %
                                  (obj['url'], obj['path']))
                print(output.strip())


def write_file(repo_list, filepath):
    """Write repo matches to file."""
    with io.open(filepath, 'w', encoding='utf-8') as f:
        data = json.dumps(repo_list, sort_keys=True, indent=4)
        f.write(unicode(data))


def read_file(filepath):
    """Return git_repos file contents as JSON."""
    logmsg.header('Reading repo_lists.json file...')
    try:
        with open(filepath, 'r') as f:
            jsondata = json.loads(f.read())
    except IOError:
        logmsg.warning('"%s" not found' % filepath)
        jsondata = []

    return jsondata


def repo_exists(dirpath):
    """Return if repo exists or not."""
    for r in repo_list:
        if r['path'] == dirpath:
            return True
    return False


def get_repo_info(dirpath, ignore=False):
    """Get repo URL from given directory."""
    output = exec_cmd(
        "cd \"%s\" && git config --get remote.origin.url" % dirpath)
    if output and output.startswith('https') or output.startswith('ssh') or output.startswith('git'):
        return {'path': dirpath, 'url': output.strip(), 'ignore': ignore}


def add_repo(dirpath, ignore):
    """Add a repo."""
    if not repo_exists(dirpath):
        repo_list.append(get_repo_info(dirpath, ignore))
        logmsg.success('"%s" successfully added' % dirpath)
        return repo_list
    logmsg.warning('"%s" already exists' % dirpath)
    return repo_list


def remove_repo(dirpath):
    """Remove a repo."""
    if repo_exists(dirpath):
        i = 0
        for r in repo_list:
            if r['path'] == dirpath:
                if logmsg.confirm('Are you sure you want to remove "%s"' % dirpath):
                    del repo_list[i]
                    logmsg.success('"%s" successfully removed' % dirpath)
                return repo_list
            i += 1
    logmsg.warning('"%s" does not exist' % dirpath)
    return repo_list


def update_origins():
    """Update all repo origins to SSH."""
    for obj in repo_list:
        url = re.sub(r'https://(.+@)?|ssh://(.+@)?', 'git@', obj['url'])
        url = re.sub(r'org/', 'org:', url)
        url = re.sub(r'com/', 'com:', url)
        if obj['url'] != url:
            print(obj['url'] + ' ==> ' + url)
            obj['url'] = url
            output = exec_cmd('cd \"%s\" && git remote rm origin || true && git remote add origin %s' % (obj['path'], url))
            # print(output.strip())


def run():
    """Run script."""
    global repo_list

    # Ensure proper command line usage
    args = get_parser().parse_args()

    # Read our config file
    config_file = os.path.expanduser("~/config/git-lazy.cfg")
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
    else:
        logmsg.warning('"%s" does not exist' % config_file)
        exit()

    repo_file = os.path.expanduser(config.get('default', 'repo_list'))
    search_dirs = config.get('default', 'search_dirs').split(',')
    repo_users = config.get('default', 'repo_users').split(',')

    repo_list = read_file(repo_file)

    if args.update_origins:
        update_origins()
        write_file(repo_list, repo_file)
        exit()

    if args.add:
        repo_list = add_repo(args.add, args.ignore)
        write_file(repo_list, repo_file)
        exit()

    if args.remove:
        repo_list = remove_repo(args.remove)
        write_file(repo_list, repo_file)
        exit()

    # Find repos in preset directories
    if args.find:
        search = get_dirs(search_dirs)

        for dirpath in search:
            find_repos(dirpath, repo_users)

        write_file(repo_list, repo_file)
        logmsg.success('DONE!')
        exit()

    # Sync
    if args.sync:
        sync_repos()
        logmsg.success('DONE!')
        exit()

    # Do our git operation on all found git repos
    ignored = []
    for repo in repo_list:
        if 'ignore' in repo and repo['ignore'] is True:
            # logmsg.warning(repo['path'] + ' is on the ignore list')
            ignored.append(repo['path'])
            continue
        if not os.path.exists(repo['path'] + '.git/'):
            # logmsg.warning(repo['path'] + ' is not a git repo')
            continue

        print('-' * 80)
        logmsg.header(repo['path'])
        os.chdir(repo['path'])

        # Set upstream to current branch
        # branch = exec_cmd("git branch | awk '{ print $2}'")
        # exec_cmd('git branch --set-upstream-to=origin/%s' % branch.strip())

        if args.method == 'push':
            exec_cmd('git add -A')
            exec_cmd('git commit -m "git-lazy auto commit"')
            output = exec_cmd('git push')
        else:
            output = exec_cmd('git ' + args.method)

        logmsg.info(output)

    logmsg.header('Ignored repos...')
    for repo in ignored:
        logmsg.warning(repo)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    run()
