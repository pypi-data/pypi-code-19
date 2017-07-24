'''
towniesim.race
==============
'''
from enum import Enum
from random import choice
from .util import gauss_mm, le_switch


class Age(Enum):
    child = 'child'
    adult = 'adult'
    middle = 'middle-aged'
    old = 'old'
    venerable = 'venerable'

    @classmethod
    def random_age(cls, parents=None):
        parents = [x.get_age() for x in parents if x]
        choices = [x for x in cls]
        for parent in parents:
            for age in choices[:]:
                if age >= parent:
                    choices.remove(age)
        return choice(choices)

    @classmethod
    def random_parent(cls):
        return choice([Age.adult, Age.middle, Age.old])

    @classmethod
    def random_notchild(cls):
        return choice([Age.adult, Age.middle, Age.old, Age.venerable])

    @classmethod
    def random_child(cls):
        return choice([Age.child, Age.adult])

    @classmethod
    def random(cls):
        return choice([x for x in cls])

    def _compare(self, other):
        numeric = {
            self.__class__.child.value: 0,
            self.__class__.adult.value: 1,
            self.__class__.middle.value: 2,
            self.__class__.old.value: 3,
            self.__class__.venerable.value: 4,
        }
        if numeric[self.value] == numeric[other.value]:
            return 0
        if numeric[self.value] < numeric[other.value]:
            return -1
        if numeric[self.value] > numeric[other.value]:
            return 1

    def __lt__(self, other):
        return self._compare(other) < 0

    def __gt__(self, other):
        return self._compare(other) > 0

    def __eq__(self, other):
        return self._compare(other) == 0

    def __le__(self, other):
        return self._compare(other) <= 0

    def __ge__(self, other):
        return self._compare(other) >= 0

    def __ne__(self, other):
        return self._compare(other) != 0


class MetaRace(type):
    RACES = {}

    def __new__(cls, name, bases, dct):
        if name == 'Race':
            return super(MetaRace, cls).__new__(cls, name, bases, dct)
        new_cls = super(MetaRace, cls).__new__(cls, name, bases, dct)
        MetaRace.RACES[dct['NAME']] = new_cls
        return new_cls


class Race(metaclass=MetaRace):

    @classmethod
    def get_races(cls):
        return MetaRace.RACES.values()

    @classmethod
    def get_race(cls, race):
        return MetaRace.RACES[race]

    @classmethod
    def get_age(cls, age_num):
        age = le_switch(cls.AGE, age_num)
        if age is None:
            return Age.venerable
        return age

    @classmethod
    def random_age(cls, age=None):
        ages = sorted(cls.AGE.items())
        if age is None:
            age = choice(a for a in Age)
        if age is Age.child:
            return gauss_mm(ages[0][0] / 2, ages[0][0] / 3, 0, ages[0][0])
        elif age is Age.adult:
            mid = (ages[0][0] + ages[1][0]) / 2
            return gauss_mm(mid, mid / 2, ages[0][0] + 1, ages[1][0])
        elif age is Age.middle:
            mid = (ages[1][0] + ages[2][0]) / 2
            return gauss_mm(mid, mid / 2, ages[1][0] + 1, ages[2][0])
        elif age is Age.old:
            mid = (ages[2][0] + ages[3][0]) / 2
            return gauss_mm(mid, mid / 2, ages[2][0] + 1, ages[3][0])
        elif age is Age.venerable:
            mid = (ages[3][0] + 1) + (ages[0][0] / 2)
            return gauss_mm(mid, mid / 2, ages[3][0] + 1, None)


class Human(Race):
    NAME = 'human'
    AGE = {15: Age.child, 34: Age.adult, 52: Age.middle, 69: Age.old}
    RACISM = 0


class HalfOrc(Race):
    NAME = 'half-orc'
    AGE = {12: Age.child, 29: Age.adult, 44: Age.middle, 59: Age.old}
    RACISM = 10


class Elf(Race):
    NAME = 'elf'
    AGE = {40: Age.child, 174: Age.adult, 262: Age.middle, 349: Age.old}
    RACISM = 0


class Dwarf(Race):
    NAME = 'dwarf'
    AGE = {30: Age.child, 124: Age.adult, 187: Age.middle, 249: Age.old}
    RACISM = 0


class HalfElf(Race):
    NAME = 'half-elf'
    AGE = {20: Age.child, 61: Age.adult, 92: Age.middle, 124: Age.old}
    RACISM = 5


class Gnome(Race):
    NAME = 'gnome'
    AGE = {25: Age.child, 99: Age.adult, 262: Age.middle, 349: Age.old}
    RACISM = 0


class Halfling(Race):
    NAME = 'halfling'
    AGE = {18: Age.child, 49: Age.adult, 74: Age.middle, 99: Age.old}
    RACISM = -5
