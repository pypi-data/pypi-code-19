from my_logger import MyLogger
from bs4 import BeautifulSoup
import urllib2
from urllib import quote_plus

class GoogleSearch:

  def __init__(self):
    self.logger = MyLogger("debug", "GoogleSearch")
    self.logger.log("created")


  def start(self, company_name):
    self.logger.log("start")

    headers = { 'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0' }
    query = quote_plus(company_name)
    url = ('http://www.google.de/search?hl=de&q=%(query)s&btnG=GoogleSearch&gws_rd=ssl' % {'query': query})
    req = urllib2.Request(url, None, headers)
    html = urllib2.urlopen(req).read()

    soup = BeautifulSoup(html, 'html5lib')
    anchors = soup.find(id='search').find_all('a')

    urls = []
    for a in anchors:
      # remove internal links
      if 'search' in a['href']:
        continue
      elif 'google' in a['href']:
        continue
      if 'http' in a['href']:
	urls.append(a['href'])
    return urls


if __name__ == "__main__":
  gs = GoogleSearch()
  urls = gs.start("Scheidt & Bachmann")
  for url in urls:
    print url
