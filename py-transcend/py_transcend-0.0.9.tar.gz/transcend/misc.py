import requests
import json

from transcend.user import User

def request_data(CLIENT_ID, CLIENT_SECRET, APP_ID):
    # Try not to run this too much. Requests against our server for all user data from users that authenticated your app.
    payload = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'appId': APP_ID}
    r = requests.get('https://app.transcendbeta.com/api/group-data', params=payload, verify=False)

    if (r.status_code != 200 and r.status_code != 204):
        print("Error: " + r.text)
    elif (r.status_code == 204):
        print("Request was valid, but there aren't any users on your app yet.")

    splt = ',"updatedAt":'
    res = [ x for x in r.content.split(splt)]
    splt2 = '{"_id":'
    n = len(res)
    print('Number of users in the group', n - 1)

    tl = res[0][len(splt2):]
    for i in range(1, n - 1):
        spltz = res[i].split(splt2)
        good = splt2.join(spltz[:-1])
        res[i] = splt2 + tl + splt + good
        tl = spltz[-1]

    res[n - 1] = splt2 + tl + splt + res[n - 1]
    res = res[1:]

    users = [User(json.loads(x)) for x in res]
    return users