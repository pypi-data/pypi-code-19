'''
Generate a town based on a configuration

pseudocode:

    For each district, tally up the commercial and industrial and residential
    For each commercial, create a random building by wealth
    For each industrial, create a random building by wealth
    For each residential, create an NPC family
      For each new family, assign an empty workplace of appropriate wealth
          Find first job which CAN_OWN
              assign to older members and set them as owner
          random choice for other members of family
    For each unowned commercial, create new family and say they live there

Later:
    military
    government
'''
import os
import re
import yaml
from random import uniform, shuffle
from itertools import chain
from collections import defaultdict
from .building import Building
from .residence import Residence
from .family import Family
from .util import random_from_list


RE_FILENAME = re.compile(r'[^a-zA-Z0-9 -_]')


def make_filename(name):
    name = name.lower().replace(' ', '_').replace('-', '_')
    return RE_FILENAME.sub('', name)


class TownConfig:

    def __init__(self, path):
        self.path = path
        with open(path) as f:
            self.config = yaml.load(f)
        self.validate_config()

    def __repr__(self):
        return 'TownConfig({!r})'.format(self.config)

    @property
    def districts(self):
        return self.config['districts']

    @property
    def races(self):
        return self.config.get('race')

    @property
    def industry(self):
        return self.config.get('industry')

    def validate_config(self):
        if 'districts' not in self.config:
            raise ValueError('town config must specify at least one district')
        if not self.races:
            self.config['race'] = {
                'human': 60,
                'elf': 12,
                'dwarf': 12,
                'half-elf': 6,
                'half-orc': 4,
                'gnome': 3,
                'halfling': 3,
            }
        if not self.industry:
            self.config['industry'] = {'farmer': 10}


class District:

    def __init__(self, name=None, config=None, default_races=None):
        self._name = name
        self.config = config
        self.default_races = default_races
        self.buildings = []
        self.residences = []
        self.families = []
        self.npcs = []

    def __repr__(self):
        return (
            'District({!r}, #buildings={}, #residences={}, #families={})'
            .format(self._name, len(self.buildings), len(self.residences),
                    len(self.families))
        )

    def create(self):
        wealth = self.config.get('wealth') or 3
        water = self.config.get('water') or False
        military = self.config.get('military') or False
        races = self.config.get('race', self.default_races)
        comm = self.config.get('commercial', 0)
        rezs = self.config.get('residences', 0)
        ind = self.config.get('industrial', {})
        for i in range(comm):
            bld = Building.rand(
                wealth=wealth,
                water=water,
                military=military,
                industrial=False,
            )(wealth=wealth, district=self._name)
            self.buildings.append(bld)
        for type_name, ct in ind.items():
            typ = Building.get_building(type_name)
            for i in range(ct):
                bld = typ(wealth=wealth)
                self.buildings.append(bld)
        for i in range(rezs):
            typ = Residence.rand(wealth=self.config.get('wealth') or 2)
            bld = typ(wealth=wealth)
            race = random_from_list(races)
            fam = Family(race=race, wealth=wealth)
            bld.owner = fam.oldest()
            bld.owner.owned_residences += [bld]
            self.residences.append(bld)
            self.families.append(fam)
            self.npcs.extend(list(fam.members()))

    def auction_buildings(self):
        fams = sorted(self.families, key=lambda x: x.gold, reverse=True)
        unowned = sorted(
            (x for x in self.buildings if x.owner is None),
            key=lambda x: x.COST,
            reverse=True,
        )
        for i in range(2):
            for un in unowned:
                for fam in fams:
                    if fam.can_afford(un):
                        fam.buy(un)
                        break
                fams = sorted(self.families, key=lambda x: x.gold, reverse=True)
            unowned = sorted(
                (x for x in self.buildings if x.owner is None),
                key=lambda x: x.COST,
                reverse=True,
            )

    def assign_jobs(self):
        npcs = [x for x in self.npcs if x.can_work() and x.job is None]
        for npc in npcs:
            owns = [
                x for x in npc.owned_buildings
                if x.count_missing_jobs() > 0
            ]
            for bld in owns:
                job = bld.hire_worker(npc)
                if job is not None:
                    break
            if npc.job is not None:
                continue
            buildings = sorted(
                self.buildings,
                key=lambda x: x.count_missing_jobs(),
                reverse=True,
            )
            buildings = [x for x in buildings if x.count_missing_jobs() > 0]
            if not buildings:
                break
            buildings[0].hire_worker(npc)

    def dump(self, out):
        fname = make_filename(self._name) + '.txt'
        path = os.path.join(out, fname)
        with open(path, 'w') as f:
            f.write('name: {}\n\n'.format(self._name))
            f.write('#occupants: {}\n'.format(len(self.npcs)))
            f.write('#families: {}\n'.format(len(self.families)))
            f.write('#residences: {}\n'.format(len(self.residences)))
            f.write('#businesses: {}\n\n'.format(len(self.buildings)))
            f.write('Residences\n----------\n\n')
            for i, res in enumerate(self.residences):
                f.write('Residence {}\n'.format(i + 1))
                f.write(res.dump() + '\n\n')
            f.write('NPCs\n----\n\n')
            for fam in self.families:
                fstr = '{} "{}"'.format(fam.idstr, fam.name)
                f.write(fstr + '\n' + len(fstr) * '-' + '\n\n')
                for npc in fam.members():
                    f.write(npc.dump() + '\n\n')
            f.write('\nBUILDINGs\n---------\n\n')
            for bld in self.buildings:
                f.write(bld.dump() + '\n\n')


