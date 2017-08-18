from __future__ import absolute_import, print_function, unicode_literals


class JobRunner(object):

    def run(self, job, config):
        job.setup()
        job.run()
        job.teardown()
