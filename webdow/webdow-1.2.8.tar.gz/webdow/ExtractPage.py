#!/usr/bin/python
from selenium import webdriver
import time
from pyvirtualdisplay import Display

'''
Get the source code from the webpage.

url: The url from which you need to get the source code
scroll_time: The time taken for the webpage to load when you scroll to the bottom (This depends on you internet speed)

'''
def get_html(url,scroll_time = 10):
	print 'Creating a virtual display...'
	display = Display(visible=0, size=(800, 600))
	display.start()

	print 'Starting Chrome in background...'
	driver = webdriver.Chrome()

	print 'Loading Webpage...'
	#Load the webpage
	driver.get(url)


	# Get the height of the webpage currently loaded
	prev_height = driver.execute_script("return document.body.scrollHeight")

	while True:

		print 'Scrolling down...'
		# Scroll to the very bottom of the webpage
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight-100);")

		# Sleep and wait for the webpage to load it's contents
		time.sleep(scroll_time)

		# Get the current height
		cur_height = driver.execute_script("return document.body.scrollHeight")
		
		#If current height is the same as the previous height, that implies no new content has loaded.So break out of the loop
		if (cur_height == prev_height):
			break
		else:
			print 'More content loaded...'
			prev_height = cur_height

	print 'Encoding the html script...'
	#Encode the source code of the webpage
	src = driver.page_source.encode('ascii', 'ignore')

	print 'Ending chrome...'
	#End session and safely close the browser
	driver.quit()
	print 'Ending virtual display...'
	display.stop()

	return src


'''
Writes the html contents to a file.

src: The source of Html file.
filePath: the path of the file where the file has to be written. 
NOTE: The path has to include the filename with '.html' extention.

'''
def write_html(src,filePath):
	print 'Opening file: ',filePath
	w=open(filePath,"w")
	try:
		print 'Writing to file...'
		w.write(src)
	except Exception,e:
		print 'ERROR OCCURED DURING WRITING TO FILE'
		print '\n'
		print 'ERROR IS: '
		print e
	w.close()

