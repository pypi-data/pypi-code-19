import logging
import sys
import typing as t

import scripting._terminal

from scripting import execution


class Logger(execution.Delegate):

    def __init__(self, stream: t.TextIO = sys.stdout) -> None:
        self._configure_logging(stream=stream)

    @staticmethod
    def _configure_logging(**kwargs: t.Any) -> None:
        kwargs.setdefault('format', '{message}')
        kwargs.setdefault('level', logging.INFO)
        kwargs.setdefault('style', '{')
        logging.basicConfig(**kwargs)

    @staticmethod
    def _script_repr(script: execution.Script) -> str:
        function_name = script.function.__name__
        file_name = script.file.name
        return f'{function_name}@{file_name}'

    def handle_entry(self, executor: execution.Executor, script: execution.Script) -> None:
        script_repr = self._script_repr(script)
        logging.info(f'Executing {script_repr}...')

    def handle_success(self, executor: execution.Executor, script: execution.Script, value: execution.ReturnValue) -> None:
        logging.info(f'Result: {value}')

    def handle_exception(self, executor: execution.Executor, script: execution.Script, exception_info: execution.ExceptionInfo) -> None:
        script_repr = self._script_repr(script)
        logging.exception(f'An exception occurred while excuting {script_repr}.')

    def handle_exit(self, executor: execution.Executor, script: execution.Script) -> None:
        pass


class TerminalController(execution.Delegate):

    _terminal: scripting._terminal.Terminal

    REENTY_CHARACTER: str = 'r'
    _EXIT_PROMPT: str = f'Press {REENTY_CHARACTER.upper()} to repeat, any key to exit.'

    def __init__(self, input_stream=sys.stdin, output_stream=sys.stdout, error_stream=sys.stderr) -> None:
        self._terminal = scripting._terminal.Terminal(input_stream, output_stream, error_stream)

    def _offer_reentry(self) -> bool:
        character = self._terminal.get_character(self._EXIT_PROMPT)
        return self.REENTY_CHARACTER == character

    def handle_entry(self, executor: execution.Executor, script: execution.Script) -> None:
        self._terminal.clear()

    def handle_success(self, executor: execution.Executor, script: execution.Script, value: execution.ReturnValue) -> None:
        pass

    def handle_exception(self, executor: execution.Executor, script: execution.Script, exception_info: execution.ExceptionInfo) -> None:
        pass

    def handle_exit(self, executor: execution.Executor, script: execution.Script) -> None:
        if self._offer_reentry():
            executor.execute(script)
        else:
            self._terminal.clear()


class ScriptController(execution.Delegate):

    logger: Logger
    terminal_controller: TerminalController

    def __init__(self) -> None:
        self.logger = Logger()
        self.terminal_controller = TerminalController()

    def handle_entry(self, executor: execution.Executor, script: execution.Script) -> None:
        self.terminal_controller.handle_entry(executor, script)
        self.logger.handle_entry(executor, script)

    def handle_success(self, executor: execution.Executor, script: execution.Script, value: execution.ReturnValue) -> None:
        self.logger.handle_success(executor, script, value)
        self.terminal_controller.handle_success(executor, script, value)

    def handle_exception(self, executor: execution.Executor, script: execution.Script, exception_info: execution.ExceptionInfo) -> None:
        self.logger.handle_exception(executor, script, exception_info)
        self.terminal_controller.handle_exception(executor, script, exception_info)

    def handle_exit(self, executor: execution.Executor, script: execution.Script) -> None:
        self.logger.handle_exit(executor, script)
        self.terminal_controller.handle_exit(executor, script)
