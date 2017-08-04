from typing import Tuple, Any, Callable

from ribosome.record import Record, field, str_field

from tubbs.tatsu.base import ParserBase
from tubbs.hints.base import HintsBase, HintMatch
from tubbs.logging import Logging
from tubbs.tatsu.ast import AstMap

from amino import Maybe, __, L, _, List, Map, Either, LazyList
from amino.func import tupled2


class StartMatch(Record):
    ast = field(AstMap)
    rule = str_field()
    ident = str_field()
    hint = field(HintMatch)

    @property
    def _str_extra(self) -> List[Any]:
        return List(self.ident, self.rule, self.hint)

    @property
    def info(self) -> Map:
        return Maybe.check(self.ast.info) / __._asdict() / Map | Map()

    @property
    def line(self) -> int:
        return self.hint.line

    @property
    def start(self) -> int:
        return self.ast.start_line.lnum + self.line

    @property
    def start1(self) -> int:
        ''' first line of the match in 1-based indexing for vim
        '''
        return self.start + 1

    @property
    def end(self) -> int:
        return self.ast.end_line.lnum + self.line

    @property
    def end1(self) -> int:
        ''' last line of the match in 1-based indexing for vim
        '''
        return self.end + 1

    @property
    def range(self) -> Tuple[int, int]:
        return self.start, self.end + 1

    @property
    def range1(self) -> Tuple[int, int]:
        return self.start1, self.end1

    @property
    def range_inclusive(self) -> Tuple[int, int]:
        return self.start, self.end


class Crawler(Logging):

    def __init__(self, content: List[str], line: int, parser: ParserBase, hints: Maybe[HintsBase]) -> None:
        self.content = content
        self.line = line
        self.parser = parser
        self.hints = hints.to_either('no hints specified')

    def search_backwards(self, ident: str) -> Either[str, HintMatch]:
        return self.hints // __.search_backwards(self.content, self.line, ident)

    def match(self, ident: str) -> Either[str, HintMatch]:
        return self.hints // __.match(self.content, self.line, ident)

    def search_backwards_and_parse(self, ident: str) -> Either[str, StartMatch]:
        self.log.debug(f'crawling for {ident}')
        return self.search_backwards(ident) // L(self._parse)(ident, _)

    def match_and_parse(self, ident: str) -> Either[str, StartMatch]:
        self.log.debug(f'crawling for {ident}')
        return self.match(ident) // L(self._parse)(ident, _)

    def candidates(self, idents: List[str]) -> LazyList[Tuple[str, HintMatch]]:
        def check(f: Callable[[str], Either[str, HintMatch]], ident: str) -> Either[str, Tuple[str, HintMatch]]:
            return f(ident).map(lambda a: (ident, a))
        return (
            LazyList(idents).collect(L(check)(self.match, _)) +
            LazyList(idents).collect(L(check)(self.search_backwards, _))
        )

    @property
    def parsable_range(self) -> Either[str, StartMatch]:
        err = 'could not find parsable range for {}'
        keys = self.hints.map(_.hints.k) | List()
        return (
            self.candidates(keys)
            .collect(tupled2(self._parse))
            .head
            .to_either(err.format(self.hints.value))
        )

    def _default_start(self, ident: str) -> HintMatch:
        return HintMatch(line=self.line, rules=List(ident))

    def _parse(self, ident: str, match: HintMatch) -> Either[str, StartMatch]:
        self.log.debug('parsing {} for {}'.format(match, ident))
        text = self.content[match.line:].join_lines
        def match_rule(rule: str) -> Either[str, StartMatch]:
            return (
                self.parser.parse(text, rule) /
                L(StartMatch.from_attr('ast'))(_, rule=rule, ident=ident, hint=match)
            )
        return (
            match.rules
            .find_map(match_rule)
            .to_either(lambda: f'no rule matched for `{ident}` at {match}')
        )

__all__ = ('Crawler',)
