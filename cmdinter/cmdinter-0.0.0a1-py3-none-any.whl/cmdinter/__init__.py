import traceback
import sys
import os
import io
from typing import Optional, Callable, Any, NamedTuple
from contextlib import redirect_stdout


class Status(object):
    ok: str = '[OK] '
    error = '[ERROR] '
    skip = '[SKIP] '


class CmdFuncResult(NamedTuple):
    return_code: int
    return_msg: str
    return_val: str


class CmdResult(NamedTuple):
    return_val: Any
    return_code: int
    return_msg: str
    output: Optional[str]
    error: Optional[str]
    traceback: Optional[str]


def _get_multi_writer(streams: list):
    writer = type('obj', (object,), {})
    writer.write = lambda s: [stream.write(s) for stream in streams]
    return writer


def _silent_call(
    func: Callable,
    *args: Optional[tuple],
    **kwargs: Optional[dict]
    ):
    args: tuple = args if args else ()
    kwargs: dict = kwargs if kwargs else {}

    with redirect_stdout(open(os.devnull, 'w')):
        return_val = func(*args, **kwargs)

    return return_val


def _catch_func_output(
    func: Callable,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
    silent: bool = False,
    ) -> tuple:
    """"""
    args: tuple = args if args else ()
    kwargs: dict = kwargs if kwargs else {}
    streams: list = []

    streams.append(io.StringIO())

    if not silent:
        streams.append(sys.stdout)

    with redirect_stdout(_get_multi_writer(streams)):
        func_return_val: Any = func(*args, **kwargs)

    output: Optional[str] = streams[0].getvalue()

    return func_return_val, output


def handle_cmd_function(
    silent: bool,
    return_stdout: bool,
    catch_err: bool,
    func: Callable,
    args: Optional[tuple],
    kwargs: Optional[dict],
    ) -> CmdResult:
    """"""
    args = args if args else ()
    kwargs = kwargs if kwargs else {}
    func_result = None
    output = None
    error = None
    trace = None

    try:
        if return_stdout:
            result_with_output: tuple = _catch_func_output(func, args, kwargs, silent=silent)
            func_result: CmdFuncResult = result_with_output[0]
            output: str = result_with_output[1]
        else:
            if silent:
                func_result: CmdFuncResult = _silent_call(func, *args, **kwargs)
            else:
                func_result = func(*args, **kwargs)
            output = None

        if type(func_result) != CmdFuncResult:
            raise TypeError('Command function not returning type: CmdFuncResult.')

    except Exception as e:
        trace: str = traceback.format_exc()

        not silent and print(trace)

        if catch_err:
            error = e
        else:
            raise e

    return CmdResult(
        return_val=func_result and getattr(func_result, 'return_val'),
        return_msg=func_result and getattr(func_result, 'return_msg'),
        return_code=func_result and getattr(func_result, 'return_code'),
        output=output,
        error=error,
        traceback=trace
        )


def run_cmd(
    silent: bool = False,
    return_stdout: bool = False,
    catch_err: bool = False,
    ) -> Callable:
    """"""
    return lambda func, *args, **kwargs: \
        handle_cmd_function(silent, return_stdout, catch_err, func, args, kwargs)
