import os

try:
    from subprocess import run
except ImportError:
    from subprocess35 import run

from subprocess import PIPE

from typing import Any, Optional


def run_subprocess(command) -> Any:  # mypy is not happy with p.stdout being
    p = run(command,      # of type `bytes`
            stdout=PIPE)
    return p


def get_socket_path(path: Optional[str]=None) -> str:
    if path is not None:
        return path

    try:
        return os.environ['I3SOCK']
    except KeyError:
        p = run_subprocess(['i3', '--get-socketpath'])
        return p.stdout.decode('utf8').strip()
