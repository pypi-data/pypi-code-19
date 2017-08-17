
import pandas as pd
from heapq import nsmallest

from examscanuiuc.scan.constants import INFTY
from examscanuiuc.scan.errors import ScoreReadError

def change_transpose_distance(s1, s2):
	''' Return the minimal number of changes and transpositions needed to get from s1 to s2. '''
	n = max(len(s1), len(s2))
	s1, s2 = s1.rjust(n, '0'), s2.rjust(n, '0')
	
	score = [0]
	for i in range(len(s1)):
		cost = score[i] + (0 if s1[i] == s2[i] else 1)
		if i: cost = min(cost, score[i-1] + (1 if set(s1[i-1:i+1]) == set(s2[i-1:i+1]) else 2))
		score.append(cost)
	return score[-1]

# The old metric was just the number of changes
def change_distance(s1, s2):
	''' Return the minimal number of changes needed to get from s1 to s2. '''
	n = max(len(s1), len(s2))
	s1, s2 = s1.rjust(n, '0'), s2.rjust(n, '0')
	return len([x for x, y in zip(s1, s2) if x != y])

class Roster(object):
	def __init__(self, roster):
		self.roster = roster
	
	@classmethod
	def from_xlsx(self, path):
		roster = pd.read_excel(path, converters={'UIN': str}, skiprows=13)
		roster['name'] = roster['Student Name']
		roster = roster[roster['name'].notnull()]
		roster['netid'] = roster['Email'].apply(lambda x: x.split('@')[0])
		return Roster(roster[['name', 'netid', 'UIN']])
	
	@classmethod
	def from_csv(self, path):
		roster = pd.read_csv(path, converters={'UIN': str})
		return Roster(roster[['name', 'netid', 'UIN']])
	
	@classmethod
	def from_file(self, path):
		for method in [Roster.from_csv, Roster.from_xlsx]:
			try:
				return method(path)
			except:
				pass
		raise TypeError('Cannot open %s' % path)
	
	def match(self, uin):
		matches = self.roster[self.roster.UIN==uin]
		if len(matches) == 0:
			num_matching_digits = self.roster.UIN.apply(lambda x: change_transpose_distance(x, uin))
			first, second = (nsmallest(2, num_matching_digits) + [INFTY, INFTY])[:2]
			if first <= 1 < second:
				return self.roster.iloc[num_matching_digits.idxmin()].copy()
		elif len(matches) == 1:
			return matches.iloc[0].copy()
		else:  # len(matches) > 1
			raise ValueError('Multiple students with UIN %s.' % uin)
		raise ScoreReadError('No close match to %d in roster' % uin)

