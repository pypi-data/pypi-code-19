import datetime
import random

from tests.live import testlib


class TestUserId(object):
    TAGS_PER = 10

    def test_00(self, fw, state_map):
        fw.userid.clear_registered_ip()

    def test_01(self, fw, state_map):
        state = state_map.setdefault(fw)
        state.data = [
            (testlib.random_ip(), [testlib.random_name()
                                   for x in range(self.TAGS_PER)])
            for x in range(10)]

        for ip, tags in state.data:
            fw.userid.register(ip, tags)

        ans = fw.userid.get_registered_ip()
        assert len(ans) == len(state.data)

        for key, tags in ans.items():
            for state_key, state_tags in state.data:
                if state_key != key:
                    continue
                assert set(state_tags) == set(tags)

    def test_02(self, fw, state_map):
        state = state_map.setdefault(fw)

        for ip, tags in state.data:
            fw.userid.unregister(ip, tags)

        assert len(fw.userid.get_registered_ip()) == 0

    def test_03_looper(self, fw, state_map):
        ips = [testlib.random_ip() for x in range(10)]
        tags = [testlib.random_name() for x in range(10)]
        tag_set = set(tags)
        one_ip = random.choice(ips)

        print('ips: {0}'.format(ips))
        print('tags: {0}'.format(tags))
        assert len(fw.userid.get_registered_ip()) == 0

        for num in range(1, 6):
            print('Loop {0}...'.format(num))

            # Register stuff
            fw.userid.register(ips, tags)
            ans = fw.userid.get_registered_ip()
            for ip in ips:
                assert ip in ans
                assert set(ans[ip]) == set(tag_set)

            # Unregister one at random
            first_selection = random.choice(tags)
            print('first_selection = {0}'.format(first_selection))
            fw.userid.unregister(ips, first_selection)
            ans = fw.userid.get_registered_ip()
            assert len(ans[one_ip]) == 9

            # Unregister one more at random
            second_selection = first_selection
            while second_selection == first_selection:
                second_selection = random.choice(tags)
            print('second_selection = {0}'.format(second_selection))
            fw.userid.unregister(ips, second_selection)
            ans = fw.userid.get_registered_ip()
            assert len(ans[one_ip]) == 8

            # Unregister everything, which includes already deleted things
            fw.userid.unregister(ips, tags)
            ans = fw.userid.get_registered_ip()
            assert ans == {}
