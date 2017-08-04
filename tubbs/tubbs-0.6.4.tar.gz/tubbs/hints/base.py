import abc

from amino import List, Map, Maybe, __, _, Empty, L, do, Just, Either
from amino.regex import Regex
from amino.util.string import ToStr

from ribosome.record import int_field, list_field, Record, dfield, maybe_field

from tubbs.logging import Logging


class HintMatch(Record):
    line = int_field()
    end_line = maybe_field(int)
    col = dfield(0)
    rules = list_field(str)

    @property
    def _str_extra(self) -> List:
        return List(self.line, self.col, self.rules) + self.end_line.to_list


class Hint(Logging, ToStr):

    @abc.abstractproperty
    def rules(self) -> List[str]:
        ...

    @abc.abstractmethod
    def match(self, content: List[str], cursor: int) -> Maybe[HintMatch]:
        ...

    @abc.abstractmethod
    def search_backwards(self, content: List[str], cursor: int) -> Maybe[HintMatch]:
        ...

    @abc.abstractmethod
    def find_end(self, content: List[str], cursor: int, start_line: int) -> Maybe[int]:
        ...

    def _line_match(self, content: List[str], cursor: int, line: int) -> HintMatch:
        return HintMatch(line=line, rules=self.rules, end_line=self.find_end(content, cursor, line))


class EOFEnd(Hint):
    '''Mixin for hints that don't specify and end position and thus will parse until EOF
    '''

    def find_end(self, content: List[str], cursor: int, start_line: int) -> Maybe[int]:
        return Empty()


class RegexHint(Hint):

    def __init__(self, back: bool=True) -> None:
        self.back = back

    @abc.abstractproperty
    def regex(self) -> Regex:
        ...

    @do
    def match(self, content: List[str], cursor: int) -> Maybe[HintMatch]:
        line = yield content.lift(cursor)
        yield self.regex.match(line)
        yield Just(self._line_match(content, cursor, cursor))

    def search_backwards(self, content: List[str], cursor: int) -> Maybe[HintMatch]:
        return (
            content[:cursor + 1]
            .reversed
            .index_where(lambda a: self.regex.matches(a)) /
            (cursor - _) /
            L(self._line_match)(content, cursor, _)
        )

    @property
    def _arg_desc(self) -> List[str]:
        return List(str(self.regex))


class HintsBase(ToStr):

    @abc.abstractproperty
    def hints(self) -> Map[str, List[Hint]]:
        ...

    def hint(self, ident: str) -> Either[str, List[Hint]]:
        return self.hints.lift(ident).to_either(f'no hint with ident `{ident}`')

    def match(self, content: List[str], line: int, ident: str) -> Either[str, HintMatch]:
        return (
            self.hint(ident) //
            __.find_map(lambda a: a.match(content, line)).to_either(f'no hint matched at line {line}')
        )

    def search_backwards(self, content: List[str], line: int, ident: str) -> Either[str, HintMatch]:
        return (
            self.hint(ident) //
            __.find_map(lambda a: a.search_backwards(content, line))
            .to_either(f'no hint found backwards from line {line}')
        )

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self.hints)

    @property
    def _arg_desc(self) -> List[str]:
        return List(str(self.hints))

__all__ = ('HintsBase',)
