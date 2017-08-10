import os
import glob
import sys

def path_validity(path):
	""" Verifies if a given OS path already exists, if it is writtable or if it impossible to write at this location. Works for both files and directories, 
	by specifying the objecttype (dir, file)"""
	valid = False
	if os.path.exists(path):
		valid = True
	elif os.access(os.path.dirname(path), os.W_OK):
		valid = True
	
	return valid


def outfile_verif(outfile):

	if os.path.isfile(outfile) == True: #Output file verification. 
		statement = "Output file %s already exists. Overwrite? (Y/N)" % outfile
		valid_answer = False
		while valid_answer == False:
			answer = raw_input(statement)
			if answer.upper() == "Y":
				print "Overwriting previous %s file..." % outfile
				return outfile
				valid_answer = True
			elif answer.upper() == "N":
				valid_answer = True
				valid_answer2 = False
				while valid_answer2 == False:
					ans2 = raw_input("Append number to current output file? (Y/N) ")
					if ans2.upper() == "Y":
						globfile = outfile.replace(".txt", "_*.txt")
						basic = outfile.replace(".txt", "")
						
						globlist = []
						if len(glob.glob(globfile)) == 0:
							outfile = basic + "_1.txt"
						else:
							for i in glob.glob(globfile):
								glob_instance = i
								glob_instance = glob_instance.replace(".txt", "").replace(basic,"").replace("_","")
								globlist.append(int(glob_instance))
								globlist.sort()

							outfile = basic + "_" + str(globlist.pop()+1) +".txt"

						valid_answer2 = True
						print "Renaming file to %s\n" % outfile
						return outfile
					elif ans2.upper() == "N":
						print "Not renaming file. Aborting..."
						sys.exit()
					else:
						print "%s is not a valid answer. Try again...\n" % ans2
						
			else:
				print "%s is not a valid answer. Try again\n" % answer
				