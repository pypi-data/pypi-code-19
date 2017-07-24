'''
towniesim.shop
==============
'''
from random import choice, uniform
from .job import *


class MetaBuilding(type):
    SHOPS = {}

    def __new__(cls, name, bases, dct):
        if name in ('Building', 'Residence'):
            return super(MetaBuilding, cls).__new__(cls, name, bases, dct)
        if 'JOBS' not in dct:
            dct['JOBS'] = {}
        if 'LEVEL' not in dct:
            dct['LEVEL'] = 0
        for key in ('MILITARY', 'WATER', 'INDUSTRIAL'):
            dct[key] = dct.get(key, False)
        new_cls = super(MetaBuilding, cls).__new__(cls, name, bases, dct)
        MetaBuilding.SHOPS[dct['NAME']] = new_cls
        return new_cls


class Workforce:

    def __init__(self):
        self.data = {}

    def __getitem__(self, val):
        from .npc import NPC
        if val.NAME in self.data:
            return [NPC.OBJS[x] for x in self.data[val.NAME]]
        else:
            return []

    def add(self, job_type, npc):
        self.data[job_type.NAME] = self.data.get(job_type.NAME, [])
        self.data[job_type.NAME].append(npc.idstr)

    def items(self):
        for name, ids in self.data.items():
            job = Job.get_job(name)
            yield (job, self[job])


class Building(metaclass=MetaBuilding):
    COUNT = 0
    OBJS = {}

    @classmethod
    def next(cls):
        cls.COUNT += 1
        return cls.COUNT

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

    def __init__(self, owner=None, wealth=0, inventory=None, district=None,
                 **kwargs):
        self.owner = owner
        self.jobs = []
        self.wealth = wealth
        self.workers = Workforce()
        self.inventory = inventory or set()
        self.district = district
        self.id = Building.next()
        self.idstr = '{}#{}'.format(self.NAME, self.id).lower()
        Building.OBJS[self.idstr] = self
        self.name = self.NAME

    def count_missing_jobs(self):
        total = 0
        for job, mnmx in self.JOBS.items():
            num = len(self.workers[job])
            if num < mnmx[0]:
                total += mnmx[0] - num
        return total

    def new_job(self):
        required = []
        desired = []
        always_hiring = []
        for job, mnmx in self.JOBS.items():
            num = len(self.workers[job])
            if num < mnmx[0]:
                required.append((job, (mnmx[0] - num) / mnmx[0]))
            if mnmx[1] is None:
                always_hiring.append((job, num))
            # if none this crashes, so leave above
            elif num < mnmx[1]:
                desired.append((job, (mnmx[1] - num) / mnmx[1]))
        required = sorted(required, key=lambda x: 1, reverse=True)
        desired = sorted(desired, key=lambda x: 1, reverse=True)
        # least jobs goes to front
        always_hiring = sorted(always_hiring, key=lambda x: 1)
        if required:
            return required[0][0]
        if desired:
            # a third of the time they go to mine/quarry/forestry/pier/etc?
            if always_hiring and uniform(0, 1) < (1 / 3):
                return always_hiring[0][0]
            return desired[0][0]
        return None

    def hire_worker(self, npc):
        job_type = self.new_job()
        if job_type is None:
            return None
        if not npc.can_work():
            return None
        self.workers.add(job_type, npc)
        job = job_type(wealth=self.wealth, location=self)
        npc.job = job
        self.jobs.append(job)
        return job

    @classmethod
    def rand(cls, **kwargs):
        return choice(cls.filter(**kwargs))

    @classmethod
    def check_conditions(cls, bld, wealth=None, water=None, military=None,
                         industrial=None):
        if isinstance(bld, Building):
            bld = bld.__class__
        if wealth:
            if bld.LEVEL > wealth:
                return False
        if water is not None:
            if bld.WATER != water:
                return False
        if military is not None:
            if bld.MILITARY != military:
                return False
        if industrial is not None:
            if bld.INDUSTRIAL != industrial:
                return False
        return True

    @classmethod
    def filter(cls, **kwargs):
        return [
            x for x in cls.get_buildings()
            if cls.check_conditions(x, **kwargs)
        ]

    @classmethod
    def get_buildings(cls):
        return MetaBuilding.SHOPS.values()

    @classmethod
    def get_building(cls, name):
        return MetaBuilding.SHOPS[name]

    def __repr__(self):
        title = '{name}[{owner}]'.format(
            name=self.NAME,
            owner=self.owner.name,
        )
        s = []
        for job, workers in self.workers.items():
            s.append('#{}={}'.format(job.NAME, len(workers)))
        s = ', '.join(s)
        return '{}({})'.format(title, s)

    def dump(self):
        workers = ''
        for job, works in self.workers.items():
            for work in works:
                workers += '{jobid} - {worker!r} {workerid}\n'.format(
                    jobid=work.job.idstr,
                    worker=work,
                    workerid=work.idstr,
                )
        return '''{name}
ID: {idstr}
Owner: {owner!r}
Owner ID: {ownerid}
Workers:\n{workers}
'''.format(
            name=self.NAME,
            idstr=self.idstr,
            owner=self.owner,
            ownerid=self.owner.idstr,
            workers=workers,
        )


class BakeryBuilding(Building):
    NAME = 'bakery'
    LEVEL = 1
    COST = 2000
    JOBS = {BakerJob: (1, 4)}


class BlacksmithBuilding(Building):
    NAME = 'blacksmith'
    LEVEL = 1
    COST = 3000
    JOBS = {BlacksmithJob: (1, 4), ArmorerJob: (0, 2)}


class BowyerBuilding(Building):
    NAME = 'bowyer'
    LEVEL = 1
    JOBS = {BowyerJob: (1, 4), FletcherJob: (1, 4)}
    COST = 3000


