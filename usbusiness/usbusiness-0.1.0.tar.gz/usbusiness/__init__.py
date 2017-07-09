from __future__ import division

import re
import pandas as pd
import requests
import tldextract
from bs4 import BeautifulSoup
from collections import defaultdict

from enchant import DictWithPWL
from enchant.checker import SpellChecker

from nltk.corpus import stopwords

from sklearn.externals import joblib

DATA_CLASSIFIER = 'util/site_clf.sk'
DATA_NAICS_MAP = 'util/2_digit_2012_codes.csv'

d = joblib.load(DATA_CLASSIFIER)
clf = d['classifier']
le = d['label_encoder']

df_map = pd.read_csv(DATA_NAICS_MAP,index_col=False).to_dict('records')
naics_mapper = {x['code']:x['description'] for x in df_map}

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
TIMEOUT = 10

def time_me(f):
    def wrap(*args):
        import time
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '{} function took {:.2f} ms'.format(f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap

def keyword_density(blob,_top_x):

    wordsNoTags = blob.split()

    word_list = {}
    total = 0
    for word in wordsNoTags:
        if not word in word_list:
            word_list[word] = 1
        else:
            word_list[word] += 1
        total +=1

    top_x = sorted(word_list.items(), key=lambda x: x[1],reverse=True)[0:_top_x]
    keywords = [{'word':x[0],'count':x[1],'density':round(x[1]/total*100,2)} for x in top_x]

    return keywords

def get_website_tld(website):
    ans = tldextract.extract(website)
    website_tld = '.'.join(part for part in ans if part)
    return website_tld

def get_website_domain(website):
    ans = tldextract.extract(website)
    website_tld = '.'.join(part for part in ans if part)
    return website_tld

def query_website(website):
    '''E.g query_website("ablelending.com")'''
    website_tld = get_website_tld(website)
    if re.search('(http://|https://)',website_tld) is None:
        url = 'http://'+website_tld
    else:
        url = 'http://'+website_tld.rstrip()
    try:
        request = requests.get(url,headers=HEADERS,timeout=TIMEOUT)
    except (requests.exceptions.SSLError, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError, requests.exceptions.ContentDecodingError):
        request = requests.models.Response()
    except (requests.exceptions.ReadTimeout):
        request = requests.models.Response()
        request.status_code = 408

    return request

def soup_to_text(soup):
    for script in soup(["script","style","symbol"]):
        script.extract()
    blob = " ".join(soup.strings)
    return blob

def clean_text(blob):
    blob = unicode(blob.encode('utf-8','ignore'),errors='ignore') if blob!=None else ''
    blob = blob.strip()
    blob = re.sub(r'[\n\r\t]',' ',blob)
    blob = re.sub(' +',' ',blob)
    blob = re.sub(r"&nbsp;", " ", blob)
    blob = re.sub(r"-", " ", blob)
    blob = blob.split()
    words = [re.compile('[^a-zA-Z]').sub('',x.lower()) for x in blob]
    words = [w for w in words if not w in stopwords.words("english")]
    blob = ' '.join(words[0:2000])
    blob = re.sub(' +',' ',blob)
    return blob

def spell_check(blob):
    d2 = DictWithPWL("en_US","util/my_words/google_100k.txt")
    chkr = SpellChecker(d2)
    chkr.set_text(blob)
    for err in chkr:
        # print err.word
        err.replace('')
    blob = chkr.get_text().lower()
    blob = re.sub(' +',' ',blob).strip()
    return blob

def get_all_links(soup,website,top_x):
    suffix = tldextract.extract(website).suffix
    tld = get_website_tld(website)
    domain = get_website_domain(website)
    links = soup.find_all(href=True)
    links = [x.get('href') for x in links]
    links_full = [x for x in links if get_website_domain(x) == domain]
    links_full = [x.split(suffix)[1] for x in links_full if '/' in x.split(suffix)[1]]
    links_full = [x.split('/')[1] for x in links_full]
    links_partial = [x for x in links if (get_website_domain(x)=='' and '/' in x)]
    links_partial = [x.split('/')[1] for x in links_partial]
    links = links_full + links_partial
    links = [x for x in links if x!='']
    links = ['http://{}/{}'.format(tld,x) for x in links]
    d = defaultdict(int)
    for link in links:
        d[link] += 1
    links_top = sorted(d.items(), key=lambda x: x[1],reverse=True)[0:top_x]
    return links_top

def parse_title(soup):
    title = soup.title.string if soup.title != None else ''
    return clean_text(title)

def parse_keywords(soup):
    d = []
    tags = soup.findAll('meta',{'name':'keywords'})
    for tag in tags:
        content = clean_text(tag.get('content',''))
        d.append(content)
    blob = ' '.join(d)
    return blob

def parse_description(soup):
    d = []
    tags = soup.findAll('meta',{'name':'description'})
    for tag in tags:
        content = clean_text(tag.get('content',''))
        d.append(content)
    blob = ' '.join(d)
    return blob

@time_me
def test_get_website_text(website,top_x):
    d = {}
    response = query_website(website)
    if str(response.status_code)[0] not in ['4','5','1','N']:
        soup = BeautifulSoup(response.text,'html.parser')
        blob = soup_to_text(soup)
        blob += ' ' + parse_title(soup)
        blob += ' ' + parse_keywords(soup)
        blob += ' ' + parse_description(soup)
        blob = clean_text(blob) if blob != None else ''
        blob = spell_check(blob) if len(blob)>0 else ''
        d['blob'] = blob
        d['keyword_density'] = keyword_density(blob,top_x)
        d['deep_links'] = get_all_links(soup,website,top_x)
        d['response'] = response.status_code
    else:
        d['blob'] = ''
        d['keyword_density'] = [{}]
        d['deep_links'] = []
        d['response'] = response.status_code

    return d

def get_website_text(website):
    d = {}
    response = query_website(website)
    if str(response.status_code)[0] not in ['4','5','1','N']:
        soup = BeautifulSoup(response.text,'html.parser')
        blob = soup_to_text(soup)
        blob += ' ' + parse_title(soup)
        blob += ' ' + parse_keywords(soup)
        blob += ' ' + parse_description(soup)
        blob = clean_text(blob) if blob != None else ''
        blob = spell_check(blob) if len(blob)>0 else ''
        d['blob'] = blob
        d['response'] = response.status_code
    else:
        d['blob'] = ''
        d['response'] = response.status_code

    return d

def classify_website(website):
    website_data = get_website_text(website)
    blob = website_data.get('blob','')
    out_encoded = clf.predict([blob])[0]
    out = le.inverse_transform(out_encoded)
    return {
        'website':website,
        'website_text':blob,
        'naics6':out,
        'naics6_description':naics_mapper.get(out),
        'naics4':out[0:4],
        'naics4_description':naics_mapper.get(out[0:4]).strip(),
        'naics3':out[0:3],
        'naics3_description':naics_mapper.get(out[0:3]).strip(),
        'naics2':out[0:2],
        'naics2_description':naics_mapper.get(out[0:2]).strip(),
    }

## TESTS ##
# websites = [
#     'https://www.ravenandlily.com',
#     'https://www.ablelending.com',
#     'https://flattrackcoffee.com/',
#     'http://www.fleetcoffee.com/',
#     'http://www.cnn.com/',
#     'http://www.bbc.com/',
#     'www.brilliantsmiles.com',
#     'www.westelm.com',
#     'www.paperlesspost.com',
#     'www.minted.com',
#     'www.bakerbotts.com',
#     'austinboulderingproject.com',
#     'www.hopsandgrain.com',
#     'www.thehotelemma.com',
#     'www.thestoryoftexas.com',
#     'hiatusspa.com',
#     'www.shagthesalon.com',
#     'info.drillinginfo.com',
#     'www.caddominerals.com',
#     'www.shell.com',
#     'www.exxon.com',
#     'www.valero.com',
#     'www.buc-ees.com',
#     'www.mccarthyprint.com',
#     'www.communitybible.com',
#     'www.austinmustardseed.org',
#     'yelp.com',
#     'stdavids.com',
#     'www.kokopellipackraft.com',
#     'kammok.com',
#     'www.allstate.com',
#     'www.ravenandlily.com',
#     'fundingcircle.com',
#     'lendingclub.com',
#     'amazon.com',
#     'google.com',
#     'overlandpartners.com',
#     'www.mainstreetarchitectsinc.com',
#     ]
#
# tags = set()
# ans = [tags.update(tag.name) for tag in soup.find_all()]
