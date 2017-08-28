#!/usr/bin/python

try:
	import twitter;import sqlite3;from time import sleep, time;from sys import argv, platform;from os import system
except Exception, e:
	print "\033[91mError: {0}".format(e) + "\033[0m"

class Coloring:
	def __init__(self):
		self.green, self.bold, self.red, self.die = "\033[1m\033[92m", "\033[1m", "\033[91m", "\033[0m"

def banner():
	tm = time()
	pfrom = ""
	if "win" not in platform.lower():
		system('clear')
		pfrom = "Linux"
	else:
		system('cls')
		pfrom = "Windows"
	print COLOR.green + """
  _____                _     ___                    _    
 |_   _|_ __ _____ ___| |_  | __|__ _ _ ___ _ _  __(_)__ 
   | | \ V  V / -_) -_)  _| | _/ _ \ '_/ -_) ' \(_-< / _|
   |_|  \_/\_/\___\___|\__| |_|\___/_| \___|_||_/__/_\__|
   -------------------------------------------------------
   Author           :    Muhammad Adeel -> \033[91m@Chaudhary1337\033[92m
   Report Bugs      :    Chaudhary1337@gmail.com
   Tool Desc        :    Performing Tweet Analysis
   Execution Time   :    %s Seconds
   Current PlatForm :    %s OS
   -------------------------------------------------------
   Commands       :    help - forensic - change - stats
                  :    clear - exit
   -------------------------------------------------------
   """ %(time() - tm, pfrom) + COLOR.die

consumer_key = 'yZA8ABXinV6rQlICV3DNyKwHV'
consumer_secret = 'D1xMDf3NnDCcYtu5KRcwes8MzQbAWW4pPQHEYL2tHH0T70L9E1'
access_token = '1731498314-nPqsTsliicuwDmeBnZplnyM0ZYXR3TAnArZPhdR'
access_token_secret = '1Tu4TYpL5ASLOzAFBDqWH721ETxVJUdT8hKnczSLyvWcH'

api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token, access_token_secret=access_token_secret)

COLOR = Coloring()

