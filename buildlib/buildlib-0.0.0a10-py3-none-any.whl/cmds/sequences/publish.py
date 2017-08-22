import prmt
from cmdinter import CmdFuncResult
from typing import NamedTuple, Union, List, Optional
from buildlib.utils.yaml import load_yaml
from buildlib.utils.semver.prompt import prompt_semver_num_by_choice, prompt_semver_num_manually
from buildlib.cmds import build
from buildlib.utils.semver import convert_semver_to_wheelver, get_python_wheel_name_from_semver_num


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
    run_update_version: Union[bool, str] = False,
    run_build_file: Union[bool, str] = False,
    run_push_gemfury: Union[bool, str] = False,
    run_push_pypi: Union[bool, str] = False,
    cfg_file: Optional[str] = None,
    build_file: Optional[str] = None,
    wheel_dir: Optional[str] = None,
    cur_version: Optional[str] = None,
    new_version: Optional[str] = None,
    ) -> dict:
    """"""
    kwargs = {}

    if run_update_version:
        default = run_update_version if type(run_update_version) == str else ''
        question: str = 'Do you want to update the VERSION NUMBER before publishing?\n'
        if prmt.confirm(question, default=default):
            new_version = new_version or _get_new_version(cur_version or _get_cur_version(cfg_file))
            kwargs['version'] = new_version
            kwargs['cfg_file'] = cfg_file
            kwargs['run_update_version'] = True

    if run_build_file:
        default = run_build_file if type(run_build_file) == str else ''
        question: str = 'Do you want to RUN BUILD FILE before publishing?\n'
        if prmt.confirm(question, default=default):
            kwargs['build_file'] = build_file
            kwargs['run_build_file'] = True

    if run_push_gemfury:
        default = run_push_gemfury if type(run_push_gemfury) == str else ''
        question: str = 'Do you want to PUSH the new version to GEMFURY?\n'
        if prmt.confirm(question, default=default):
            new_version = new_version or _get_new_version(cur_version or _get_cur_version(cfg_file))
            kwargs['version'] = new_version
            kwargs['wheel_dir'] = wheel_dir
            kwargs['run_push_gemfury'] = True

    if run_push_pypi:
        default = run_push_pypi if type(run_push_pypi) == str else ''
        question: str = 'Do you want to PUSH the new version to PYPI?\n'
        if prmt.confirm(question, default=default):
            new_version = new_version or _get_new_version(cur_version or _get_cur_version(cfg_file))
            kwargs['version'] = new_version
            kwargs['wheel_dir'] = wheel_dir
            kwargs['run_push_pypi'] = True

    return kwargs


def run_seq(
    run_update_version: bool = False,
    run_build_file: bool = False,
    run_push_gemfury: bool = False,
    run_push_pypi: bool = False,
    cfg_file: Optional[str] = None,
    build_file: Optional[str] = None,
    wheel_dir: Optional[str] = None,
    version: Optional[str] = None,
    ) -> List[CmdFuncResult]:
    """"""
    results = []

    if run_update_version:
        results.append(build.update_version_num_in_cfg_yaml(cfg_file, version))

    if run_build_file:
        results.append(build.run_build_file(build_file))

    if run_push_gemfury:
        wheel_version = convert_semver_to_wheelver(version)
        wheel_name = get_python_wheel_name_from_semver_num(wheel_version, wheel_dir)
        if not wheel_name:
            print('There is no build for requested version.')
            return results
        wheel_file = wheel_dir + '/' + wheel_name
        results.append(build.push_python_wheel_to_gemfury(wheel_file))

    if run_push_pypi:
        results.append(build.push_python_wheel_to_pypi())

    return results


def run_seq_interactively(
    run_update_version: Union[bool, str] = False,
    run_build_file: Union[bool, str] = False,
    run_push_gemfury: Union[bool, str] = False,
    run_push_pypi: Union[bool, str] = False,
    cfg_file: Optional[str] = None,
    build_file: Optional[str] = None,
    wheel_dir: Optional[str] = None,
    cur_version: Optional[str] = None,
    new_version: Optional[str] = None,
    ) -> List[CmdFuncResult]:
    """"""
    kwargs = get_args_interactively(**locals())
    results = run_seq(**kwargs)
    return results
