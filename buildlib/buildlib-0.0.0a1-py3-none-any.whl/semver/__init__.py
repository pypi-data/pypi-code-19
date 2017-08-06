import re
import os
from typing import Union, Optional
from buildlib.wheel import extract_version_from_wheel_name


def validate(version: str) -> bool:
    """
    Check if version number has 'semver' format (num.num.num or num.num.num-str.num)
    """
    pattern = re.compile('(^\d+\.\d+\.\d+$|^\d+\.\d+\.\d+[-]\D+[.]\d+$)')

    if not pattern.match(version):
        return False
    else:
        return True


def extract_pre_release_suffix(version: str) -> str:
    """
    Get the non-numeric part of the semver num. E.g. '1.0.4-alpha.4' returns '-alpha'
    """
    return re.sub(r'[0-9.\s]', '', version)


def increase(
    version: str,
    command: str
    ) -> str:
    """
    Increase version num based on @command:
        major: Increase num before first dot.
        minor: Increase num before second dot.
        patch: Increase num after second dot.
        pre: Increase pre num after third dot. (only when 4 dots exist in version num.)
    @version: must be of semver type. E.g.: '1.0.4' or '1.0.4-a.2' or '1.0.4-beta.1' etc.
    """
    extract_numbers = lambda version: re.findall(r'\d+', version)

    vnum: list = extract_numbers(version)
    has_suffix: bool = True if len(vnum) > 3 else False
    suffix_str: str = '-alpha.' if not has_suffix else extract_pre_release_suffix(version)
    suffix_num: str = '.0' if not has_suffix else '.' + str(int(vnum[3]) + 1)
    suffix_new: str = '' if not has_suffix else suffix_str + '.0'

    if command == 'major':
        return '.'.join([str(int(vnum[0]) + 1), '0', '0' + suffix_new])
    if command == 'minor':
        return '.'.join([vnum[0], str(int(vnum[1]) + 1), '0' + suffix_new])
    if command == 'patch':
        return '.'.join([vnum[0], vnum[1], str(int(vnum[2]) + 1) + suffix_new])
    if command == 'pre':
        return '.'.join([vnum[0], vnum[1], vnum[2] + suffix_str + suffix_num])


def convert_semver_to_wheelver(version: str) -> str:
    """
    Convert a semver num like this one: 1.12.1-alpha.10
    to a python wheel-version num like this one: 1.12.1a10
    """
    suffix: str = extract_pre_release_suffix(version)
    return version if not len(suffix) > 2 else version.replace(suffix + '.', suffix[1])


def get_python_wheel_name_from_semver_num(
    requested_version: str,
    wheel_dir: str
    ) -> Union[None, str]:
    """
    Search dir for a wheel-file which contains a specific version number in its name.
    Return found wheel name or False.
    """
    version_to_find: str = convert_semver_to_wheelver(requested_version)
    files: list = [f for f in os.listdir(wheel_dir)]
    matches: list = [f for f in files if extract_version_from_wheel_name(f) == version_to_find]

    if matches:
        return matches[0]
    else:
        print('Error: Could not find wheel: ' + version_to_find)
        return None
