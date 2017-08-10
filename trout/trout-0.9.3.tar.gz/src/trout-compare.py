#!/usr/bin/python

import sys

# Check arguments
if len(sys.argv) is not 3:
	print 'usage:	trout-compare <distance_matrix> <distance_matrix>'
	exit(1);

distfile1 = open(sys.argv[1],'r')
distfile2 = open(sys.argv[2],'r')

# Distance's of 1 minus distance's of 2
'''
Distance matrix expected in following format:

FASTQ1 FASTQ2 0.0
...

'''

distance = {}

for line in distfile1:
	field = line.split()
	if field[0] < field[1]:
		if not field[0] in distance:
			distance[field[0]] = {}
		distance[field[0]][field[1]] = float(field[2])
	else:
		if not field[1] in distance:
			distance[field[1]] = {}
		distance[field[1]][field[0]] = float(field[2])
	
for line in distfile2:
	field = line.split()
	if field[0] > field[1]:
		field[0], field[1] = field[1], field[0]
	
	if field[0] in distance and field[1] in distance[field[0]]:
		distance[field[0]][field[1]] = float(distance[field[0]][field[1]] - float(field[2]))
	else:
		print 'trout-compare: Incompatible Distance Matrices'
		print field[0] +' '+field[1]
		sys.exit(1)


for fileA in sorted(distance):
	for fileB in sorted(distance[fileA]):
		print fileA+' '+fileB+' '+str(distance[fileA][fileB])

