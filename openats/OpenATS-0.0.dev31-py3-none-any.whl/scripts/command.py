
import os
import sys

'''
openATS init = OpenATS.scripts.command:init
makeDataset = OpenATS.scripts.command:makeDataset
run = OpenATS.scripts.command:run
runAll = OpenATS.scripts.command:runAll
'''

def init():
    print("OpenATS.scripts.command.init")
    print("Create Directory Tree")
    print(sys.argv)

def makeDataset():
	print("OpenATS.scripts.command.makeDataset")
	print("Create Dataset")

def run():
	print("OpenATS.scripts.command.run")
	pass

def runAll():
	print("OpenATS.scripts.command.runAll")
	pass

def main():
	print("main!!")