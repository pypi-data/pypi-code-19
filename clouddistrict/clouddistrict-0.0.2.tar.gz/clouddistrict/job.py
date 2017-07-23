'''
towniesim.job
=============
'''
from random import gauss


class MetaJob(type):
    JOBS = {}

    def __new__(cls, name, bases, dct):
        if name == 'Job':
            return super(MetaJob, cls).__new__(cls, name, bases, dct)
        for key in ('CAN_OWN', 'SUPERVISOR', 'MILITARY', 'WATER'):
            dct[key] = dct.get(key, False)
        for key in ('LEVEL',):
            dct[key] = dct.get(key, 1)
        new_cls = super(MetaJob, cls).__new__(cls, name, bases, dct)
        MetaJob.JOBS[dct['NAME']] = new_cls
        return new_cls


class Job(metaclass=MetaJob):
    COUNT = 0
    OBJS = {}

    @classmethod
    def next(cls):
        cls.COUNT += 1
        return cls.COUNT

    def __init__(self, wealth=None, location=None, pay=None):
        pay = pay or self.WAGE
        self.wealth = wealth or self.LEVEL
        self.pay = int(max(gauss(pay, pay / 10), 2))
        self.location = location
        self.id = Job.next()
        self.idstr = '{}#{}'.format(self.NAME, self.id)
        Job.OBJS[self.idstr] = self

    @property
    def location(self):
        from .building import Building
        if self._location is None:
            return None
        return Building.OBJS[self._location]

    @location.setter
    def location(self, val):
        from .building import Building
        if isinstance(val, Building):
            self._location = val.idstr
        else:
            self._location = val

    @classmethod
    def get_jobs(cls):
        return MetaJob.JOBS.values()

    @classmethod
    def get_job(cls, name):
        return MetaJob.JOBS[name]

    def __repr__(self):
        return '{name}L{wealth}[{pay}]'.format(
            name=self.NAME.title(), wealth=self.wealth, pay=self.pay
        )


class ApothecaryJob(Job):
    NAME = 'apothecary'
    WAGE = 40
    CAN_OWN = True
    LEVEL = 1


class ButcherJob(Job):
    NAME = 'butcher'
    WAGE = 10
    CAN_OWN = True
    LEVEL = 1


class HerbalistJob(Job):
    NAME = 'herbalist'
    WAGE = 40
    CAN_OWN = True
    LEVEL = 1


class ClothierJob(Job):
    NAME = 'clothier'
    WAGE = 30
    CAN_OWN = True
    LEVEL = 1


class ShoemakerJob(Job):
    NAME = 'shoemaker'
    WAGE = 30
    CAN_OWN = True
    LEVEL = 1


class SpinsterJob(Job):
    NAME = 'spinster'
    WAGE = 5
    LEVEL = 1


class BakerJob(Job):
    NAME = 'baker'
    WAGE = 20
    CAN_OWN = True
    LEVEL = 1


class BarberJob(Job):
    NAME = 'barber'
    WAGE = 10
    CAN_OWN = True
    LEVEL = 2


class BlacksmithJob(Job):
    NAME = 'blacksmith'
    WAGE = 100
    CAN_OWN = True
    LEVEL = 1


class ArmorerJob(Job):
    NAME = 'armorer'
    WAGE = 100
    CAN_OWN = True
    LEVEL = 1


class BowyerJob(Job):
    NAME = 'bowyer'
    WAGE = 50
    CAN_OWN = True
    LEVEL = 1


class AtilliatorJob(Job):
    NAME = 'atilliator'
    WAGE = 80
    CAN_OWN = True
    LEVEL = 1


class FletcherJob(Job):
    NAME = 'fletcher'
    WAGE = 20
    LEVEL = 1


class SailorJob(Job):
    NAME = 'sailor'
    WAGE = 5
    WATER = True
    LEVEL = 1


class MessengerJob(Job):
    NAME = 'messenger'
    WAGE = 2
    LEVEL = 2


