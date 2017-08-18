from __future__ import absolute_import, print_function, unicode_literals

from dojo.job import Job
from dojo.vanilla.stores.google_storage import VanillaGoogleStorage

from .runners.direct import DirectMLEngineRunner
from .runners.cloud import CloudMLEngineRunner


class GoogleCloudMLEngineModel(Job):

    RUNNERS = {
        'direct': DirectMLEngineRunner,
        'cloud': CloudMLEngineRunner
    }

    STORES = {
        'gs': VanillaGoogleStorage
    }

    def run(self):
        pass
