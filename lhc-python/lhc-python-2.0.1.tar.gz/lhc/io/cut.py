import re

from collections import Counter


class CodonUsageTable(Counter):

    REGX = re.compile(r'(?P<codon>[ACGTU]{3})\s+(?P<frq>\d+\.\d+)\s+\((\s*\d+)\)')

    def __init__(self, fname):
        super(CodonUsageTable, self).__init__()
        with open(fname, encoding='utf-8') as fileobj:
            for line in fileobj:
                matches = self.REGX.findall(line)
                for match in matches:
                    self[match[0].lower().replace('u', 't')] =\
                        float(match[2])
