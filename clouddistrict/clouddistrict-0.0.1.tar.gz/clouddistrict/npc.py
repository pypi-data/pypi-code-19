'''
towniesim.npc
=============

Generate a random NPC

from .job import (ApothecaryJob, ButcherJob, HerbalistJob, ClothierJob,
                  ShoemakerJob, SpinsterJob, BakerJob, BarberJob,
                  BlacksmithJob, ArmorerJob, BowyerJob, AtilliatorJob,
                  FletcherJob, CookJob, ServerJob, ArtistJob, CandlemakerJob,
                  CarpenterJob, MoneylenderJob, ClerkJob, PotterJob,
                  LibrarianJob, ScribeJob, FishermanJob, FarmerJob,
                  BartenderJob, ForesterJob, Job)
'''
from enum import Enum
from random import choice
from .namerator import make_name
from .race import Race, Age
from .util import nds, random_from_list

CLASSES = ['fighter', 'wizard', 'rogue', 'cleric', 'ranger', 'barbarian',
           'druid', 'monk', 'bard', 'paladin', 'sorcerer', 'warlock']


class Memory:

    def __init__(self):
        self.reaction = 0


class NPC:
    COUNT = 0
    OBJS = {}

    @classmethod
    def next(cls):
        cls.COUNT += 1
        return cls.COUNT

    def __init__(self, race=None, name=None, level=1, klass=None, job=None,
                 age=None, gender=None, lover=None, family=None):
        self.id = NPC.next()
        self.idstr = 'NPC#{}'.format(self.id)
        NPC.OBJS[self.idstr] = self
        self.chars = Character.rand()
        race = race or choice(['human', 'half-orc', 'elf', 'dwarf', 'half-elf',
                               'gnome', 'halfling'])
        self.gender = gender or choice(['male', 'female'])
        self.race = race
        self.name = name or make_name(race=self.race, gender=self.gender)
        self.level = level
        self.klass = klass
        self.job = job
        self.age = self.race.random_age(age=age)
        self.lover = lover
        self.family = family
        self.owned_residences = []
        self.owned_buildings = []
        self.init_racism()

    @property
    def race(self):
        return Race.get_race(self._race)

    @race.setter
    def race(self, val):
        if hasattr(val, 'NAME'):
            self._race = val.NAME
        else:
            self._race = val

    def __repr__(self):
        age = self.race.get_age(self.age).value
        mid = ' '
        if self.job:
            mid = ' {!r} '.format(self.job)
        elif self.klass:
            mid = ' {!r} '.format(self.klass)
        return '{age} {gender} {race}{mid}"{name}" wealth={wealth}'.format(
            age=age,
            race=self.race.NAME.title(),
            gender=self.gender,
            mid=mid,
            name=self.name,
            wealth=self.family.wealth,
        )

    @property
    def lover(self):
        if self._lover is None:
            return None
        return NPC.OBJS[self._lover]

    @lover.setter
    def lover(self, val):
        if isinstance(val, NPC):
            self._lover = val.idstr
        else:
            self._lover = val

    @property
    def family(self):
        from .family import Family
        if self._family is None:
            return None
        return Family.OBJS[self._family]

    @family.setter
    def family(self, val):
        from .family import Family
        if isinstance(val, Family):
            self._family = val.idstr
        else:
            self._family = val

    @property
    def job(self):
        from .job import Job
        if self._job is None:
            return None
        return Job.OBJS[self._job]

    @job.setter
    def job(self, val):
        from .job import Job
        if isinstance(val, Job):
            self._job = val.idstr
        else:
            self._job = val

    @property
    def owned_buildings(self):
        from .building import Building
        blds = []
        for bld in self._owned_buildings:
            blds.append(Building.OBJS[bld])
        return blds

    @owned_buildings.setter
    def owned_buildings(self, val):
        self._owned_buildings = []
        for bld in val:
            self._owned_buildings.append(bld.idstr)

    @property
    def owned_residences(self):
        from .residence import Residence
        blds = []
        for bld in self._owned_residences:
            blds.append(Residence.OBJS[bld])
        return blds

    @owned_residences.setter
    def owned_residences(self, val):
        self._owned_residences = []
        for bld in val:
            self._owned_residences.append(bld.idstr)

    def output(self):
        s = '{!r}'.format(self)
        if self.job:
            s += '\nworks at {!r}'.format(self.job)
        s += '\n{}\n'.format('\n'.join(self.chars))
        print(s)

    def init_racism(self):
        self.racism = {}
        for r in Race.get_races():
            self.racism[r.NAME] = nds(5, 10) - nds(5, 10)
            self.racism[r.NAME] += r.RACISM
        self.racism[self.race.NAME] -= 25

    def take_last_name(self, other):
        last = other.get_last_name()
        if last is None:
            raise ValueError('No name for significant other: {!r}'.format(other))
            return None
        myspl = self.name.split()
        self.name = '{} {}'.format(myspl[0], last).title()
        return last

    def long_r(self):
        return (
            'NPC(name="{s.name}", race="{s.race!r}", age={s.age}, '
            'level={s.level}, klass={s.klass!r}, job={s.job!r})'
            .format(s=self)
        )

    def get_last_name(self):
        spl = self.name.split()
        if len(spl) == 1:
            raise ValueError('No name for self: {!r}'.format(self))
            return None
        return spl[-1].title()

    def get_age(self):
        return self.race.get_age(self.age)

    def can_work(self):
        return self.get_age() not in (Age.child, Age.venerable)


