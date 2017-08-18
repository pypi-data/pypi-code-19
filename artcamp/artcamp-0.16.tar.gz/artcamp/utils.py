import json
import requests

import pandas as pd
from bs4 import BeautifulSoup

def load_json(file_path):
    with open(file_path) as json_data:
        d = json.load(json_data)
    return d

def fetch_url(url, tags, verify, strip_unicode):
        """
        Scrapes and fetches front-page text content for a given url.
        **Note** - The scraping methods in this are particular to the websites
        provided by the irs 990 forms. In particular, the conditional statements
        dealing with the "www." and "http" stuff may not work across the board for
        different websites. The 990 websites being scraped are for non-profits, and
        often don't have the most secure sites. Thus this seemingly ad-hoc code works
        well.

        Parameters
        ----------
        url : str
            URL of website to be scraped.
        tags : iterable
            List of html tags in-which to grab content.
        verify : Boolean (default=True)
            Whether or not to ignore verification of SSL certificate.
        strip_unicode : Boolean (default=True)
            Whether or not to strip unicode values from result.

        Returns
        -------
            iterable : List of unicode-stripped tokens from front-page of `url`.
        """
        from bs4 import BeautifulSoup
        orig_url = url
        url = url.lower()
        if "www." in url:
            url = url.split("www.")[-1].split("/")[0]
        elif "http://" in url:
            url = url.strip("http://")
        domain = "http://" + url
        html = requests.get(domain, verify=verify, headers=self.headers)
        soup = BeautifulSoup(html.content, "html.parser")
        site_text = []
        for tag in soup.find_all(tags):
            site_text.append(tag.get_text().strip())
        all_text = " ".join(site_text)
        cleaned_text = re.sub('\s+', ' ', all_text)
        if strip_unicode:
            cleaned_text = ''.join([i if ord(i) < 128 else ' ' for i in cleaned_text])
        return pd.DataFrame({"url": [orig_url], "url_text": [cleaned_text]})





name_list = []
