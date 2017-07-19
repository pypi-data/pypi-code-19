# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from .resources import VALID_PARAMS

SYSTEM_SGE = "SGE"
SYSTEM_GE = "GE"
SYSTEM_LSF = "LSF"
SYSTEM_SLURM = "SLURM"


class BaseSystem(object):
    __metaclass__ = ABCMeta

    def __str__(self):
        return self.__class__.__name__

    @staticmethod
    def _prepare_resources(res, res_map):
        output = []

        for name in VALID_PARAMS:
            if name in res:
                output.append(res_map[name].format(res[name]))

        return ' '.join(output)

    def is_slurm(self):
        return False

    def is_sge(self):
        return False

    def is_lsf(self):
        return False

    @abstractmethod
    def native_resources(self, resources):
        return resources


class SystemSGE(BaseSystem):
    def is_sge(self):
        return True

    def native_resources(self, resources):
        res = super(SystemSGE, self).native_resources(resources)
        # On SGE memory needs to be provided per/slot or core
        if "mem" in res:
            cpu = res.get("cpu", 1)
            res["mem"] = int(res["mem"] / cpu)

        res_map = {
            "cpu": "-pe smp {0}",
            "mem": "-l h_vmem={0}M",
            "queue": "-q {0}",
        }
        return self._prepare_resources(res, res_map)


class SystemLSF(BaseSystem):
    def is_lsf(self):
        return True

    def native_resources(self, resources):
        res = super(SystemLSF, self).native_resources(resources)
        res_map = {
            "cpu": "-n {0}",
            "mem": '-M {0} -R "select[(mem>={0})] rusage[mem={0}] span[hosts=1]"',
            "queue": "-q {0}",
        }
        return self._prepare_resources(res, res_map)


class SystemSLURM(BaseSystem):
    def is_slurm(self):
        return True

    def native_resources(self, resources):
        res = super(SystemSLURM, self).native_resources(resources)
        # On SLURM mem needs to be provided per CPU and we use MB so mem can be an integer
        if "mem" in res:
            cpu = res.get("cpu", 1)
            res["mem"] = int(res["mem"] / cpu)

        res_map = {
            "cpu": "--ntasks={0}",
            "mem": "--mem-per-cpu={0}",
            "queue": "--partition={0}",
        }
        return self._prepare_resources(res, res_map)


# vim: ai sts=4 et sw=4
