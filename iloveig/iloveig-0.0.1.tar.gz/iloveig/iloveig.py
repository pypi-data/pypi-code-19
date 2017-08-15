import os
import re
import json
import sys
import time
import platform
import requests

from bs4 import BeautifulSoup


def find_query_id(soup):

    data = soup.find_all("script")[1].string
    p = re.compile('window._sharedData = (.*?);')
    m = p.match(data)
    o = json.loads(m.groups()[0])

    csrf_token = o['config']["csrf_token"]
    end_cursor = o["entry_data"]["ProfilePage"][0]["user"]["media"]['page_info']['end_cursor']
    has_next_page =  o["entry_data"]["ProfilePage"][0]["user"]["media"]['page_info']['has_next_page']
    user_id = o["entry_data"]["ProfilePage"][0]["user"]["id"]

    query_ids = []
    for script in soup.find_all("script"):
         if script.has_attr("src") and "zh_TW_Commons" in script['src']:
            text = requests.get("%s%s" % ('https://www.instagram.com', script['src'])).text
            for query_id in re.findall("(?<=queryId:\")[0-9]{17,17}", text):
                query_ids.append(query_id)

    query_id = ''

    for qid in query_ids:
        try:
            response = requests.get(
                url="https://www.instagram.com/graphql/query/",
                params={
                    "first": "12",
                    "after": end_cursor,
                    "id": user_id,
                    "query_id": qid,
                },
                headers={
                    "cookie": "csrftoken=" + csrf_token,
                    "x-requested-with": "XMLHttpRequest",
                    "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4",
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
                },
            )
            obj = json.loads(response.text)
            if 'ok' in obj['status'] and obj['data']:
                if 'user' in obj['data']:
                    if obj['data']['user'] is not None:
                        query_id = qid
                        break
                    else:
                        continue
                else:
                    continue
            else:
                continue

        except requests.exceptions.RequestException:
            print('HTTP Request failed')

    if not query_id:
        print("Error extracting Query Id, exiting")
        sys.exit(1)

    return query_id

def create_iloveig_and_username_folder(username):
    """
    create folder and username folder
    """

    system = platform.system()
    if system == 'Darwin':
        picfolder = 'Pictures'
    elif system == 'Windows':
        release = platform.release()
        if release in ['Vista', '7', '8']:
            picfolder = 'Pictures'
        elif release is 'XP':
            picfolder = os.path.join('My Documents', 'My Pictures')
        else:
            picfolder = ''
    else:
        picfolder = ''

    home = os.path.expanduser("~")
    base_folder = os.path.join(home, picfolder, 'iloveckig')

    if not os.path.exists(base_folder):
        os.mkdir(base_folder)

    folder = os.path.join(base_folder, "%s" % (username))

    if not os.path.exists(folder):
        os.mkdir(folder)

    return folder

def iloveig(url):
    print 'start fetch url: %s' %(url)

    r = requests.get(
        url=url,
        headers={
            "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        }
    )

    soup = BeautifulSoup(r.text, 'html.parser')

    data = soup.find_all("script")[1].string
    p = re.compile('window._sharedData = (.*?);')
    m = p.match(data)
    o = json.loads(m.groups()[0])

    csrf_token      = o['config']["csrf_token"]
    end_cursor      = o["entry_data"]["ProfilePage"][0]["user"]["media"]['page_info']['end_cursor']
    has_next_page   = o["entry_data"]["ProfilePage"][0]["user"]["media"]['page_info']['has_next_page']
    user_id         = o["entry_data"]["ProfilePage"][0]["user"]["id"]

    query_id    = find_query_id(soup)
    title       = o['entry_data']['ProfilePage'][0]['user']['username']
    folder      = create_iloveig_and_username_folder(title)

    for element in o["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]:
        filename = element['display_src'].rsplit('/', 1)[1]

        resp = requests.get(element['display_src'])
        print 'fetch %s' % (filename)

        with open(os.path.join(folder, filename), 'wb+') as f:
            f.write(resp.content)

    while has_next_page:
        try:
            time.sleep(10)
            response = requests.get(
                url="https://www.instagram.com/graphql/query/",
                params={
                    "first": "12",
                    "after": end_cursor,
                    "id": user_id,
                    "query_id": query_id,
                },
                headers={
                    "cookie": "csrftoken=" + csrf_token,
                    "x-requested-with": "XMLHttpRequest",
                    "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4",
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
                },
            )

            obj = json.loads(response.text)

            if 'data' in obj:

                for element in obj['data']['user']['edge_owner_to_timeline_media']['edges']:
                    filename = element['node']['display_url'].rsplit('/', 1)[1].rsplit('?', 1)[0]

                    resp = requests.get(element['node']['display_url'])

                    print 'fetch %s' % (filename)

                    with open(os.path.join(folder, filename), 'wb+') as f:
                        f.write(resp.content)

                end_cursor = obj["data"]["user"]["edge_owner_to_timeline_media"]['page_info']['end_cursor']
                has_next_page =  obj["data"]["user"]["edge_owner_to_timeline_media"]['page_info']['has_next_page']

            else:
                print obj
                has_next_page = False

        except requests.exceptions.RequestException:
            print('HTTP Request failed')
            sys.exit(1)

    print 'Winter is comming'

def main():
    try:
        url = sys.argv[1]
    except IndexError:
        sys.exit('Please provide URL from ck101')

    iloveig(url)
