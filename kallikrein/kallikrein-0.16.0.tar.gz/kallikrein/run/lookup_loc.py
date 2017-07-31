import abc
from types import ModuleType
import pkgutil
from pkgutil import ModuleInfo  # type: ignore

from amino.regex import Regex, Match
from amino import Path, Either, List, _, Just, Empty, L, Left, __
from amino.util.numeric import parse_int
from amino.list import Lists
from amino.util.exception import format_exception
from amino.util.string import ToStr
from amino.either import ImportFailure, ImportException

from kallikrein.run.data import (SpecLocation, LineSelector, FileMethodSelector, FileClassSelector, FileSelector,
                                 ModuleSelector, infer_path)
from kallikrein.util.string import red, blue

dir_loc_regex = None
file_loc_regex = Regex(
    r'(?P<path>.*?\.py)(:((?P<lnum>\d+)|(?P<select>\w+(\.\w+)?)))?$')
path_loc_regex = Regex(r'(?P<path>\w+(\.\w+)*)')
cls_def_regex = Regex(r'\s*(?P<kw>class|def) (?P<name>\w+)')
cls_regex = Regex(r'class (?P<name>\w+)')
init_name = '__init__.py'


class LookupFailure(ToStr):

    @staticmethod
    def from_import(fail: ImportFailure) -> 'LookupFailure':
        return LookupException(fail.exc) if isinstance(fail, ImportException) else InvalidLocator(fail.msg)

    @staticmethod
    def from_import_l(fail: ImportFailure) -> 'List[LookupFailure]':
        return List(LookupFailure.from_import(fail))

    @abc.abstractproperty
    def message(self) -> List[str]:
        ...

    @property
    def _arg_desc(self) -> List[str]:
        return self.message


class LookupException(LookupFailure):
    head = 'Exception during spec import:'

    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    @property
    def message(self) -> List[str]:
        return List(self.head, '') + format_exception(self.exc)

    @property
    def _arg_desc(self) -> List[str]:
        return List(f'{self.head}: {self.exc}')


class InvalidLocator(LookupFailure):

    def __init__(self, loc: str) -> None:
        self.loc = loc

    @property
    def message(self) -> List[str]:
        return List(f'invalid locator for single spec: {self.loc}')


class LookupFailures:

    def __init__(self, failures: List[LookupFailure], locator: str) -> None:
        self.failures = failures
        self.locator = locator

    @property
    def head(self) -> List[str]:
        pre = red('Could not resolve spec locator')
        post = red('. Errors were:')
        return List(f'{pre} {blue(self.locator)}{post}', '')

    @property
    def report_lines(self) -> List[str]:
        return self.head + self.failures.flat_map(lambda a: a.message.cons('')).drop(1)

    @property
    def report(self) -> str:
        return self.report_lines.join_lines


def resolve_module(path: Path) -> str:
    def rec(p: Path) -> List[str]:
        return (
            rec(p.parent).cat(p.name)
            if List.wrap(p.iterdir()).exists(_.name == init_name) else
            List()
        )
    return rec(path.parent).cat(path.stem).mk_string('.')


def lookup_file(loc: str) -> Either[str, List[SpecLocation]]:
    path = Path(loc)
    mod = resolve_module(path)
    selector = FileSelector(path)
    return (
        (
            List.lines(path.read_text()) //
            cls_regex.match //
            __.group('name')
        )
        .traverse(L(SpecLocation.create)(Just(path), mod, _, Empty(), selector, True), Either)
        if path.is_file() else
        Left('invalid path: {}'.format(loc))
    )


def lookup_file_lnum(path: Path, mod: str, lnum: int) -> Either[str, SpecLocation]:
    content = List.lines(path.read_text())[:lnum + 1].reversed
    selector = LineSelector(path, lnum)
    def found_def(name: str) -> Either[str, SpecLocation]:
        cls = content.find_map(cls_regex.match) // __.group('name')
        return cls // L(SpecLocation.create)(Just(path), mod, _, Just(name), selector, False)
    def found_cls_def(match: Match) -> Either[str, SpecLocation]:
        name = match.group('name')
        return (
            name // found_def
            if match.group('kw').contains('def') else
            name // L(SpecLocation.create)(Just(path), mod, _, Empty(), selector, False)
        )
    loc = content.find_map(cls_def_regex.match)
    return loc // found_cls_def