class Town:

    def __init__(self, config):
        if isinstance(config, TownConfig):
            self.config = config
        else:
            self.config = TownConfig(config)
        self.districts = []
        self.create()
        self.districts = sorted(
            self.districts,
            key=lambda x: (x.config.get('wealth'), x._name),
        )

    def __repr__(self):
        s = ''
        for i, d in enumerate(self.districts):
            s += '  {}: {!r}\n'.format(i, d)
        return 'Town(\n{})'.format(s)

    def __getitem__(self, i):
        return self.districts[i]

    @property
    def families(self):
        return list(chain(*[x.families for x in self.districts]))

    @property
    def npcs(self):
        return list(chain(*[x.npcs for x in self.districts]))

    @property
    def buildings(self):
        return list(chain(*[x.buildings for x in self.districts]))

    @property
    def residences(self):
        return list(chain(*[x.residences for x in self.districts]))

    def finish_assigning_jobs(self):
        npcs = [x for x in self.npcs if x.can_work() and x.job is None]
        for npc in npcs:
            buildings = sorted(
                self.buildings,
                key=lambda x: x.count_missing_jobs(),
                reverse=True,
            )
            buildings = [x for x in buildings if x.count_missing_jobs() > 0]
            if not buildings:
                break
            buildings[0].hire_worker(npc)
        buildings = [x for x in buildings if x.count_missing_jobs() > 0]
        for bld in buildings:
            raise ValueError('{!r} failed to get enough workers!'.format(bld))
        npcs = [x for x in self.npcs if x.can_work() and x.job is None]
        buildings = self.buildings
        for npc in npcs:
            shuffle(buildings)
            for building in self.buildings:
                job = building.hire_worker(npc)
                if job is not None:
                    break
            else:
                raise ValueError('{!r} failed to get a job!'.format(npc))

    def auction_buildings(self):
        fams = sorted(self.families, key=lambda x: x.gold, reverse=True)
        unowned = sorted(
            (x for x in self.buildings if x.owner is None),
            key=lambda x: x.COST,
            reverse=True,
        )
        while unowned:
            bought = False
            for un in unowned:
                for fam in fams:
                    if fam.can_afford(un):
                        fam.buy(un)
                        bought = True
                        break
                fams = sorted(self.families, key=lambda x: x.gold, reverse=True)
            unowned = sorted(
                (x for x in self.buildings if x.owner is None),
                key=lambda x: x.COST,
                reverse=True,
            )
            if not bought:
                for fam in fams:
                    if uniform(0, 1) < 0.1:
                        fam.gold *= 1.5

    def create(self):
        for name, dist in self.config.districts.items():
            new = District(name=name, config=dist,
                           default_races=self.config.races)
            self.districts.append(new)
            new.create()
        for dist in self.districts:
            dist.auction_buildings()
        worked = defaultdict(list)
        for bld in self.buildings:
            worked[0].append(bld)
        worked[0].sort(key=lambda x: x.wealth, reverse=True)
        self.auction_buildings()
        for dist in self.districts:
            dist.assign_jobs()
        self.finish_assigning_jobs()

    def output_residents(self):
        for npc in self.npcs:
            npc.output()

    def dump(self, output_dir):
        from yaml.representer import Representer
        from .race import MetaRace
        from .building import MetaBuilding
        from .job import MetaJob
        from .residence import MetaResidence
        for meta in (MetaRace, MetaBuilding, MetaJob, MetaResidence):
            Representer.add_representer(meta, Representer.represent_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        raw_path = os.path.join(output_dir, 'raw.yml')
        with open(raw_path, 'w') as f:
            s = yaml.dump({'town': self}, default_flow_style=False)
            f.write(s)
        print('Saved raw town data to {}'.format(raw_path))
        for district in self.districts:
            district.dump(output_dir)

    def reload(self):
        from .building import Building
        from .residence import Residence
        from .family import Family
        from .job import Job
        from .npc import NPC
        Building.COUNT = len(self.buildings)
        Residence.COUNT = len(self.residences)
        Family.COUNT = len(self.families)
        NPC.COUNT = len(self.npcs)
        Job.COUNT = len([x for x in self.npcs if x._job is not None])
        for bld in self.buildings:
            Building.OBJS[bld.idstr] = bld
            for job in bld.jobs:
                Job.OBJS[job.idstr] = job
        for res in self.residences:
            Residence.OBJS[res.idstr] = res
        for fam in self.families:
            Family.OBJS[fam.idstr] = fam
        for npc in self.npcs:
            NPC.OBJS[npc.idstr] = npc
