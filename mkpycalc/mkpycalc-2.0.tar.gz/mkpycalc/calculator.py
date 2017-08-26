import logging

import mklibpy

from . import constant
from . import util

__author__ = 'Michael'

logger = logging.getLogger("calculator")


class ExitCommand(Exception):
    pass


class ResetCommand(Exception):
    pass


class Calculator(object):
    def __init__(self, **kwargs):
        self.constants = kwargs
        self.locals = dict()
        self.last = None
        self.e = None

    def __setattr__(self, key, value):
        if key == "last":
            self.locals["_"] = value
        object.__setattr__(self, key, value)

    def show(self):
        mklibpy.terminal.clear_screen()
        const, builtin = util.split_var_func(self.constants)
        var, func = util.split_var_func(self.locals)

        print("Constants:")
        util.terminal.print_vars(const)
        print("")

        print("Built-in functions:")
        util.terminal.print_func_names(builtin)
        print("")

        print("Variables:")
        util.terminal.print_vars(var)
        print("")

        print("User-defined functions:")
        util.terminal.print_func_names(func)
        print("")

    def err(self):
        util.terminal.print_err("Error: {}".format(self.e))

    def eval_expression(self, line):
        try:
            self.last = eval(line, self.constants, self.locals)
        except:
            return False
        else:
            if "__builtins__" in self.constants:
                self.constants.pop("__builtins__")
            return True

    def exec_statement(self, line):
        # store locals
        old_values = dict(self.locals)

        try:
            exec(line, self.constants, self.locals)
        except Exception as e:
            self.e = e
            return False

        if "__builtins__" in self.constants:
            self.constants.pop("__builtins__")

        # check for new values
        new_keys = [key for key in self.locals if key not in old_values]
        if len(new_keys) == 1:
            self.last = self.locals[new_keys[0]]
            return True
        elif len(new_keys) > 1:
            self.last = None
            return True

        # check if any value changed (in case of += etc.)
        changed_values = [
            self.locals[key]
            for key in self.locals
            if self.locals[key] != old_values[key]
        ]
        if len(changed_values) == 1:
            self.last = changed_values[0]
            return True
        elif len(changed_values) > 1:
            self.last = None
            return True

        # check the first element in line
        for i in range(len(line) - 1):
            if not util.valid_var_name(line[:i + 1]):
                name = line[:i]
                break
        else:
            name = line
        if name in self.locals:
            self.last = self.locals[name]
            return True

        self.last = None
        return True

    def calc(self, line):
        if self.eval_expression("_ {}".format(line)):
            logger.info("Appended expression \'{}\', result {}".format(line, repr(self.last)))
        elif self.eval_expression(line):
            logger.info("Expression \'{}\', result {}".format(line, repr(self.last)))
        elif self.exec_statement(line):
            logger.info("Statement \'{}\', result {}".format(line, repr(self.last)))
        else:
            self.err()
            return False
        if self.last is not None:
            util.terminal.print_result(repr(self.last))
        return True

    def line(self, line):
        if line == "exit":
            raise ExitCommand
        elif line == "reset":
            raise ResetCommand
        elif line == "clear":
            mklibpy.terminal.clear_screen()
            print("")
        elif line == "show":
            self.show()
        elif ">>" in line:
            expr, var_name = line.rsplit(">>", 1)
            var_name = var_name.strip()
            if not self.calc(expr) or self.last is None:
                util.terminal.print_err("Cannot assign value: not an expression")
            else:
                if not util.valid_var_name(var_name):
                    util.terminal.print_err(
                        "Cannot assign: \'{}\' is not a valid name".format(var_name))
                else:
                    self.locals[var_name] = self.last
                    logger.info("Value assigned to \'{}\'".format(var_name))
        else:
            self.calc(line)


def new_calculator(interactive=True):
    logger.info("--- Starting ---")
    if interactive:
        mklibpy.terminal.clear_screen()
        print(constant.INTRO_STR)
    return Calculator(**constant.MATH_VARS)