def lookup_file_select(fpath: Path, mod: str, select: str) -> Either[str, List[SpecLocation]]:
    parts = Lists.split(select, '.')
    meth = parts.lift(1)
    def create(cls: str) -> Either[str, SpecLocation]:
        selector = (
            meth /
            L(FileMethodSelector)(fpath, cls, _) |
            FileClassSelector(fpath, cls)
        )
        return SpecLocation.create(Just(fpath), mod, cls, meth, selector, False)
    return (
        parts.head.to_either('empty select') //
        create /
        List
    )


def handle_file_select(match: Match, mod: str, fpath: Path) -> Either[str, List[SpecLocation]]:
    return (match.group('select')) // L(lookup_file_select)(fpath, mod, _)


def handle_file_lnum(match: Match, mod: str, fpath: Path) -> Either[str, List[SpecLocation]]:
    return (
        match.group('lnum') //
        parse_int /
        (_ - 1) //
        L(lookup_file_lnum)(fpath, mod, _) /
        List
    )


def handle_file(match: Match, fpath: Path) -> Either[str, List[SpecLocation]]:
    mod = resolve_module(fpath)
    return (
        handle_file_select(match, mod, fpath)
        .o(lambda: handle_file_lnum(match, mod, fpath))
        .o(lambda: lookup_file(fpath))
        if fpath.is_file() else
        handle_dir(fpath)
        if fpath.is_dir() else
        Left('{} is not a file or dir'.format(fpath))
    )


def lookup_module(mod: ModuleType) -> Either[LookupFailure, List[SpecLocation]]:
    names = List.wrap(mod.__all__)  # type: ignore
    selector = ModuleSelector(mod.__name__)
    return names.traverse(L(SpecLocation.create)(infer_path(mod), mod.__name__, _, Empty(), selector, False), Either)


def exclude_module(mod: ModuleInfo) -> bool:
    return mod.ispkg or '._' in mod.name


def lookup_package(mod: ModuleType) -> Either[List[LookupFailure], List[SpecLocation]]:
    name = mod.__name__
    path = mod.__path__  # type: ignore
    names = List.wrap(pkgutil.walk_packages(path, prefix='{}.'.format(name))).filter_not(exclude_module) / _.name
    mods: Either[List[LookupFailure], List[ModuleType]] = (
        names
        .traverse(Either.import_module, Either)
        .lmap(LookupFailure.from_import_l)

    )
    return mods // __.flat_traverse(lookup_path, Either)


def lookup_path(path: ModuleType) -> Either[List[LookupFailure], List[SpecLocation]]:
    l = lookup_package if path.__package__ == path.__name__ else lookup_module
    return l(path)


def handle_path(path: str) -> Either[List[LookupFailure], List[SpecLocation]]:
    def single() -> Either[List[LookupFailure], List[SpecLocation]]:
        return SpecLocation.from_path(path).bimap(__.map(LookupFailure.from_import), List)
    return (
        (Either.import_module(path).lmap(LookupFailure.from_import_l) // lookup_path)
        .accum_error_f(single)
    )


def handle_dir(dpath: Path) -> Either[List[LookupFailure], List[SpecLocation]]:
    return Either.import_module(resolve_module(dpath)).lmap(LookupFailure.from_import_l) / lookup_path


def lookup_loc(loc: str) -> Either[LookupFailures, List[SpecLocation]]:
    fpath = Path(loc)
    file_match = file_loc_regex.match(loc)
    path_match = path_loc_regex.match(loc)
    return (
        path_match // __.group('path') // handle_path
        if path_match.present else
        file_match
        .flat_apzip(lambda a: a.group('path') / Path)
        .flat_map2(handle_file)
        if file_match.present else
        handle_dir(fpath)
        if fpath.is_dir() else
        Left(List(InvalidLocator(loc)))
    ).lmap(L(LookupFailures)(_, loc))

__all__ = ('lookup_loc', 'lookup_file_lnum', 'lookup_file', 'lookup_file_select')
