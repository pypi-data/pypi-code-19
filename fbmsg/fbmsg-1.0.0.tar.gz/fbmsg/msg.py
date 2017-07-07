import fbchat 
from getpass import getpass
from fbchat import Client
from fbchat.models import *
def msg_to_usr():
	
	n=raw_input("No. of friends you would like to interact: \nif single then enter 1 for multiple choose 2\n")
	
	while 1:
		if n==1:
			name=str(raw_input("Name of usr: "))
			users = client.searchForUsers(name)
			msg=raw_input("Enter ur msg: ")
			sent=client.sendMessage(msg, thread_id=users[0].uid, thread_type=ThreadType.USER)
			if sent:
        			print("Message sent successfully!")
			
		else:
			name=list(map(str,raw_input("Enter(comma separated) Name of friends: \n").split(',')))
			msg=raw_input("Enter ur msg: ")
			for naam in name:
				users = client.searchForUsers(naam)
				sent=client.sendMessage(msg, thread_id=users[0].uid, thread_type=ThreadType.USER)
				if sent:
        				print("Message sent successfully!")
				
		status=raw_input("do you want to continue or logout: \nEnter 1 to contine and \n 2 for logout\n")
		if(status==1):
			continue
		else:
			break
	
	
#def to interact with grp
				
def msg_to_grp():
	for i in xrange(n):
		name=str(raw_input("Name of grp: "))
		grps = client.searchForGroups(name)
		msg=raw_input("Enter ur msg: \n")
		sent=client.sendMessage( msg, thread_id=grps[0].gid, thread_type=ThreadType.GROUP)
	
#login. Enter your credentials in place of email and password.

username=raw_input("Username: ")
#password=raw_input("Password: ")
client = Client(username,getpass())
#client=client('<username' , '<password>' , cookies)


#choose the option to interact in a grp or with usr.

print("Let's start the fun....."+'\n')
print("wanna play with usr's or grp "+'\n'+ "choose 1 for usr and 2 for grp:")


n=int(raw_input())

if n==1:
	msg_to_usr()
else:
	msg_to_grp()
		
#script created by 
#himanshu chouhan(hchouhan3654@gmail.com)
