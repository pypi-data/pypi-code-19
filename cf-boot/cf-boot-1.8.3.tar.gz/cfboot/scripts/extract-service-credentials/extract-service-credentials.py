#!/usr/bin/python
from __future__ import print_function
import subprocess, os, json, random, sys

input_json = json.load(sys.stdin)

required = ["cf_home",
	    "app_guid",
	    "service_instance_guid",
	    "credential_paths"]

missing = set(required).difference(set(input_json.keys()))

if missing:
    raise Exception("missing input argument(s) {}"
                    .format(",".join(missing)))


app_guid = input_json["app_guid"]
service_instance_guid = input_json["service_instance_guid"]
credential_paths = input_json["credential_paths"]

child_env = os.environ.copy()
child_env["CF_HOME"] = input_json["cf_home"]

#bind service
bind_service_payload = {"service_instance_guid" : service_instance_guid,
                        "app_guid" : app_guid}

def cf_curl ( *args ):
    out = subprocess.check_output(args, env = child_env)
    return json.loads(out)

bs_output = cf_curl("cf", "curl", "/v2/service_bindings",
		    "-X", "POST",
		    "-d", json.dumps(bind_service_payload))

if "error_code" in bs_output and\
not bs_output["error_code"]=="CF-ServiceBindingAppServiceTaken":
		raise Exception("bind service failed: {}".format(bs_output))


# get binding
bindings = cf_curl("cf", "curl",
                   "/v2/apps/{}/service_bindings?q=service_instance_guid:{}"
		   .format(app_guid, service_instance_guid))

if len(bindings["resources"]) != 1:
    raise Exception("""there should be exactly one
    binding for (app, service_instance) pair""")

credentials = bindings["resources"][0]["entity"]["credentials"]

output = {}
for key, path in credential_paths.iteritems():
    if not isinstance(path, list):
        path = [path]
    try:
        val = reduce(lambda cum, k: cum[k], path, credentials)
    except Exception as e:
        print("invalid credential path: {}, {}".format(path, credentials),
              file=sys.stderr)
        raise e

    output[key] = val

json.dump(output, sys.stdout)
