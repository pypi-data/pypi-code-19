#!/usr/bin/env python

import unittest

from netutils_linux_monitoring.softnet_stat import SoftnetStat


class SoftnetStatTests(unittest.TestCase):
    first = """
    9d3cbd5e 00000000 0000004d 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    301350a8 00000000 00000025 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    2102d7a3 00000000 00000021 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    1d208d3b 00000000 00000021 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    6ba194e0 00000000 0000002b 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    25ef7e5f 00000000 0000001f 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    178ea501 00000000 0000001e 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    16882427 00000000 00000029 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    """

    second = """
    9d3cebfe 00000000 0000004d 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    30135354 00000000 00000025 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    2102d995 00000000 00000021 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    1d208e70 00000000 00000021 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    6ba1984a 00000000 0000002b 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    25ef7f6f 00000000 0000001f 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    178ed754 00000000 0000001e 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    168824ff 00000000 00000029 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    """

    def test_delta(self):
        __first = [SoftnetStat().parse_string(row, cpu) for cpu, row in enumerate(self.first.strip().split('\n'))]
        __second = [SoftnetStat().parse_string(row, cpu) for cpu, row in enumerate(self.second.strip().split('\n'))]
        delta = __second[0] - __first[0]
        data = [0, 11936, 0, 0, 0, 0]
        expected = SoftnetStat().parse_list(data)
        self.assertEqual(delta, expected)


if __name__ == '__main__':
    unittest.main()
