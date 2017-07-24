'''
towniesim.residence
===================
'''
from random import choice


class MetaResidence(type):

    RESIDENCES = {}

    def __new__(cls, name, bases, dct):
        new_cls = super(MetaResidence, cls).__new__(cls, name, bases, dct)
        if name == 'Residence':
            return new_cls
        MetaResidence.RESIDENCES[dct['NAME']] = new_cls
        return new_cls


class Residence(metaclass=MetaResidence):
    COUNT = 0
    OBJS = {}

    @classmethod
    def next(cls):
        cls.COUNT += 1
        return cls.COUNT

    def __init__(self, owner=None, wealth=0, **kwargs):
        self.id = Residence.next()
        self.idstr = '{}#{}'.format(self.NAME, self.id).lower()
        Residence.OBJS[self.idstr] = self
        self.wealth = wealth
        self.owner = owner

    @property
    def owner(self):
        from .npc import NPC
        if self._owner is None:
            return None
        return NPC.OBJS[self._owner]

    @owner.setter
    def owner(self, val):
        from .npc import NPC
        if isinstance(val, NPC):
            self._owner = val.idstr
        else:
            self._owner = val

    @classmethod
    def get_residences(cls, max_level=None):
        rezs = MetaResidence.RESIDENCES.values()
        if max_level is not None:
            rezs = [r for r in rezs if r.LEVEL <= max_level]
        return rezs

    @classmethod
    def get_residence(cls, name):
        return MetaResidence.RESIDENCES[name]

    @classmethod
    def rand(cls, wealth=None):
        if not wealth:
            return choice([Cottage, Home, TownHouse])
        if wealth == 1:
            return choice([Cottage, Home])
        if wealth == 2:
            return choice([Cottage, Home, TownHouse])
        if wealth == 3:
            return choice([Cottage] + [Home, TownHouse] * 9 + [Mansion])
        return Home

    def dump(self):
        residents = ''
        for res in self.owner.family.members():
            residents += '- {res!r} {resid}\n'.format(res=res, resid=res.idstr)
        return '''{lastname}'s {name}
ID: {id}
Owner: {owner!r}
Owner ID: {ownerid}
Residents:\n{residents}
'''.format(
            lastname=self.owner.name.split()[-1],
            name=self.NAME,
            id=self.idstr,
            owner=self.owner,
            ownerid=self.owner.idstr,
            residents=residents,
    )


class Cottage(Residence):
    NAME = 'cottage'
    LEVEL = 1


class Home(Residence):
    NAME = 'home'
    LEVEL = 1


class TownHouse(Residence):
    NAME = 'townhouse'
    LEVEL = 2


class Mansion(Residence):
    NAME = 'mansion'
    LEVEL = 3
