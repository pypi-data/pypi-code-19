

def subset_singlechoice_recurse(myset):
	if len(myset) == 0:
		yield []
	else:
		a = myset.pop()
		tail = subset_singlechoice_recurse(myset.difference({a}))
		for othersets in tail:
			# Either: a is alone
			yield [[{a}] + othersets]
			# Or: a is in one of the sets
			for otherset in othersets:
				yield [otherset.union([a])] + [otherset2 for otherset2 in othersets if otherset2 != otherset]


def subset_singlechoice_recurse(mylist):
	if len(mylist) == 0:
		yield []
	else:
		a = mylist[0]
		tail = subset_singlechoice_recurse(mylist[1:])
		for setsolution in tail:
			# Either: a is alone
			yield [[a]] + setsolution
			# Or: a is in one of the sets
			for set1 in setsolution:
				yield [[a] + set1] + [set2 for set2 in setsolution if set2 != set1]

import itertools

def combine_multichoice_recurse(mylist, existing_sets):
	if len(mylist) == 0:
		yield existing_sets
	else:
		a = mylist[0]
		tail = combine_multichoice_recurse(mylist[1:], existing_sets)
		for setsolution in tail:
			#print '    Xcombining', setsolution, 'with', a
			# Either create a new subset with only a
			yield [([a], False)] + setsolution
			# Or: a is in one of the sets, but none of the others must be in there
			for set1, free in setsolution:
				if free:
					yield [([a] + set1, False)] + [(set2, free2) for set2, free2 in setsolution if set2 != set1]

def subset_multichoice_recurse(superlist):
	if len(superlist) == 0:
		yield []
	else:
		a = superlist[0]
		tail = subset_multichoice_recurse(superlist[1:])
		# make cross-product of as and [tail + empty list]
		for setsolution in tail:
			#print 'combining', a, 'with', setsolution
			for setsolution in combine_multichoice_recurse(a, [(set1, True) for set1 in setsolution]):
				#print '-->', setsolution
				yield [set1 for set1, free in setsolution]

"""
print list(subset_singlechoice_recurse([1,2]))

print
print
print


print list(subset_singlechoice_recurse([1,2,3]))

print
print
print

print list(subset_singlechoice_recurse([1,2,3,4]))

print len(list(subset_singlechoice_recurse([1])))
print len(list(subset_singlechoice_recurse([1,2])))
print len(list(subset_singlechoice_recurse([1,2,3])))
print len(list(subset_singlechoice_recurse([1,2,3,4])))
print len(list(subset_singlechoice_recurse([1,2,3,4,5])))
"""

print list(subset_multichoice_recurse([['A1'],['B1', 'B2']]))

print
print
print


print list(subset_multichoice_recurse([['A1'],['B2','B3'], ['C4','C5']]))

print len(list(subset_multichoice_recurse([['A1'],['B2']])))
print len(list(subset_multichoice_recurse([['A1'],['B2','B3']])))
print len(list(subset_multichoice_recurse([['A1'],['B2','B3'], ['C4']])))
print len(list(subset_multichoice_recurse([['A1'],['B2','B3'], ['C4','C5']])))
print len(list(subset_multichoice_recurse([['A1'],['B2','B3'], ['C4','C5'], ['D6']])))
print len(list(subset_multichoice_recurse([['A1'],['B2','B3'], ['C4','C5'], ['D6','D7']])))

print len(list(subset_multichoice_recurse([['A1'],['B%d' % i for i in range(1, 20)]])))
print len(list(subset_multichoice_recurse([['A1'],['B%d' % i for i in range(1, 20)], ['C%d' % i for i in range(1, 20)]])))
print len(list(subset_multichoice_recurse([['A1'],['B%d' % i for i in range(1, 20)], ['C%d' % i for i in range(1, 20)],['D%d' % i for i in range(1, 20)]])))

