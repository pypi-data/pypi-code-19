import sys
import os
import shutil
import glob

def find():
					print("Please input the path to your folder excluding '/' beacuse i will put it by myself..so if your path is /sdcard .you put sdcard only.")
					a=input("where is your file or folder located ?")
					file = "/" + a
					os.chdir(file)
					


def remove():
				ans = input("Do you want to delete all the files? Y/N")
				if(ans == 'Y'):
						shutil.rmtree(file)
				else:
						bas = input("which file do you want to delete?")
						find = glob.glob(bas)
						if(find):
								print("Found {}".format(find))
								os.remove(bas)
								print("The file is deleted")
						else:
								print("File not found")
								print("Exiting now")
								sys.exit()


find()
remove()		
				
				