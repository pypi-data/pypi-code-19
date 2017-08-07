from buildlib.semver.prompt import prompt_semver_num_by_choice
from buildlib.cmds.sequences import git as prompt_seq_git
from typing import NamedTuple, Optional
import prmt


class Answers(NamedTuple):
    should_update_version_num: bool
    version: Optional[str]
    should_run_build_py: bool
    should_run_git_commands: bool
    should_run_git_add_all: bool
    should_run_git_commit: bool
    commit_msg: Optional[str]
    should_run_git_tag: bool
    should_run_git_push: bool
    branch: Optional[str]
    should_push_registry: bool
    should_push_gemfury: bool
    gemfury_env: Optional[str]


def get_answers(
    ask_registry=False,
    ask_build=False,
    cur_version=None,
    gemfury_env=None
    ) -> Answers:
    """"""

    question: str = 'Do you want to update the VERSION NUMBER before publishing? [y|n]'
    should_update_version_num = prmt.confirm(question, default='y')

    version = prompt_semver_num_by_choice(cur_version) if should_update_version_num else None

    question: str = 'Do you want to run "build.py" before publishing?'
    should_run_build_py = prmt.confirm(question, default='y') if ask_build else None

    question: str = 'Do you want to run ANY GIT COMMANDS before publishing?'
    should_run_git_commands = prmt.confirm(question, default='y')

    git_args = prompt_seq_git.get_answers() if should_run_git_commands else None

    question: str = 'Do you want to PUSH to a package REGISTRY?'
    should_push_registry = prmt.confirm(question, default='y') if ask_registry else None

    question: str = 'Do you want to push the new version to GEMFURY?'
    should_push_gemfury = prmt.confirm(question, default='y') if should_push_registry else None

    return Answers(
        should_update_version_num=should_update_version_num,
        version=version or cur_version,
        should_run_build_py=should_run_build_py,
        should_run_git_commands=should_run_git_commands,
        should_run_git_add_all=git_args and getattr(git_args, 'should_run_git_add_all'),
        should_run_git_commit=git_args and getattr(git_args, 'should_run_git_commit'),
        commit_msg=git_args and getattr(git_args, 'commit_msg'),
        should_run_git_tag=git_args and getattr(git_args, 'should_run_git_tag'),
        should_run_git_push=git_args and getattr(git_args, 'should_run_git_push'),
        branch=git_args and getattr(git_args, 'branch'),
        should_push_registry=should_push_registry,
        should_push_gemfury=should_push_gemfury,
        gemfury_env=gemfury_env
        )
