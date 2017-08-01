import __main__
import inspect
import pathlib

from scripting import delegates, execution


class MainDecorator:

    executor: execution.Executor

    def __init__(self) -> None:
        self.executor = execution.Executor(delegate=delegates.ScriptController())

    def __call__(self, function: execution.MainFunction) -> execution.MainFunction:
        if inspect.getmodule(function) == __main__:
            script = self._script(function)
            self.executor.execute(script)

        return function

    @staticmethod
    def _script(function: execution.MainFunction) -> execution.Script:
        file_path = pathlib.Path(inspect.getfile(function))
        return execution.Script(file_path, function)


main: MainDecorator = MainDecorator()
