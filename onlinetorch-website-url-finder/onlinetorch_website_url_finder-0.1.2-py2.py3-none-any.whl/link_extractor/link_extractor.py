from my_logger import MyLogger
import os
import urllib2
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

class LinkExtractor:

	def __init__(self):
		self.logger = MyLogger("debug", "LinkExtractor")
		global client, db
		client  = MongoClient()
		db = client.test
		self.logger.log("created")

	def start(self, links, words):
		self.logger.log("start")
		hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       			'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       			'Accept-Encoding': 'none',
       			'Accept-Language': 'de;q=0.7,en;q=0.8',
       			'Connection': 'keep-alive'}
		for link in links:
			request= urllib2.Request(link, headers=hdr)
			response = urllib2.urlopen(request)
			html = response.read()

			domain = self.__DomainFromLink(link)
			filename = self.__FilenameFormLink(link)

			if not os.path.exists(path):
				os.makedirs(path)
			try:
        	        	text_file = open(filename, "w")
               			text_file.write("%s" % html)
	                	text_file.close()
			except IOError:
				self.logger.log("Error: Datei %s nicht schreibbar" % filename)
				result = db.url_list.updateOne(
					{"url" : domain},
					{
						"$set",
						{
							"status-code" : "410",
							"status-description" : "File not writeable",
							"timestamp"	: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
						}
					}
				)
				#todo error log hier
				continue

	                soup = BeautifulSoup(html, "html.parser")
			for a in soup.find_all('a'):
                    		href = a.get('href')
                    		if href:
                        		for word in words:
                           			if word in href:
                                			url = self.__realUrl(href, domain)
                                			self.logger.log(url)

        def __realUrl(self, path, domain):
		if domain[-1:] == '/':
			domain = domain[:-1]

		if 'http' in path:
                    return path
                return domain + "/" + path


	def __DomainFromLink(self, link):
		if link[-1:] == '/':
			link = link[:-1]

		if 'https' in link:
			if 'www' in link:
				domain = link[12:].split("/")[0]
			else:
				domain = link[8:].split("/")[0]
		elif 'http' in link:
			domain = link[7:].split("/")
			if 'www' in link:
				domain = link[11:].split("/")[0]
			else:
				domain = link[7:].split("/")[0]

		return domain


	def __FilenameFromLink(self, link):
		if link[-1:] == '/':
			link = link[:-1]

		if 'https' in link:
			if 'www' in link:
				domain = link[12:].split("/")[0]
				path = "../var/websites/" + domain
				filename = path + "/" + domain + ".html"
			else:
				domain = link[8:].split("/")[0]
				path = "../var/websites/" + domain
				filename = path + "/" + domain + ".html"
		elif 'http' in link:
			domain = link[7:].split("/")
			if 'www' in link:
				domain = link[11:].split("/")[0]
				path = "../var/websites/" + domain
				filename = path + "/" + domain + ".html"
			else:
				domain = link[7:].split("/")[0]
				path = "../var/websites/" + domain
				filename = path + "/" + domain + ".html"

		return filename


	def getImpressum(self, link):
		self.logger.log(link)
		words = ["Impressum", "impressum"]
		hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	       		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	       		'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	       		'Accept-Encoding': 'none',
	       		'Accept-Language': 'de;q=0.7,en;q=0.8',
	       		'Connection': 'keep-alive'}
		request = urllib2.Request(link, headers=hdr)
		response = urllib2.urlopen(request)
		html = response.read()
                soup = BeautifulSoup(html, "html.parser")

		domain = self.__DomainFromLink(link)

		for a in soup.find_all('a'):
	       		href = a.get('href')
        		if href:
				for word in words:
               				if word in href:
                    				return self.__realUrl(href, domain)
		return None
