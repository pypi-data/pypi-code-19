'''
towniesim.family
================
'''
from enum import Enum
from random import choice, uniform
from itertools import chain
from .race import Age
from .npc import NPC
from .util import even_switch, nds, gauss_mm


class FamilyType(Enum):
    normal = 'husband, wife and children'
    single_father = 'father and children'
    single_mother = 'mother and children'
    siblings = 'siblings'
    single_male = 'single male'
    single_female = 'single female'


def random_gold(wealth):
    if wealth == 0:
        return 0
    if wealth == 1:
        return int(uniform(500, 1500))
    if wealth == 2:
        return int(uniform(2500, 5000))
    if wealth == 3:
        return int(uniform(5000, 50000))
    return uniform(2500, 5000)


class Family:
    COUNT = 0
    OBJS = {}

    @classmethod
    def next(cls):
        cls.COUNT += 1
        return cls.COUNT

    TYPES = (
        (50, FamilyType.normal),
        (15, FamilyType.single_male),
        (15, FamilyType.single_female),
        (10, FamilyType.siblings),
        (5, FamilyType.single_father),
        (5, FamilyType.single_mother),
    )

    def __repr__(self):
        fam = [repr(m) for m in self.members()]
        fam = '\n - ' + '\n - '.join(fam)
        return 'Family({}\n)'.format(fam)

    def __init__(self, race=None, wealth=0):
        self.id = Family.next()
        self.idstr = 'Family#{}'.format(self.id)
        Family.OBJS[self.idstr] = self
        self.name = None
        self.mother = None
        self.father = None
        self.children = []
        self.family_type = even_switch(self.TYPES, nds(1, 100))
        self.race = race
        self.wealth = wealth
        self.gold = random_gold(wealth)
        if self.family_type == FamilyType.normal:
            self.father = self.create_male(age=Age.random_parent())
            self.mother = self.create_female(age=Age.random_parent())
            self.mother.take_last_name(self.father)
            self.children = self.create_children()
            for child in self.children:
                child.take_last_name(self.father)
            self.name = self.father.get_last_name()
        elif self.family_type == FamilyType.single_father:
            self.father = self.create_male(age=Age.random_parent())
            self.children = self.create_children()
            for child in self.children:
                child.take_last_name(self.father)
            self.name = self.father.get_last_name()
        elif self.family_type == FamilyType.single_mother:
            self.mother = self.create_female(age=Age.random_parent())
            self.children = self.create_children()
            for child in self.children:
                child.take_last_name(self.mother)
            self.name = self.mother.get_last_name()
        elif self.family_type == FamilyType.single_male:
            self.father = self.create_male(age=Age.random_notchild())
            self.name = self.father.get_last_name()
        elif self.family_type == FamilyType.single_female:
            self.mother = self.create_female(age=Age.random_notchild())
            self.name = self.mother.get_last_name()
        elif self.family_type == FamilyType.siblings:
            self.children = self.create_children(min_num=2,
                                                 age=Age.random_parent())
            children = list(self.children)
            for child in children[1:]:
                child.take_last_name(children[0])
            self.name = children[0].get_last_name()
        else:
            raise ValueError('No family type: {!r}'.format(self.family_type))
        self.link_family()

    @property
    def father(self):
        if self._father is None:
            return None
        return NPC.OBJS[self._father]

    @father.setter
    def father(self, val):
        if isinstance(val, NPC):
            self._father = val.idstr
        else:
            self._father = val

    @property
    def mother(self):
        if self._mother is None:
            return None
        return NPC.OBJS[self._mother]

    @mother.setter
    def mother(self, val):
        if isinstance(val, NPC):
            self._mother = val.idstr
        else:
            self._mother = val

    @property
    def children(self):
        return [NPC.OBJS[child] for child in self._children]

    @children.setter
    def children(self, val):
        self._children = []
        for child in val:
            if isinstance(child, NPC):
                self._children.append(child.idstr)
            else:
                self._children.append(child)

    def create_male(self, age=None):
        age = age or Age.random()
        new = NPC(race=self.race, gender='male', age=age)
        return new

    def create_female(self, age=None):
        age = age or Age.random()
        new = NPC(race=self.race, gender='female', age=age)
        return new

    def create_children(self, min_num=1, age=None):
        children = set()
        for i in range(int(gauss_mm(2, 1, min_num, 9))):
            func = choice([self.create_male, self.create_female])
            new = func(age=age)
            children.add(new)
        return children

    def link_family(self):
        if self.father:
            self.father.lover = self.mother
            self.father.family = self
        if self.mother:
            self.mother.lover = self.father
            self.mother.family = self
        for child in self.children:
            child.family = self

    def members(self):
        if self.father:
            yield self.father
        if self.mother:
            yield self.mother
        if self.children:
            for child in self.children:
                yield child

    def assign_workplace(self, workplace):
        members = set()
        jobtype = choice(workplace.JOBS)
        for mem in self.members():
            if mem.get_age() in (Age.child, Age.venerable):
                continue
            members.add(mem)
            job = jobtype(location=workplace)
            mem.set_job(job)

    @property
    def owned_buildings(self):
        return list(chain(*[x.owned_buildings for x in self.members()]))

    @property
    def owned_residences(self):
        return list(chain(*[x.owned_residences for x in self.members()]))

    def oldest(self):
        return max(list(self.members()), key=lambda x: x.age)

    def oldest_nonowner(self):
        members = [
            x for x in self.members()
            if not (x.owned_buildings or x.age == Age.child)
        ]
        if not members:
            return None
        return max(members, key=lambda x: x.age)

    def working(self):
        return [
            x for x in self.members()
            if x.age not in (Age.child, Age.venerable)
        ]

    def can_afford(self, building):
        return self.gold >= building.COST

    def buy(self, building):
        from .building import Building
        from .residence import Residence
        self.gold -= building.COST
        owner = self.oldest_nonowner()
        if owner is None:
            if not self.working():
                owner = self.oldest()
            else:
                owner = choice(self.working())
        building.owner = owner
        if isinstance(building, Building):
            owner.owned_buildings += [building]
        elif isinstance(building, Residence):
            owner.owned_residences += [building]
        else:
            raise ValueError('cant handle building type {!r}'.format(building))
        return owner
