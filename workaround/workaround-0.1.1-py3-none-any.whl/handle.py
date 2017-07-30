import random
from pathlib import Path
from typing import (
    Iterable,
    Tuple,
)

import regex

from workaround.handlers.base import BaseHandler

from . import Workaround
from .handlers import (
    get_all_adjectives,
    get_handler,
    get_handlers,
)

adverbs = ('when', 'if', 'once')
pattern = r'^.*(?P<statement>(%s) (?P<value>.*) is (?P<adjective>(%s))).*' % (
    '|'.join(adverbs), '|'.join(get_all_adjectives()))

MATCH_REGEX = regex.compile(pattern, regex.IGNORECASE | regex.VERSION1)


def iter_locations(locations: Iterable[Path]) -> Iterable[Path]:
    for location in locations:
        if not location.exists():
            continue

        if location.is_dir():
            yield from (p for p in location.rglob('*') if not p.is_dir())
        else:
            yield location


def read_file(path: Path) -> Iterable[Tuple[BaseHandler, Workaround]]:
    with path.open('r') as fd:
        try:
            lines = fd.readlines()
        except UnicodeDecodeError:
            return

    for idx, line in enumerate(lines):
        match = MATCH_REGEX.search(line)
        if not match:
            continue

        handler = get_handler(match['value'], match['adjective'])

        if handler:
            start_idx = idx - 2 if idx - 2 > 0 else 0
            context = (''.join(lines[start_idx:idx]), ''.join(lines[idx + 1:idx + 4]))
            yield handler, Workaround(match, path, context, line=idx + 1)


def handle_files(paths: Iterable[Path]) -> Iterable[Tuple[Workaround, str]]:
    workarounds = (handler for path in iter_locations(paths) for handler in read_file(path))

    for handler, workaround in workarounds:
        result, status = handler.handle(workaround)
        if not result:
            continue

        yield workaround, status


def get_examples():
    for name, cls in sorted(get_handlers().items()):
        examples = cls.examples()
        examples_sample = random.sample(examples, min(len(examples), 3))
        examples_with_adverbs = ((random.choice(adverbs), ex) for ex in examples_sample)
        yield name, examples_with_adverbs
