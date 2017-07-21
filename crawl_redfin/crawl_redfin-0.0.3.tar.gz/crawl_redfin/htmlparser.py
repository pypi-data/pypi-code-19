#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

try:
    from .pkg.crawlib import exc
    from .pkg.crawlib.htmlparser import BaseHtmlParser
except:
    from crawl_redfin.pkg.crawlib import exc
    from crawl_redfin.pkg.crawlib.htmlparser import BaseHtmlParser


class HTMLParser(BaseHtmlParser):
    """Redfin html parser.
    """

    def get_all_state(self, html):
        """Parse state information.

        Example: https://www.redfin.com/sitemap
        """
        soup = self.get_soup(html)
        all_state = list()

        for ul in soup.find_all("ul"):
            try:
                if ul.attrs["data-reactid"] == "5":
                    for a in ul.find_all("a"):
                        state_href = a["href"]
                        state_abbr = state_href.split("/")[-1]
                        state_name = a.text
                        all_state.append({
                            "state_href": state_href,
                            "state_abbr": state_abbr,
                            "state_name": state_name,
                        })
            except:
                pass
        return all_state

    def get_all_county_and_zipcode(self, html):
        """Parse county and zipcode information.

        Example: https://www.redfin.com/sitemap/MD
        """
        soup = self.get_soup(html)
        all_county = list()
        all_zipcode = list()
        for ul in soup.find_all("ul"):
            try:
                if ul.attrs["data-reactid"] == "5":
                    for a in ul.find_all("a"):
                        county_href = a["href"]
                        county_code = county_href.split("/")[-3]
                        county_name = a.text
                        all_county.append({
                            "county_href": county_href,
                            "county_code": county_code,
                            "county_name": county_name,
                        })
            except:
                pass

        for ul in soup.find_all("ul", class_="list"):
            try:
                for a in ul.find_all("a"):
                    zipcode_href = a["href"]
                    if zipcode_href.startswith("/zipcode/"):
                        zipcode = zipcode_href.split("/")[-1]
                        all_zipcode.append({
                            "zipcode_href": zipcode_href,
                            "zipcode": zipcode,
                        })
            except:
                pass

        return all_county, all_zipcode

    def get_all_city(self, html):
        """Parse city information.

        Example: https://www.redfin.com/sitemap/1324/MD/Montgomery-County
        """
        soup = self.get_soup(html)
        all_city = list()

        for ul in soup.find_all("ul", class_="list"):
            try:
                for a in ul.find_all("a"):
                    city_href = a["href"]
                    if city_href.startswith("/city/"):
                        city_code = city_href.split("/")[2]
                        city_name = a.text.strip()
                        all_city.append({
                            "city_href": city_href,
                            "city_code": city_code,
                            "city_name": city_name,
                        })
            except:
                pass
        return all_city


htmlparser = HTMLParser()


if __name__ == "__main__":
    from os.path import join, exists
    from pprint import pprint as ppt

    from pathlib_mate import Path

    from crawl_redfin.urlencoder import urlencoder
    from crawl_redfin.pkg.dataIO.textfile import read, write

    import time
    from selenium_spider import ChromeSpider

    executable_path = r"C:\Users\shu\PycharmProjects\py34\crawl_redfin-project\chromedriver.exe"
#     driver = ChromeSpider(executable_path)

    def get_path(filename):
        return join("testhtml", filename)

    def test_get_all_state():
        # Get test data
        url = urlencoder.state_listpage()
        path = get_path("all_state.html")
        if not exists(path):
            with ChromeSpider(executable_path) as spider:
                html = spider.get_html(url)
                write(html, path)

        html = read(path)
        ppt(htmlparser.get_all_state(html))

#     test_get_all_state()

    def test_get_all_county_and_zipcode():
        state_list = ["MD", "VA", "PA"]
        path_list = [get_path("state_%s.html" % state) for state in state_list]

        # Get test data
        need_download_flag = False
        for state, path in zip(state_list, path_list):
            if not exists(path):
                need_download_flag = True

        if need_download_flag:
            with ChromeSpider(executable_path) as spider:
                for state, path in zip(state_list, path_list):
                    if not exists(path):
                        url = urlencoder.county_and_zipcode_listpage(state)
                        html = spider.get_html(url)
                        write(html, path)

        for state, path in zip(state_list, path_list):
            html = read(path)
            all_county, all_zipcode = htmlparser.get_all_county_and_zipcode(
                html)
            ppt(all_zipcode)

#     test_get_all_county_and_zipcode()

    def test_get_all_city():
        county_href_list = [
            "/sitemap/1324/MD/Montgomery-County",
            "/sitemap/1312/MD/Baltimore-County",
            "/sitemap/1319/MD/Frederick-County-MD",
        ]
        path_list = [
            get_path("county_%s.html" % county_href.split("/")[-1])
            for county_href in county_href_list
        ]

        # Get test data
        need_download_flag = False
        for county_href, path in zip(county_href_list, path_list):
            if not exists(path):
                need_download_flag = True

        if need_download_flag:
            with ChromeSpider(executable_path) as spider:
                for county_href, path in zip(county_href_list, path_list):
                    if not exists(path):
                        url = urlencoder.city_listpage(href=county_href)
                        html = spider.get_html(url)
                        write(html, path)

        for county_href, path in zip(county_href_list, path_list):
            html = read(path)
            all_county = htmlparser.get_all_city(html)
            ppt(all_county)

    test_get_all_city()
