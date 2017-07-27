import requests
import json

from user import User

def request_data(CLIENT_ID, CLIENT_SECRET, APP_ID, local = False):
    # Try not to run this too much. Requests against our server for all user data from users that authenticated your app.
    payload = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'appId': APP_ID}
    if local:
    	url = 'https://yo.com:3000/api/group-data'
    else:
    	url = 'https://app.transcendbeta.com/api/group-data'
    r = requests.get(url, params=payload, verify=False)

    if (r.status_code != 200 and r.status_code != 204):
        print("Error: " + r.text)
    elif (r.status_code == 204):
        print("User is not authenticated for this app.")
    else:
        return json.loads(r.content)