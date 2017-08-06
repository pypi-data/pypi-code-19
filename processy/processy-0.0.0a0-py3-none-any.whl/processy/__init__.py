import sys
import subprocess as sp


def _print_and_return_lines_from_popen(p: sp.Popen) -> str:
    out: str = ''
    for c in iter(lambda: p.stdout.readline(1), ''):
        sys.stdout.write(c)
        out += c
    return out


def _return_lines_from_popen(p: sp.Popen) -> str:
    out: str = ''
    for c in iter(lambda: p.stdout.readline(1), ''):
        out += c
    return out


def _print_lines_from_popen(p: sp.Popen) -> None:
    for c in iter(lambda: p.stdout.readline(1), ''):
        sys.stdout.write(c)


class PopenResult(object):
    def __init__(
        self,
        return_code: int = None,
        out: str = None,
        error: str = None,
        ):
        """"""
        self.return_code: int = return_code
        self.out: str = out
        self.error: str = error


def run(
    cmd: list,
    return_stdout: bool = False,
    verbose: bool = True,
    raise_err: bool = False,
    **popen_kwargs
    ) -> PopenResult:
    """"""
    out = None
    error = None

    default_kwargs = {
        'universal_newlines': True
        }

    if return_stdout:
        default_kwargs.update({'stdout': sp.PIPE})
    elif not return_stdout and not verbose:
        default_kwargs.update({'stdout': sp.DEVNULL})

    p: sp.Popen = sp.Popen(cmd, **default_kwargs, **popen_kwargs)

    if return_stdout and verbose:
        out = _print_and_return_lines_from_popen(p)
        error = p.communicate()[1]
    elif return_stdout and not verbose:
        out, error = p.communicate()
    elif not return_stdout and verbose:
        error = p.communicate()[1]
    elif not return_stdout and not verbose:
        error = p.communicate()[1]

    return_code: int = p.wait()

    if raise_err and return_code:
        raise sp.CalledProcessError(return_code, cmd)

    return PopenResult(
        return_code=return_code,
        out=out,
        error=str(error)
        )