def PerformAnalysis(tweetID):
	try:
		con = sqlite3.connect("tweets.db")
		con.execute('''
		create table if not exists tweets(
		tweetID varchar(50) PRIMARY KEY NOT NULL,
		tweetAuthor varchar(32) NOT NULL,
		Name varchar(50) NOT NULL,
		Location varchar(50) NOT NULL,
		TimeZone varchar(50) NOT NULL,
		RetweetCount varchar(50) NOT NULL,
		FavouritesCount varchar(32) NOT NULL,
		StatusCounts varchar(32) NOT NULL,
		CreatedAt varchar(50) NOT NULL,
		idCreatedAt varchar(50) NOT NULL,
		TweetText text NOT NULL,
		authorDescription text NOT NULL
		);''')
		cursor = con.execute("select * from tweets where tweetID=?",(str(tweetID),))
		data = cursor.fetchall()
		if(len(data) == 0):
			stats = api.GetStatus(tweetID)
			print COLOR.green + "\n\t--> Not Found in Database, Trying Live Api Search\n" + COLOR.die				
			con.execute("insert into tweets(tweetID, tweetAuthor, Name, Location, TimeZone, RetweetCount, FavouritesCount, StatusCounts, CreatedAt, idCreatedAt, TweetText, authorDescription) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",(str(tweetID), str(stats.user.screen_name), str(stats.user.name), str(stats.user.location), str(stats.user.time_zone), str(stats.retweet_count), str(stats.favorite_count), str(stats.user.statuses_count), str(stats.created_at), str(stats.user.created_at), str(stats.text), str(stats.user.description)))
			con.commit()
			con.close()
			print COLOR.green + "\n\t--> Tweet Author: @" + COLOR.die + str(stats.user.screen_name) + COLOR.green + "\n\t--> Name: " + COLOR.die + str(stats.user.name) + COLOR.green + "\n\t--> Location: " + COLOR.die + str(stats.user.location) + COLOR.green + "\n\t--> Time Zone: " + COLOR.die + str(stats.user.time_zone) + COLOR.green + "\n\t--> Retweet Count: " + COLOR.die + str(stats.retweet_count) + COLOR.green + "\n\t--> Favourites Count: " + COLOR.die + str(stats.favorite_count) + COLOR.green + "\n\t--> Tweeter\'s Status Count: " + COLOR.die + str(stats.user.statuses_count) + COLOR.green + "\n\t--> Tweet Created At: " + COLOR.die + str(stats.created_at) + COLOR.green + "\n\t--> Tweeter's ID Created: " + COLOR.die + str(stats.user.created_at) + COLOR.green + "\n\t--> Tweet Text: " + COLOR.die + str(stats.text) + COLOR.green + "\n\t--> Author Description: " + COLOR.die + str(stats.user.description) + "\n\n"
		else:
			cursor = con.execute("select * from tweets where tweetID=?",(str(tweetID),))
			for row in cursor:
				print COLOR.green + "\n\t--> Found in Database...\n" + COLOR.die
				print COLOR.green + "\n\t--> Tweet Author: @" + COLOR.die + str(row[1]) + COLOR.green + "\n\t--> Name: " + COLOR.die + str(row[2]) + COLOR.green + "\n\t--> Location: " + COLOR.die + str(row[3]) + COLOR.green + "\n\t--> Time Zone: " + COLOR.die + str(row[4]) + COLOR.green + "\n\t--> Retweet Count: " + COLOR.die + str(row[5]) + COLOR.green + "\n\t--> Favourites Count: " + COLOR.die + str(row[6]) + COLOR.green + "\n\t--> Tweeter\'s Status Count: " + COLOR.die + str(row[7]) + COLOR.green + "\n\t--> Tweet Created At: " + COLOR.die + str(row[8]) + COLOR.green + "\n\t--> Tweeter's ID Created: " + COLOR.die + str(row[9]) + COLOR.green + "\n\t--> Tweet Text: " + COLOR.die + str(row[10]) + COLOR.green + "\n\t--> Author Description: " + COLOR.die + str(row[11]) + "\n\n"
	except Exception, e:
		print COLOR.red + "Error: {0}".format(e) + COLOR.die
		exit()

def main():
	banner()
	if len(argv) < 2:
                print COLOR.red + "   --> Usage: {0} <tweetID>\n".format(argv[0]) + COLOR.die
		print COLOR.red + "   --> Example: {0} 814019208212320256\n".format(argv[0]) + COLOR.die
	else:	
		try:
			while True:
				try:
					tweetId = raw_input("   (\033[1mCommands:\033[0m)> ")
					if tweetId == "change":
						newTweetID = raw_input("\n   (\033[1mNew TweetID:\033[0m)> ")
						PerformAnalysis(newTweetID)
					elif tweetId == "stats":
						print COLOR.red + COLOR.bold + "\n -- Stats For This Tool are -- \n\n   Tool Nature: Command Line\n   Compatibility: Cross Platform\n   Language: Python\n   Database: SQLite\n   Extra Module: python-twitter\n   Feature: Colored output without external module\n" + COLOR.die
					elif tweetId == "clear":
						system('clear')
						banner()
					elif tweetId == "forensic":
						print COLOR.bold + "\n   --> Please Wait..." + COLOR.die
						sleep(0.5)
						PerformAnalysis(argv[1])
					elif tweetId == "help":
						print COLOR.bold + """
   -------------------------------
    help   - Show this Meessage
    change - Change Tweet ID
    stats  - Tool Statistics
    clear  - clear the Console
    exit   - quit the tool
   -------------------------------""" + COLOR.die
					elif tweetId == "exit":
						print COLOR.bold + "\n  [+] Good Bye.\n" + COLOR.die
						exit()
					else:
						print COLOR.bold + "\n  [-] Invalid Command.\n" + COLOR.die
				except KeyboardInterrupt:
					print COLOR.red + "\nError: KeyboardInterrupt" + COLOR.die
					exit()
		except Exception, e:
			print COLOR.red + "Error: {0}".format(e) + COLOR.die

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print COLOR.red + "\nError: KeyboardInterrupt" + COLOR.die
		exit()