class ArmorerBuilding(Building):
    NAME = 'armorer'
    LEVEL = 2
    JOBS = {ArmorerJob: (1, 4), BlacksmithJob: (0, 4)}
    COST = 6000


class AtilliatorJob(Building):
    NAME = 'atilliator'
    LEVEL = 2
    JOBS = {AtilliatorJob: (1, 4), BowyerJob: (0, 4), FletcherJob: (1, 4)}
    COST = 6000


class ButcherBuilding(Building):
    NAME = 'butchery'
    LEVEL = 1
    JOBS = {ButcherJob: (1, 4)}
    COST = 2000


class TailorBuilding(Building):
    NAME = 'tailor'
    LEVEL = 1
    JOBS = {
        TailorJob: (1, 4),
    }
    COST = 3000


class ClothierBuilding(Building):
    NAME = 'clothier'
    LEVEL = 1
    JOBS = {
        ClothierJob: (1, 4),
        ShoemakerJob: (0, 2),
        SpinsterJob: (0, 4),
        WeaverJob: (0, 2),
        TailorJob: (0, 2),
    }
    COST = 3000


class PotteryBuilding(Building):
    NAME = 'potter'
    LEVEL = 1
    JOBS = {PotterJob: (1, 4)}
    COST = 2000


class FishBuilding(Building):
    NAME = 'fishmonger'
    LEVEL = 1
    WATER = True
    JOBS = {FishermanJob: (1, 4)}
    COST = 2000


class ProduceBuilding(Building):
    NAME = 'produce'
    LEVEL = 1
    JOBS = {FarmerJob: (1, 4)}
    COST = 1500


class CarpentryBuilding(Building):
    NAME = 'carpenter'
    LEVEL = 1
    JOBS = {CarpenterJob: (1, 4)}
    COST = 2500


class ApothecaryBuilding(Building):
    NAME = 'apothecary'
    LEVEL = 2
    JOBS = {
        ApothecaryJob: (1, 4),
        HerbalistJob: (1, 4),
    }
    COST = 5000


class CandleBuilding(Building):
    NAME = 'candlemaker'
    LEVEL = 2
    JOBS = {CandlemakerJob: (1, 4)}
    COST = 5000


class LibraryBuilding(Building):
    NAME = 'library'
    LEVEL = 2
    JOBS = {LibrarianJob: (1, 12), ScribeJob: (0, 8)}
    COST = 8000


class TavernBuilding(Building):
    NAME = 'tavern'
    LEVEL = 2
    JOBS = {BartenderJob: (1, 4), CookJob: (1, 3), ServerJob: (1, 3)}
    COST = 7000


class InnBuilding(Building):
    NAME = 'inn'
    LEVEL = 2
    JOBS = {BartenderJob: (1, 8), CookJob: (1, 4), ServerJob: (1, 6)}
    COST = 10000


class PierTavernBuilding(Building):
    NAME = 'waterside-tavern'
    LEVEL = 1
    JOBS = {BartenderJob: (1, 4), CookJob: (1, 3), ServerJob: (1, 3)}
    WATER = True
    COST = 7500


class ArtBuilding(Building):
    NAME = 'gallery'
    LEVEL = 3
    JOBS = {ArtistJob: (1, 4)}
    COST = 10000


class BankBuilding(Building):
    NAME = 'bank'
    LEVEL = 3
    JOBS = {MoneylenderJob: (1, 4), ClerkJob: (1, 8)}
    COST = 15000


class BarberBuilding(Building):
    NAME = 'barbershop'
    LEVEL = 2
    JOBS = {BarberJob: (1, 4)}
    COST = 5000


class QuarryBuilding(Building):
    NAME = 'quarry'
    LEVEL = 1
    JOBS = {QuarrymanJob: (8, None)}
    INDUSTRIAL = True
    COST = 25000


class SawmillBuilding(Building):
    NAME = 'sawmill'
    LEVEL = 1
    JOBS = {ForesterJob: (8, None)}
    INDUSTRIAL = True
    COST = 25000


class MineBuilding(Building):
    NAME = 'mine'
    LEVEL = 1
    JOBS = {MinerJob: (8, None)}
    INDUSTRIAL = True
    COST = 25000


class PierBuilding(Building):
    NAME = 'pier'
    LEVEL = 1
    WATER = True
    JOBS = {
        FishermanJob: (8, None),
        SailorJob: (4, None),
        ShipCaptainJob: (1, None),
    }
    INDUSTRIAL = True
    COST = 25000


class JewelryBuilding(Building):
    NAME = 'jeweler'
    LEVEL = 2
    JOBS = {JewelerJob: (1, 4)}
    COST = 8000


class MasonryBuilding(Building):
    NAME = 'masonry'
    LEVEL = 1
    JOBS = {MasonJob: (1, 4)}
    COST = 1500


class HatmakerBuilding(Building):
    NAME = 'hatmaker'
    LEVEL = 2
    JOBS = {HatmakerJob: (1, 4)}
    COST = 3000


class LocksmithBuilding(Building):
    NAME = 'locksmith'
    LEVEL = 2
    JOBS = {LocksmithJob: (1, 4)}
    COST = 4000


class RooferBuilding(Building):
    NAME = 'roofer'
    LEVEL = 1
    JOBS = {RooferJob: (1, 4)}
    COST = 2000


class TanneryBuilding(Building):
    NAME = 'tanner'
    LEVEL = 1
    JOBS = {TannerJob: (1, 4)}
    COST = 2000


class RugmakerBuilding(Building):
    NAME = 'rugmaker'
    LEVEL = 3
    JOBS = {RugmakerJob: (1, 6)}
    COST = 7000
