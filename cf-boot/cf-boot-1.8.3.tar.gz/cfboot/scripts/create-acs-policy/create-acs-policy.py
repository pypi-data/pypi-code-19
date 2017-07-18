#!/usr/bin/python
import subprocess, json, base64, string, random, sys
from os.path import join, realpath, dirname
input_json = json.load(sys.stdin)

required = ["uaa_uri",
            "acs_client_id",
            "acs_client_secret",
            "acs_uri",
            "acs_zone",
            "acs_http_header_name",
            "acs_policy_payload"]

missing = filter(lambda key: key not in input_json, required)
if missing:
    raise Exception("missing input argument(s) {}"
                    .format(",".join(missing)))

uaa_uri = input_json["uaa_uri"]
acs_uri = input_json["acs_uri"]
acs_client_id = input_json["acs_client_id"]
acs_client_secret = input_json["acs_client_secret"]
acs_http_header_name = input_json["acs_http_header_name"]
acs_zone = input_json["acs_zone"]
acs_policy_payload = input_json["acs_policy_payload"]
acs_policy_name = acs_policy_payload["name"]

# base64_encode of client id and client secret
base64_encode = base64.b64encode("{0}:{1}".format(acs_client_id, acs_client_secret))

curl_uaa_uri = "{}/oauth/token?grant_type=client_credentials".format(uaa_uri)

authorization_field = "Authorization: Basic {}".format(base64_encode)

get_token_args = ["curl", "-sS", "-X", "GET", curl_uaa_uri,
                  "-H", authorization_field,
                  "-H", "Content-Type: application/x-www-form-urlencoded"]

response_json = subprocess.check_output(get_token_args)

response_dict = json.loads(response_json)

token = response_dict["access_token"]


# create acs policy with uaa token
acs_target = "{}/v1/policy-set/{}".format(acs_uri, acs_policy_name)
acs_zone = "{}:{}".format(acs_http_header_name, acs_zone)


self_dir = dirname(realpath(__file__))

authorization = "Authorization:bearer {}".format(token)

create_acs_policy_args = ["curl", "-sS", "-X", "PUT", acs_target,
                          "-d", json.dumps(acs_policy_payload),
                          "-H", authorization,
                            "-H", "Content-Type: application/json",
                            "-H", acs_zone]

p = subprocess.Popen(create_acs_policy_args, stdout=sys.stderr)
p.wait()

#must output valid json
print ( "{}" )
