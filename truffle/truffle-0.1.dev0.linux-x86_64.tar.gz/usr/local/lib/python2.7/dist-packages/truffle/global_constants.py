"""Description: List of constants maintained for python backend."""


SUPPORTED_LANGS = ('.py')

SUPPORTED_LANGS_REGEX = (".py$")

TRUFFLE_DOCSTRING_REGEX = ("Description:((\n)|.)*Args:((\n)|.)*Returns:((\n)|.)*Raises:((\n)|.)*")

INCLUDE_LIST = [".py$", ".md$", ".txt$", ".js$", ".html$", ".htm$", ".css$"]

EXCLUDE_LIST = [".git*", ".DS_Store", ".pyc$", "__pycache__", ".ico"]

COUNT_ID = 0
