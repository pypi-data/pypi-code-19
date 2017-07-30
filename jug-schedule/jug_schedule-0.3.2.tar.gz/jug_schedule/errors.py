# -*- coding: utf-8 -*-


class UnsupportedDRMAAVersion(Exception):
    def __init__(self, ver):
        self.ver = ver

    def __str__(self):
        return "We only support DRMAA version 1.x - You have {}".format(self.ver)


class UnrecognizedQueueSystem(Exception):
    def __init__(self, contact, info, impl, version):
        self.args = (contact, info, impl, version)

    def __str__(self):
        return """Failed to recognize the current system.

Please report to the author(s) of jug_schedule and include the following

Contact : {0}
DRM Info: {1}
DRMAA   : {2}
Version : {3}
""".format(*self.args)


class JobFailed(Exception):
    "Raised when a jug job exits with non-zero or aborted state"
    pass


# vim: ai sts=4 et sw=4
