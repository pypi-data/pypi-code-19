#!/usr/bin/python
from __future__ import print_function
import subprocess, json, base64, string, random, sys, urllib

input_json = json.load(sys.stdin)

required = ["uaa_uri",
            "uaa_client_secret",
            "client_payloads"]

missing = filter(lambda key: key not in input_json, required)
if missing:
    raise Exception("missing input argument(s) {}"
                    .format(",".join(missing)))
uaa_uri = input_json["uaa_uri"]
uaa_secret = input_json["uaa_client_secret"]
client_payloads = input_json.get("client_payloads", [])
user_payloads = input_json.get("user_payloads", [])
group_payloads = input_json.get("group_payloads", [])
group_mems = input_json.get("group_mems", [])
# base64_encode of client id and client secret
base64_encode = base64.b64encode("admin:{}".format(uaa_secret))

curl_uaa_uri = "{}/oauth/token?grant_type=client_credentials".format(uaa_uri)

authorization_field = "Authorization: Basic {}".format(base64_encode)

get_token_args = ["curl", "-sS", "-X", "GET", curl_uaa_uri,
                  "-H", authorization_field,
                  "-H", "Content-Type: application/x-www-form-urlencoded",
                  "-H", "Accept: application/json"]

response_json = subprocess.check_output(get_token_args)

def parse_json ( resp_json ):
    try:
        return json.loads(resp_json)
    except:
        raise Exception("non JSON response from server:\n '{}'".
                        format(resp_json))

response_dict = parse_json(response_json)

if not "access_token" in response_dict:
    json.dump(response_dict, sys.stderr)
    raise Exception("no access_token in response")

token = response_dict["access_token"]
authorization_header = "Authorization:bearer {}".format(token)


def uaa_curl ( endpoint, verb = "GET", payload = None ):
    url = uaa_uri + endpoint
    args = ["curl", "-sS", "-X", verb, url,
            "-H", authorization_header,
            "-H", "Accept: application/json"]
    if payload != None:
        args+=["-d", json.dumps(payload),
               "-H", "Content-Type: application/json"]

    resp_json = subprocess.check_output(args)
    return parse_json(resp_json)


def uaa_post_force ( endpoint, payload, delete_id_fun ):
    "post object to the uaa. if it already exists, delete and re-post"
    resp_dict = uaa_curl(endpoint, "POST", payload)
    # print ("resp: {}".format(resp_dict) )
    if "already" in resp_dict.get("error_description", ""):
        delete_id = delete_id_fun()
        assert(delete_id != None)
        print ("deleting ... {}".format(delete_id), file = sys.stderr)
        uaa_curl("{}/{}".format(endpoint, delete_id), "DELETE")
        uaa_curl(endpoint, "POST", payload)


for payload in client_payloads:
    delete_id_fun = lambda client_id = payload["client_id"]: client_id
    uaa_post_force("/oauth/clients", payload, delete_id_fun)

def extract_unique_id (resources, filter_query = ""):
    resources = resources["resources"]
    if len(resources) != 1:
        filter_msg = " for query '{}'".format(filter_query) if filter_query else ""
        raise Exception("not exactly one resource, but {}{}: {}"
                        .format(len(resources),filter_msg, resources))
    else:
        return resources[0]["id"]

def quoted ( val ):
    return urllib.quote('"{}"'.format(val))

def unique_user_id ( user_name, email ):
    # filter_url='/Users?filter=userName+eq+{}+or+email+eq+{}'.format(quoted(user_name), quoted(email))
    filter_url='/Users?filter=userName+eq+{}+and+email+eq+{}'.format(quoted(user_name), quoted(email))
    return extract_unique_id(uaa_curl(filter_url), filter_url)

def unique_group_id ( display_name ):
    filter_url='/Groups?filter=displayName+eq+{}'.format(quoted(display_name))
    return extract_unique_id(uaa_curl(filter_url), filter_url)

for payload in user_payloads:
  primary_emails = [email["value"] for email in payload.get("emails", [])
                    if email["primary"]==True]
  user_name = payload["userName"]

  if not len(primary_emails)==1 or not user_name:
      raise Exception("must provide primary email and username: {}".format(payload))

  email = primary_emails[0]
  delete_id_fun = lambda user_name = user_name, email = email: unique_user_id(user_name, email)
  uaa_post_force("/Users", payload, delete_id_fun)



for payload in group_payloads:
  display_name = payload["displayName"]
  delete_id_fun = lambda display_name = display_name: unique_group_id(display_name)
  uaa_post_force("/Groups", payload, delete_id_fun)

for memberships in group_mems:
    display_name = memberships.get("group", {}).get("displayName")
    if not display_name:
        raise Exception("must provide enough properties to retrieve group uid")
    group_id = unique_group_id(display_name)
    for users in memberships.get("users", []):
        user_name = users.get("userName")
        email = users.get("email")
        if not user_name and not email:
            raise Exception("must provide enough properties to retrieve user uid")
        user_id = unique_user_id(user_name, email)
        payload = {"origin":"uaa",
                   "type":"USER",
                   "value":user_id}
        print ("adding {} to group {}".format(user_id, group_id), file = sys.stderr)
        uaa_curl("/Groups/{}/members".format(group_id), "POST", payload)

print ("{}")