class MinerJob(Job):
    NAME = 'miner'
    WAGE = 10
    LEVEL = 1
    INDUSTRIAL = True


class LaborerJob(Job):
    NAME = 'laborer'
    WAGE = 5
    LEVEL = 1


class CookJob(Job):
    NAME = 'cook'
    WAGE = 40
    CAN_OWN = True
    LEVEL = 1


class ServerJob(Job):
    NAME = 'server'
    WAGE = 3
    LEVEL = 1


class ArtistJob(Job):
    NAME = 'artist'
    WAGE = 50
    CAN_OWN = True
    LEVEL = 3


class CandlemakerJob(Job):
    NAME = 'candlemaker'
    WAGE = 10
    CAN_OWN = True
    LEVEL = 1


class CarpenterJob(Job):
    NAME = 'carpenter'
    WAGE = 60
    CAN_OWN = True
    LEVEL = 1


class MoneylenderJob(Job):
    NAME = 'moneylender'
    WAGE = 100
    CAN_OWN = True
    LEVEL = 3


class ClerkJob(Job):
    NAME = 'clerk'
    WAGE = 50
    LEVEL = 3


class PotterJob(Job):
    NAME = 'potter'
    WAGE = 20
    CAN_OWN = True
    LEVEL = 1


class LibrarianJob(Job):
    NAME = 'librarian'
    WAGE = 50
    CAN_OWN = True
    LEVEL = 2


class ScribeJob(Job):
    NAME = 'scribe'
    WAGE = 50
    CAN_OWN = True
    LEVEL = 2


class JewelerJob(Job):
    NAME = 'jeweler'
    WAGE = 100
    CAN_OWN = True
    LEVEL = 3


class MasonJob(Job):
    NAME = 'mason'
    WAGE = 20
    CAN_OWN = True
    LEVEL = 1


class GuardJob(Job):
    NAME = 'guard'
    WAGE = 20
    MILITARY = True
    LEVEL = 2


class GuardCaptainJob(Job):
    NAME = 'guardcaptain'
    WAGE = 100
    SUPERVISOR = True
    MILITARY = True
    LEVEL = 3


class ShipCaptainJob(Job):
    NAME = 'shipcaptain'
    WAGE = 100
    SUPERVISOR = True
    WATER = True
    LEVEL = 2


class FishermanJob(Job):
    NAME = 'fisherman'
    WAGE = 10
    WATER = True
    LEVEL = 1
    INDUSTRIAL = True


class FarmerJob(Job):
    NAME = 'farmer'
    WAGE = 10
    CAN_OWN = True
    LEVEL = 1
    INDUSTRIAL = True


class BartenderJob(Job):
    NAME = 'bartender'
    WAGE = 20
    CAN_OWN = True
    LEVEL = 1


class ForesterJob(Job):
    NAME = 'forester'
    WAGE = 10
    CAN_OWN = True
    LEVEL = 1
    INDUSTRIAL = True


class QuarrymanJob(Job):
    NAME = 'quarryman'
    WAGE = 10
    CAN_OWN = True
    LEVEL = 1
    INDUSTRIAL = True


class TailorJob(Job):
    NAME = 'tailor'
    WAGE = 30
    CAN_OWN = True
    LEVEL = 1


class WeaverJob(Job):
    NAME = 'weaver'
    WAGE = 10
    CAN_OWN = True
    LEVEL = 1


class HatmakerJob(Job):
    NAME = 'hatmaker'
    WAGE = 30
    CAN_OWN = True
    LEVEL = 2


class LocksmithJob(Job):
    NAME = 'locksmith'
    WAGE = 30
    CAN_OWN = True
    LEVEL = 2


class RooferJob(Job):
    NAME = 'roofer'
    WAGE = 20
    CAN_OWN = True
    LEVEL = 2


class TannerJob(Job):
    NAME = 'tanner'
    WAGE = 10
    CAN_OWN = True
    LEVEL = 1


class RugmakerJob(Job):
    NAME = 'rugmaker'
    WAGE = 50
    CAN_OWN = True
    LEVEL = 3
