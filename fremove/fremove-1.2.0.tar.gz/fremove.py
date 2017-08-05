import sys
import os
import shutil
import glob

def find():
					a=input("Is the file to be removed in the same directory Y/N?")
					if(a == 'Y' or a == 'y'):
							b = input("Whats the filename?")
							c=glob.glob(b)
							if(c):
									os.remove(b)
									print("The file is deleted")
									sys.exit()
							else:
									print("File not found")
							
							
							
							
					
					print("\n")	
					print("\n")
					
					
					print("Please input the full path")
					a=input("where is your file or folder located ?")
					file = a
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
				
				