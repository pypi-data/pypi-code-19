import coverage


def pytest_addoption(parser):
    """Add options to control coverage."""

    group = parser.getgroup(
        'seppelsmother', 'seppelsmother reporting')
    group.addoption('--seppelsmother', action='append', default=[], metavar='path',
                    nargs='?', const=True, dest='seppelsmother_source',
                    help='measure coverage for filesystem path '
                    '(multi-allowed)')
    group.addoption('--seppelsmother-output', action='store', default='.seppelsmother',
                    help='output file for smother data. '
                         'default: .seppelsmother')


def pytest_configure(config):
    """Activate plugin if appropriate."""
    if config.getvalue('seppelsmother_source'):
        if not config.pluginmanager.hasplugin('_seppelsmother'):
            plugin = Plugin(config.option)
            config.pluginmanager.register(plugin, '_seppelsmother')


class Plugin(object):

    def __init__(self, options):
        self.coverage = coverage.coverage(
            source=options.seppelsmother_source,
        )

        # The unusual import statement placement is so that
        # smother's own test suite can measure coverage of
        # smother import statements
        self.coverage.start()
        from seppelsmother.control import SeppelSmother
        self.smother = SeppelSmother(self.coverage)

        self.output = options.seppelsmother_output
        self.first_test = True

    def pytest_runtest_setup(self, item):
        if self.first_test:
            self.first_test = False
            self.coverage.stop()
            self.smother.save_context("")
        self.smother.start()

    def pytest_runtest_teardown(self, item, nextitem):
        self.coverage.stop()
        self.smother.save_context(item.nodeid)

    def pytest_terminal_summary(self):
        self.smother.write(self.output)
