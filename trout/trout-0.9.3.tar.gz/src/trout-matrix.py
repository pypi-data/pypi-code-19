#!/usr/bin/python

import sys
import glob

### Check command line arguments

if len(sys.argv) is not 2:
	print 'usage:	trout-matrix <sketch_dir>'
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
		print "error: multiple sketches written to file "+sketch
		exit(1)
	f.close()



### Compute sketch data into matrix

numFiles = len(file_names)
matrix = []  # list of rows; each row of matrix is a list of values

for i in range(numFiles): # loops through all of the files' data
	matrix.append([])     # append empty row to matrix
	for j in range(numFiles):  # loops through all files for comparision
		# matrix is 0 for the same elements
		if i==j:
			matrix[i].append(0.0)
			continue

		# value has already been computed
		if j<i:
			#matrix[i].append( matrix[j][i] )
			matrix[i].append(' ')
			continue
		
		# loop through both data sets to determine diff/total ratio
		set1 = data[i].split()
		set2 = data[j].split()

		index = 0
		diff = 0
		for bit in set1:
			if set1[index]!=set2[index]:
				diff += 1
			index += 1

		ratio = diff / float(index)  # index = total
		matrix[i].append( float(ratio))



### Print Results

for i in range(numFiles):
	for j in range(numFiles):
		if isinstance(matrix[i][j], float):
			print file_names[i]+" "+file_names[j]+" "+str(matrix[i][j])


'''
# creates matrix like sructure
print "\t",
for name in file_names:
	print name+"\t",

print ""

i=0
for row in matrix:
	print file_names[i]+"\t",
	for value in row:
		print str(value)+"\t",
	print ""
	i +=1

'''
