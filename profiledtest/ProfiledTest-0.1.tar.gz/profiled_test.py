import cProfile
import pstats

class ProfiledTest(object):
    def setUp(self):
        '''Start before any tests'''
        super(ProfiledTest, self).setUp()
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        print("\n<<<---")

    def tearDown(self):
        """Finish after any test"""
        super(ProfiledTest, self).tearDown()
        stats = pstats.Stats(self.profiler)
        stats.strip_dirs()
        stats.sort_stats('cumtime')
        stats.print_stats()
        print("\n--->>>")

