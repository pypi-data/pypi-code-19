# encoding=utf8
from __future__ import print_function
from datetime import datetime
from ghlint import config
from github import Github
from github.GithubException import UnknownObjectException
from termcolor import colored, cprint


ERROR_COUNT = 0
WARN_COUNT = 0


def run(settings):
    github = Github(settings["username"], settings["password"])

    account_type = settings["account-type"]
    organization = settings["organization"]
    repo_type = settings["repo-type"]

    if account_type == "organization":
        repos = github.get_organization(organization).get_repos(repo_type)
    else:
        repos = github.get_user().get_repos(repo_type)

    for repo in repos:
        if repo.fork is False:
            lint(repo)

def lint(repo):
    global ERROR_COUNT, WARN_COUNT # pylint: disable=global-statement

    branches = repo.get_branches()
    for branch in branches:
        if branch.name == repo.default_branch:
            ERROR_COUNT = 0
            WARN_COUNT = 0

            try:
                file_ = repo.get_file_contents("/.ghlintrc")
                ghlintrc = config.merged(file_.decoded_content)
            except UnknownObjectException:
                ghlintrc = config.default()

            print_repo(repo)

            rule_gitignore(repo, ghlintrc, "gitignore")
            rule_contributing(repo, ghlintrc, "contributing")
            rule_editorconfig(repo, ghlintrc, "editorconfig")
            rule_ghlintrc(repo, ghlintrc, "ghlintrc")
            rule_protection(repo, ghlintrc, "protection")
            rule_old_pull(repo, ghlintrc, "old-pull")
            rule_loose_branch(repo, ghlintrc, "loose-branch")

            print("")

    print_summary()

def get_file_found(repo, file_name):
    root = "/"

    for file_root in repo.get_dir_contents(root):
        if file_root.path == file_name:
            return True

    return False

def get_rule_value(repo, ghlintrc, rule):
    value = ghlintrc.get("ALL", rule)

    if repo.private:
        if ghlintrc.has_option("PRIVATE", rule):
            value = ghlintrc.get("PRIVATE", rule)

    return value

def print_repo(repo):
    repo_type = "private" if repo.private else "public"
    print("{}{}  {}".format(
        colored("https://github.com/", "white", attrs=["underline", "bold"]),
        colored(repo.full_name, "white", attrs=["underline", "bold"]),
        colored(repo_type, "white", attrs=["dark"])
    ))

def print_message(rule, severity, message):
    global ERROR_COUNT, WARN_COUNT # pylint: disable=global-statement

    if severity == "error":
        ERROR_COUNT += 1
        severity_color = "red"
    elif severity == "warn":
        WARN_COUNT += 1
        severity_color = "yellow"
    else: # severity == "info"
        severity_color = "white"

    print("  {}  {}  {}".format(
        colored(severity, severity_color),
        colored(message, "white"),
        colored(rule, "white", attrs=["dark"])
    ))

def print_summary():
    problem_count = ERROR_COUNT + WARN_COUNT
    if problem_count > 0:
        summary_color = "red" if ERROR_COUNT > 0 else "yellow"

        problem_word = "problem" if problem_count == 1 else "problems"
        error_word = "error" if ERROR_COUNT == 1 else "errors"
        warn_word = "warning" if WARN_COUNT == 1 else "warnings"

        cprint("✖ {problem_count} {problem_word} ({error_count} {error_word}, {warn_count} {warn_word})\n".format(
            problem_count=problem_count,
            problem_word=problem_word,
            error_count=ERROR_COUNT,
            error_word=error_word,
            warn_count=WARN_COUNT,
            warn_word=warn_word), summary_color)
    else:
        cprint("✓ 0 problems\n", "green")

def rule_gitignore(repo, ghlintrc, rule):
    severity = get_rule_value(repo, ghlintrc, rule)
    if severity == "off":
        return

    message = "File .gitignore not found"
    if not get_file_found(repo, ".gitignore"):
        print_message(rule, severity, message)

def rule_contributing(repo, ghlintrc, rule):
    severity = get_rule_value(repo, ghlintrc, rule)
    if severity == "off":
        return

    message = "File CONTRIBUTING not found"
    if not get_file_found(repo, "CONTRIBUTING"):
        print_message(rule, severity, message)

def rule_editorconfig(repo, ghlintrc, rule):
    severity = get_rule_value(repo, ghlintrc, rule)
    if severity == "off":
        return

    message = "File .editorconfig not found"
    if not get_file_found(repo, ".editorconfig"):
        print_message(rule, severity, message)

def rule_ghlintrc(repo, ghlintrc, rule):
    severity = get_rule_value(repo, ghlintrc, rule)
    if severity == "off":
        return

    message = "File .ghlintrc not found"
    if not get_file_found(repo, ".ghlintrc"):
        print_message(rule, severity, message)

def rule_protection(repo, ghlintrc, rule):
    severity = get_rule_value(repo, ghlintrc, rule)
    if severity == "off":
        return

    branch = repo.get_protected_branch(repo.default_branch)
    message = "Branch '{}' not protected".format(repo.default_branch)
    if not branch.protected:
        print_message(rule, severity, message)

def rule_old_pull(repo, ghlintrc, rule):
    severity = get_rule_value(repo, ghlintrc, rule)
    if severity == "off":
        return

    pulls = repo.get_pulls()
    for pull in pulls:
        pull_age = datetime.now() - pull.created_at
        pull_max_age = int(get_rule_value(repo, ghlintrc, "old-pull-max-age"))
        if pull_age.days >= pull_max_age and pull.state == "open":
            message = "Pull request #{} '{}' is {} days old".format(pull.number, pull.title, pull_age.days)
            print_message(rule, severity, message)

def rule_loose_branch(repo, ghlintrc, rule):
    severity = get_rule_value(repo, ghlintrc, rule)
    if severity == "off":
        return

    branches = repo.get_branches()
    branch_names = []
    for branch in branches:
        branch_names.append(branch.name)

    pulls = repo.get_pulls()
    pull_refs = []
    for pull in pulls:
        pull_refs.append(pull.head.ref)

    loose_branch_names = list(set(branch_names).difference(pull_refs))
    for loose_branch_name in loose_branch_names:
        if loose_branch_name != repo.default_branch:
            message = "Branch '{}' without pull request".format(loose_branch_name)
            print_message(rule, severity, message)
