from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import argparse
import os
from Yahoo_Finance_Stock_Ticker.ticker import start_ticker
from Yahoo_Finance_Stock_Ticker.ticker import add_ticker
from Yahoo_Finance_Stock_Ticker.ticker import remove_ticker
from Yahoo_Finance_Stock_Ticker.ticker import create_new

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--start', help="Print the ticker(s) that is/are saved",choices=['ticker'])
	parser.add_argument('--add', help="Add a stock ticker")
	parser.add_argument('--remove', help="Remove a stock ticker")
	parser.add_argument('--create', help="Create a new list")
	args = parser.parse_args()
	
	if args.add:
		add_ticker(args.add)
	
	if args.remove:
		remove_ticker(args.remove)
	
	if args.start == 'ticker':
		start_ticker()

	if args.create == 'list':
		create_new()

if __name__ == '__main__':
	main()