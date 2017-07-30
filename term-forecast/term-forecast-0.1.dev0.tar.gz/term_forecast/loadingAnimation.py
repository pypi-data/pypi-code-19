#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Author: KevinMidboe
# @Date:   2017-07-30 13:53:38
# @Last Modified by:   KevinMidboe
# @Last Modified time: 2017-07-30 13:53:46

import itertools
from threading import Thread
from time import sleep
from sys import stdout

class LoadingAnimation(object):
	def __init__(self):
		self.done = False

	def start(self):
		t = Thread(target=self.animate)
		t.start()

	def animate(self):
	    for c in itertools.cycle(['|', '/', '-', '\\']):
	        if self.done:
	            break
	        stdout.write('\rFetching ' + c)
	        stdout.flush()
	        sleep(0.1)

	def stop(self):
		self.done = True

def main():
	loadingAnimation = LoadingAnimation()
	loadingAnimation.start()
	sleep(2)
	loadingAnimation.stop()
	stdout.write('\rTemp          \n')
	
if __name__ == '__main__':
	main()