import os
import time

print ("To run this program you need to install the Pi-Plates libraries.")
print ("Do so by executing the following from the command line:")
print ("'sudo pip install Pi-Plates' for Python 2 programming and")
print ("'sudo pip3 install Pi-Plates' for Python 3 programming")
response=raw_input("Would you like to install these now? (y/n)")
if (response.lower()=='y'):
    os.system("sudo pip install Pi-Plates")
    os.system("sudo pip3 install Pi-Plates")
    print('Pi-Plates modules installed. Please restart the program.')
print('This window will close in 5 seconds...')
time.sleep(5)
