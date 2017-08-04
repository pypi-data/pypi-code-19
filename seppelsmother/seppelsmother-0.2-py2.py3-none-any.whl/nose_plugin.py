import logging

import time
from nose.plugins.cover import Coverage
from seppelsmother.control import SeppelSmother


log = logging.getLogger(__name__)


class SmotherNose(Coverage):
    name = "seppelsmother"

    def afterTest(self, test):
        self.coverInstance.stop()
        self.smother.save_context("%s:%s" % test.address()[1:3])

    def beforeTest(self, test):

        # Save coverage from before first test as an unlabeled
        # context. This captures coverage during import.
        if self.first_test:
            self.coverInstance.stop()
            self.smother.save_context("")
            self.first_test = False

        self.smother.start()

    def configure(self, options, conf):
        super(SmotherNose, self).configure(options, conf)
        if self.enabled:
            self.first_test = True
            self.output = options.smother_output
            self.smother = SeppelSmother(self.coverInstance)

    def options(self, parser, env):
        super(Coverage, self).options(parser, env)
        parser.add_option("--seppelsmother-package", action="append",
                          default=env.get('NOSE_COVER_PACKAGE'),
                          metavar="PACKAGE",
                          dest="cover_packages",
                          help="Restrict coverage output to selected packages "
                          "[NOSE_COVER_PACKAGE]")
        parser.add_option("--seppelsmother-erase", action="store_true",
                          default=env.get('NOSE_COVER_ERASE'),
                          dest="cover_erase",
                          help="Erase previously collected coverage "
                          "statistics before run")
        parser.add_option("--seppelsmother-output", action="store",
                          default=env.get('NOSE_SMOTHER_OUTPUT', '.seppelsmother'),
                          dest="smother_output",
                          help="Location of output file")

    def report(self, stream):
        self.smother.write(self.output)
