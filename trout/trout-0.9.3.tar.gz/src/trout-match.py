#!/usr/bin/python

import sys
import glob

### Check command line arguments

if len(sys.argv) is not 2:
	print 'usage:	trout-match <sketch_dir>'
        print '             only *.trout.sketch are used'
	exit(1);


### Read in sketch data from files

file_names = []
data = []

sketches = glob.glob(sys.argv[1]+"*.trout.sketch");

for sketch in sketches:
	f = open(sketch,'r')
	i = 0
	for line in f:
		i += 1
		file_names.append( line.split(':')[0] );
		data_list = (line.split(':')[1]).split()[:]  ## enter number of markers after :
		data.append ( " ".join(data_list) );
	if i is not 1:
		print "trout-match: multiple sketches written to file "+sketch
		exit(1)
	f.close()



### Compute sketch data into matrix

files_column = []
for row in data:
	files_column.append(row.split())

for col in range(0,len(row)):
	count = 0
	for f in files_column:
		if f[col]=="1":
			count += 1
	if count < (.1*len(file_names)):
		print 'kmer: '+str(col)+'\tNOT FOUND in 90% of sketches: '+str(count)
	if count > (.9*len(file_names)):
		print 'kmer: '+str(col)+'\tFOUND in 90% of sketches: '+str(count)
