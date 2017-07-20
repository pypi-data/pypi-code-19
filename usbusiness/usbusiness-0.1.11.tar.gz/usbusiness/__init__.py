import sys
import csv
import warnings

import re
import pandas as pd
import requests
import tldextract
from bs4 import BeautifulSoup
from collections import defaultdict

import pkg_resources

warnings.filterwarnings("ignore")

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
TIMEOUT = 10
CLASSIFIER = None
LABEL_ENCODER = None
NAICS_MAPPER = None
STOP_WORDS = None
SPELL_CHECKER = None

def time_me(f):
    def wrap(*args):
        import time
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '{} function took {:.4f} s'.format(f.func_name, (time2-time1))
        return ret
    return wrap

def _download(file_name,link):

    with open(file_name, "wb") as f:
            print "Downloading %s" % file_name
            response = requests.get(link, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None: # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                    sys.stdout.flush()

def download():
    '''check to see if model exists if not download'''
    link_site_clf = "https://s3-us-west-2.amazonaws.com/usbusiness-naics/site_clf.sk"
    file_name = pkg_resources.resource_filename(__name__,'data/site_clf.sk')
    _download(file_name,link_site_clf)

@time_me
def initialize(classifier_path=None):
    load_stop_words()
    load_naics_map()
    load_checker_d()
    load_classifier(classifier_path)

def load_stop_words():
    global STOP_WORDS
    if STOP_WORDS == None:
        STOP_WORDS = open(pkg_resources.resource_filename(__name__,'data/stop_words.txt')).read().splitlines()

def load_checker_d():
    from enchant import DictWithPWL
    from enchant.checker import SpellChecker
    global SPELL_CHECKER
    if SPELL_CHECKER == None:
        d = DictWithPWL("en_US",pkg_resources.resource_filename(__name__, 'data/google_100k.txt'))
        SPELL_CHECKER = SpellChecker(d)

def load_naics_map():
    global NAICS_MAPPER
    if NAICS_MAPPER == None:
        df_map = [x for x in csv.DictReader(open(pkg_resources.resource_filename(__name__,'data/naics_codes_2012.csv')))]
        NAICS_MAPPER = {str(x['code']):x['description'] for x in df_map}

def load_classifier(classifier_path=None):
    from sklearn.externals import joblib
    global CLASSIFIER, LABEL_ENCODER
    with warnings.catch_warnings():
        if CLASSIFIER == None:
            d = joblib.load(pkg_resources.resource_filename(__name__,'data/site_clf.sk')) if classifier_path == None else joblib.load(classifier_path)
            CLASSIFIER = d['classifier']
            LABEL_ENCODER = d['label_encoder']

def get_website_tld(website):
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

def soup_to_text(soup):
    for script in soup(["script","style","symbol"]):
        script.extract()
    blob = " ".join(soup.strings)
    return blob

def clean_text(blob):
    load_stop_words()
    blob = unicode(blob.encode('utf-8','ignore'),errors='ignore') if blob!=None else ''
    blob = blob.strip()
    blob = re.sub(r'[\n\r\t]',' ',blob)
    blob = re.sub(' +',' ',blob)
    blob = re.sub(r"&nbsp;", " ", blob)
    blob = re.sub(r"-", " ", blob)
    blob = blob.split()
    words = [re.compile('[^a-zA-Z]').sub('',x.lower()) for x in blob]
    words = [w for w in words if not w in STOP_WORDS]
    blob = ' '.join(words[0:2000])
    blob = re.sub(' +',' ',blob)
    return blob

def spell_check(blob):
    load_checker_d()
    SPELL_CHECKER.set_text(blob)
    for err in SPELL_CHECKER:
        # print err.word
        err.replace('')
    blob = SPELL_CHECKER.get_text().lower()
    blob = re.sub(' +',' ',blob).strip()
    return blob

def get_all_links(soup,website,top_x):
    suffix = tldextract.extract(website).suffix
    tld = get_website_tld(website)
    domain = get_website_tld(website)
    links = soup.find_all(href=True)
    links = [x.get('href') for x in links]
    links_full = [x for x in links if get_website_tld(x) == domain]
    links_full = [x.split(suffix)[1] for x in links_full if '/' in x.split(suffix)[1]]
    links_full = [x.split('/')[1] for x in links_full]
    links_partial = [x for x in links if (get_website_tld(x)=='' and '/' in x)]
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

    load_classifier()
    load_naics_map()

    website_data = get_website_text(website)
    blob = website_data.get('blob','')
    out_encoded = CLASSIFIER.predict([blob])[0]
    out = LABEL_ENCODER.inverse_transform(out_encoded)
    return {
        'website':website,
        'website_text':blob,
        'naics6':out,
        'naics6_description':NAICS_MAPPER.get(out,''),
        'naics5':out[0:5],
        'naics5_description':NAICS_MAPPER.get(out[0:5],'').strip(),
        'naics4':out[0:4],
        'naics4_description':NAICS_MAPPER.get(out[0:4],'').strip(),
        'naics3':out[0:3],
        'naics3_description':NAICS_MAPPER.get(out[0:3],'').strip(),
        'naics2':out[0:2],
        'naics2_description':NAICS_MAPPER.get(out[0:2],'').strip(),
    }


def classify_website_proba(website, desc=True):

    load_classifier()
    load_naics_map()

    website_data = get_website_text(website)
    blob = website_data.get('blob','')
    ans = predict_probability(blob,desc)
    return ans

def predict_probability(text, desc=True):
    out = [[x,y] for x,y in zip(CLASSIFIER.classes_, CLASSIFIER.predict_proba([text])[0])]

    labels = LABEL_ENCODER.inverse_transform([x[0] for x in out])
    values = [x[1] for x in out]

    ans = [{label:value} for label,value in zip(labels,values)]
    ans = [[{'naics_6':x,'naics_5':x[0:5],'naics_4':x[0:4],'naics_3':x[0:3],'naics_2':x[0:2],'value':y} for x,y in z.iteritems()][0] for z in ans]

    naics_2_prob, naics_3_prob, naics_4_prob, naics_5_prob, naics_6_prob = {}, {}, {}, {}, {}
    for row in ans:
        naics_2_prob[row['naics_2']] = naics_2_prob.get(row['naics_2'],0) + row['value']
        naics_3_prob[row['naics_3']] = naics_3_prob.get(row['naics_3'],0) + row['value']
        naics_4_prob[row['naics_4']] = naics_4_prob.get(row['naics_4'],0) + row['value']
        naics_5_prob[row['naics_5']] = naics_5_prob.get(row['naics_5'],0) + row['value']
        naics_6_prob[row['naics_6']] = naics_6_prob.get(row['naics_6'],0) + row['value']

    top_3 = sorted(naics_6_prob.iteritems(), key=lambda x:-x[1])[:3]
    top_3 = [{'naics_2':x[0][0:2], 'naics_3':x[0][0:3], 'naics_4':x[0][0:4], 'naics_5':x[0][0:5], 'naics_6':x[0]} for x in top_3]

    _ = [x.update({
        'naics_2_prob':naics_2_prob[x['naics_2']],
        'naics_3_prob':naics_3_prob[x['naics_3']],
        'naics_4_prob':naics_4_prob[x['naics_4']],
        'naics_5_prob':naics_5_prob[x['naics_5']],
        'naics_6_prob':naics_6_prob[x['naics_6']],
        }) for x in top_3]

    if desc == True:
        _ = [x.update({
            'naics_2_desc':NAICS_MAPPER[x['naics_2']],
            'naics_3_desc':NAICS_MAPPER[x['naics_3']],
            'naics_4_desc':NAICS_MAPPER[x['naics_4']],
            'naics_5_desc':NAICS_MAPPER[x['naics_5']],
            'naics_6_desc':NAICS_MAPPER[x['naics_6']],
            }) for x in top_3]

    return top_3
