from tubbs.hints.base import HintsBase, Hint, RegexHint, EOFEnd

from amino import Map, List
from amino.regex import Regex


ts_mods = List('implicit', 'lazy', 'protected(\[[^\]]+\])?', 'private(\[[^\]]+\])?', 'override')


class TemplateStatHint(RegexHint, EOFEnd):
    rex = r'\s*(({})\s*)*\b(def|val)\b'.format(ts_mods.mk_string('|'))

    @property
    def regex(self) -> Regex:
        return Regex(self.rex)

    @property
    def rules(self) -> List[str]:
        return List('templateStatDef')


class ImplDefHint(RegexHint, EOFEnd):

    @property
    def regex(self) -> Regex:
        return Regex(r'.*\b(class|object|trait)\b')

    @property
    def rules(self) -> List[str]:
        return List('implDef')


class Hints(HintsBase):

    @property
    def hints(self) -> Map[str, List[Hint]]:
        return Map(
            {
                'def': List(TemplateStatHint()),
                'impl': List(ImplDefHint()),
            }
        )

__all__ = ('Hints',)
