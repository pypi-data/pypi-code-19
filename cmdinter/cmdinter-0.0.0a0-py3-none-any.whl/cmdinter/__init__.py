import traceback
import sys
import io
from contextlib import redirect_stdout
from typing import Optional, Callable, Any


class CmdResult(object):
    def __init__(
        self,
        return_val: Any = None,
        return_code: int = None,
        return_msg: str = None,
        output: str = None,
        error: str = None,
        ):
        """"""
        self.return_val: Any = return_val
        self.return_code: int = return_code
        self.return_msg: str = return_msg
        self.output: str = output
        self.error: str = error


def raise_func_should_not_return_output_error():
    msg = 'A function that is wrapped with the @command decorator should not return "output" ' \
          'via the CmdResult object. Capturing of the function output is handled by @command ' \
          'decorator.'
    raise Exception(msg)


def _get_multi_writer(streams: list):
    writer = type('obj', (object,), {})
    writer.write = lambda s: [stream.write(s) for stream in streams]
    return writer


def _catch_func_output(
    func: Callable,
    args: Optional[tuple],
    kwargs: Optional[dict],
    verbose: bool = True,
    return_stdout: bool = True
    ) -> tuple:
    streams: list = []

    if return_stdout:
        streams.append(io.StringIO())

    if verbose:
        streams.append(sys.stdout)

    with redirect_stdout(_get_multi_writer(streams)):
        func_return_val: Any = func(*args, **kwargs)

    if return_stdout:
        output: Optional[str] = streams[0].getvalue()
    else:
        output = None

    return func_return_val, output


def _get_default_return_msg(
    cmd_title: str,
    return_code: int,
    ):
    messages = {
        0: '[OK] ' + cmd_title,
        1: '[Error] ' + cmd_title,
        }
    return messages[return_code]


def cmd_wrapper(
    cmd_title: Optional[str] = None,
    func: Callable = None,
    args: tuple = None,
    kwargs: dict = None,
    ) -> CmdResult:
    """"""
    kwargs_: dict = kwargs or {}
    verbose: bool = kwargs_.get('verbose')
    return_stdout: bool = kwargs_.get('return_stdout')
    result: CmdResult = CmdResult()

    try:
        data: tuple = _catch_func_output(func, args, kwargs_, verbose, return_stdout)
        raw_func_result: Any = data[0]
        output: Optional[str] = data[1]

        if type(raw_func_result) is CmdResult:
            raw_func_result.output and raise_func_should_not_return_output_error()
            func_result: CmdResult = raw_func_result
        else:
            func_result = CmdResult()
            func_result.return_val: Any = raw_func_result

        result.return_val: Optional[Any] = func_result.return_val or None
        result.return_code: int = func_result.return_code or 0
        result.return_msg: str = func_result.return_msg or _get_default_return_msg(cmd_title, 0)
        result.error: Optional[str] = func_result.error or None
        result.output: Optional[str] = output

    except Exception as e:
        verbose and print(traceback.format_exc())
        result.return_val: Optional[Any] = None
        result.return_code: int = 1
        result.return_msg: str = _get_default_return_msg(cmd_title, 1)
        result.error: Optional[str] = str(e)

    return result


def command(title: str = 'Untitled Command'):
    """
    @command decorator function.
    Wrap a function with this decorator, to apply the "command" interface to it.
    If a function is wrapped with @command the following parameters become available for the
    decorated function:

    @cmd_title: This parameter makes the value that is passed to @command(title=...) available
    inside the function.

    @verbose: This parameter defines if the function call should print to stdout. If it is set to
    False the function will execute 'silently', print(), etc. are ignored.
    The logic for this is handled inside the decorator. You do _NOT_ have to apply any logic inside
    the decorated function to handle it's verbosity.

    @return_stdout: If this is set to True, the decorator will save the output (stdout) of the
    decorated function into a variable and return it with the CmdResult object.
    Waring: This may require a lot of memory. Its default value is set to False.

    @pretty: This parameter can be used to enable/disable output styles. For example:
    `print(h1("Headline")) if pretty else print("Headline")`.
    """

    def inner1(func: Callable):
        def inner2(*args, **kwargs):
            default_kwargs = {
                'cmd_title': title,
                'verbose': True,
                'return_stdout': False,
                'pretty': False,
                }

            return cmd_wrapper(
                cmd_title=title,
                func=func,
                args=args,
                kwargs={**default_kwargs, **kwargs}
                )

        return inner2

    return inner1
