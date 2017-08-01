import abc
import pathlib
import sys
import types
import typing as t


ReturnValue = t.TypeVar('ReturnValue')
MainFunction = t.Callable[[], ReturnValue]
ExceptionInfo = t.Tuple[t.Type[BaseException], BaseException, types.TracebackType]


class Script(t.NamedTuple):
    file: pathlib.Path
    function: MainFunction


class Executor:

    delegate: t.Optional['Delegate']

    def __init__(self, *, delegate: t.Optional['Delegate'] = None) -> None:
        self.delegate = delegate

    def execute(self, script: Script) -> None:
        if self.delegate:
            self.delegate.handle_entry(self, script)

        try:
            value = script.function()
        except Exception:
            exception_info = sys.exc_info()

            if self.delegate:
                self.delegate.handle_exception(self, script, exception_info)
        else:
            if self.delegate:
                self.delegate.handle_success(self, script, value)

        if self.delegate:
            self.delegate.handle_exit(self, script)


class Delegate(abc.ABC):

    @abc.abstractmethod
    def handle_entry(self, executor: Executor, script: Script) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def handle_success(self, executor: Executor, script: Script, value: ReturnValue) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def handle_exception(self, executor: Executor, script: Script, exception_info: ExceptionInfo) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def handle_exit(self, executor: Executor, script: Script) -> None:
        raise NotImplementedError
