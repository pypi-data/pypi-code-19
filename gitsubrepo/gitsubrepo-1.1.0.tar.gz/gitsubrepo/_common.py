import subprocess
from typing import List, Dict

from gitsubrepo.exceptions import RunException

_DATA_ENCODING = "utf-8"
_SUCCESS_RETURN_CODE = 0


def run(arguments: List[str], execution_directory: str=None, execution_environment: Dict=None) -> str:
    """
    Runs the given arguments from the given directory (if given, else resorts to the (undefined) current directory).
    :param arguments: the CLI arguments to run
    :param execution_directory: the directory to execute the arguments in
    :param execution_environment: the environment to execute in
    :return: what is written to stdout following execution
    :exception RunException: called if the execution has a non-zero return code
    """
    process = subprocess.Popen(
        arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, cwd=execution_directory,
        env=execution_environment)
    out, error = process.communicate()
    stdout = out.decode(_DATA_ENCODING).rstrip()
    if process.returncode == _SUCCESS_RETURN_CODE:
        return stdout
    else:
        raise RunException(stdout, error.decode(_DATA_ENCODING).rstrip(), arguments, execution_directory)
