from my_logger import MyLogger
from link_extractor.link_extractor import LinkExtractor
from google_search.google_search import GoogleSearch
from pymongo import MongoClient
from datetime import datetime
import urllib2
from bs4 import BeautifulSoup
import re

class WebsiteFinder:

	def __init__(self):
		global words, client, db
		client  = MongoClient("127.0.0.1", 27017)
		db = client.test
		words = ["impressum", "kontakt"]
		self.logger = MyLogger("WebsiteFinder")
		self.logger.log("created")


	def findFromCompanyName(self, company_name):
		self.logger.log("Starting research for: %s" % company_name)

		gs = GoogleSearch()
		links = gs.start(company_name)

		for link in links:
			if self.__websiteMatchesCompanyName(link, company_name):
				self.logger.log("Found url: %s" % link)
				return link
		self.logger.log(("Not found: %s" % company_name), "warning")
		return None


	def __websiteMatchesCompanyName(self, link, company_name):
		linkExtractor = LinkExtractor()
		impressum_link = linkExtractor.getImpressum(link)
		
		if None == impressum_link:
			return False

		response = urllib2.urlopen("http://www." + impressum_link)
		html = response.read()
        	soup = BeautifulSoup(html, "html.parser")

		for tag in soup.find_all(text=re.compile(company_name, re.IGNORECASE)):
			return True

		return False


if __name__ == "__main__":
  wf = WebsiteFinder()
  wf.findFromCompanyName("Scheidt & Bachmann")
