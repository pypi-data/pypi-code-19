from github import Github
from . import lint


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
            lint.lint(repo)