class QualityStrength(Enum):
    average = None
    very = 'very'
    extremely = 'extremely'

    @classmethod
    def prepend(cls, s):
        c = random_from_list({
            None: 85,
            'very': 12,
            'extremely': 3,
        })
        if c:
            return '{} {}'.format(c, s)
        else:
            return s


BODY_QUALITIES = {
    'strength': ('weak', 'strong'),
    'intelligence': ('stupid', 'smart'),
    'agility': ('clumsy', 'graceful'),
    'weight': ('thin', 'fat'),
    'looks': ('ugly', 'pretty'),
}

PERSONALITIES = {
    'religion': ('atheistic', 'superstitious', 'spiritual', 'religious'),
    'sympathy': ('empathetic', 'self-centered'),
    'vanity': ('narcississtic', 'modest'),
    'naivete': ('gullible', 'cunning'),
    'courage': ('cowardly', 'courageous'),
    'laziness': ('lazy', 'ambitious'),
    'stubborness': ('stubborn', 'compliant'),
    'calmness': ('anxious', 'calm'),
    'introvert': ('introverted', 'extroverted'),
    'rudeness': ('rude', 'polite'),
    'generous': ('stingy', 'generous'),
    'playfulness': ('serious', 'playful'),
    'romantic': ('cold', 'romantic'),
    'chaotic': ('chaotic', 'lawful'),
    'evil': ('evil', 'good'),
    'skeptic': ('skeptical', 'trusting'),
    'private': ('private', 'public'),
    'gloomy': ('gloomy', 'joyful'),
    'security': ('insecure', 'confident'),
    'paranoia': ('paranoid', 'stable'),
    'submission': ('submissive', 'dominating'),
    'appreciate': ('unappreciative', 'gracious'),
    'volume': ('soft-spoken', 'obnoxious'),
    'optimist': ('pessimistic', 'optimistic'),
}


class Character:

    @classmethod
    def rand(cls):
        chars = []
        body_ct = random_from_list({
            0: 40,
            1: 50,
            2: 10,
        })
        mood_ct = random_from_list({
            1: 60,
            2: 35,
            3: 5,
        })
        if body_ct + mood_ct < 2:
            mood_ct += 1
        can_use_body = set(BODY_QUALITIES.keys())
        can_use_pers = set(PERSONALITIES.keys())
        for i in range(body_ct):
            key = choice(list(can_use_body))
            can_use_body.remove(key)
            b = choice(BODY_QUALITIES[key])
            s = QualityStrength.prepend(b)
            chars.append(s)

        for i in range(mood_ct):
            key = choice(list(can_use_pers))
            can_use_pers.remove(key)
            b = choice(PERSONALITIES[key])
            s = QualityStrength.prepend(b)
            chars.append(s)
        return chars
