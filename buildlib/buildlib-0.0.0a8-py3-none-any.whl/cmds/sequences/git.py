import prmt
from typing import NamedTuple, Union, List, Optional
from headlines import h3
from cmdinter import CmdFuncResult
from buildlib.utils.yaml import load_yaml
from buildlib.cmds import git
from buildlib.cmds.git.prompt import prompt_commit_msg, prompt_branch
from buildlib.utils.semver.prompt import prompt_semver_num_by_choice, prompt_semver_num_manually
from buildlib.cmds.build import update_version_num_in_cfg_yaml


def _load_cfg(path):
    try:
        return load_yaml(path, keep_order=True)
    except:
        return None


def _get_cur_version(cfg_file):
    cfg = _load_cfg(cfg_file)
    cur_version: str = cfg and cfg.get('version')
    return cur_version


def _get_new_version(cur_version):
    if cur_version:
        return prompt_semver_num_by_choice(cur_version)
    else:
        return prompt_semver_num_manually()


def get_args_interactively(
    run_any: Union[bool, str] = False,
    show_status: Union[bool, str] = False,
    show_diff: Union[bool, str] = False,
    run_update_version: Union[bool, str] = False,
    run_add_all: Union[bool, str] = False,
    run_commit: Union[bool, str] = False,
    run_tag: Union[bool, str] = False,
    run_push: Union[bool, str] = False,
    cfg_file: Optional[str] = None,
    cur_version: Optional[str] = None,
    new_version: Optional[str] = None,
    branch: Optional[str] = None,
    ) -> dict:
    """"""
    kwargs = {}

    if run_any:
        default = run_any if type(run_any) == str else ''
        question: str = 'Run ANY GIT COMMANDS?\n'
        if not prmt.confirm(question, default=default):
            return kwargs

    if show_status:
        print(h3('Git Status'))
        git.status()
        default = show_status if type(show_status) == str else ''
        question: str = 'GIT STATUS ok?\n'
        if not prmt.confirm(question, default=default, margin=(1, 1)):
            return kwargs

    if show_diff:
        print(h3('Git Diff'))
        git.diff()
        default = show_diff if type(show_diff) == str else ''
        question: str = 'GIT DIFF ok?\n'
        if not prmt.confirm(question, default=default, margin=(1, 1)):
            return kwargs

    if run_update_version:
        default = run_update_version if type(run_update_version) == str else ''
        question: str = 'BUMP VERSION number?\n'
        if prmt.confirm(question, default=default):
            new_version = new_version or _get_new_version(cur_version or _get_cur_version(cfg_file))
            kwargs['version'] = new_version
            kwargs['cfg_file'] = cfg_file
            kwargs['run_update_version'] = True

    if run_add_all:
        default = run_add_all if type(run_add_all) == str else ''
        question: str = 'Run GIT ADD ALL ("git add --all")?\n'
        if prmt.confirm(question, default=default):
            kwargs['run_add_all'] = True

    if run_commit:
        default = run_commit if type(run_commit) == str else ''
        question: str = 'Run GIT COMMIT?\n'
        if prmt.confirm(question, default=default):
            commit_msg = prompt_commit_msg()
            kwargs['commit_msg'] = commit_msg
            kwargs['run_commit'] = True

    if run_tag:
        default = run_tag if type(run_tag) == str else ''
        question: str = 'Run GIT TAG?\n'
        if prmt.confirm(question, default=default):
            new_version = new_version or _get_new_version(cur_version or _get_cur_version(cfg_file))
            branch = branch or prompt_branch()
            kwargs['version'] = new_version
            kwargs['branch'] = branch
            kwargs['run_tag'] = True

    if run_push:
        default = run_push if type(run_push) == str else ''
        question: str = 'GIT PUSH to GITHUB?\n'
        if prmt.confirm(question, default=default):
            branch = branch or prompt_branch()
            kwargs['branch'] = branch
            kwargs['run_push'] = True

    return kwargs


def run_seq(
    run_update_version: bool = False,
    run_add_all: bool = False,
    run_commit: bool = False,
    run_tag: bool = False,
    run_push: bool = False,
    cfg_file: Optional[str] = None,
    version: Optional[str] = None,
    commit_msg: Optional[str] = None,
    branch: Optional[str] = None,
    ) -> List[CmdFuncResult]:
    """"""
    results = []

    if run_update_version:
        results.append(update_version_num_in_cfg_yaml(cfg_file, version))

    if run_add_all:
        results.append(git.add_all())

    if run_commit:
        results.append(git.commit(commit_msg))

    if run_tag:
        results.append(git.tag(version, branch))

    if run_push:
        results.append(git.push(branch))

    return results


def run_seq_interactively(
    run_any: Union[bool, str] = False,
    show_status: Union[bool, str] = False,
    show_diff: Union[bool, str] = False,
    run_update_version: Union[bool, str] = False,
    run_add_all: Union[bool, str] = False,
    run_commit: Union[bool, str] = False,
    run_tag: Union[bool, str] = False,
    run_push: Union[bool, str] = False,
    cfg_file: Optional[str] = None,
    cur_version: Optional[str] = None,
    new_version: Optional[str] = None,
    branch: Optional[str] = None,
    ) -> List[CmdFuncResult]:
    """"""

    kwargs = get_args_interactively(**locals())
    results = run_seq(**kwargs)
    return results
