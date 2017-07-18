#!/usr/bin/python
from __future__ import print_function
import subprocess, os, json, sys

input_json = json.load(sys.stdin)

required_input = ["instance_name",
            	  "service",
            	  "plan",
            	  "cf_home"]

missing = filter(lambda key: key not in input_json, required_input)
if missing:
    raise Exception("missing input argument(s) {}"
                    .format(",".join(missing)))

#  enhance our own PATH with subscripts
os.environ["PATH"] += ":" + os.getenv("CFBOOT_PATH")
child_env = os.environ.copy()

instance_name = input_json.get("instance_name")

def subscript_call ( subscript_exe, json_obj_input ):
    # call subscript with json_obj_input. return output map
    p = subprocess.Popen([subscript_exe], env = child_env,
                     stdout = subprocess.PIPE,
                     stdin = subprocess.PIPE)
    json.dump(json_obj_input, p.stdin)
    p.stdin.close() #EOF
    p.wait()
    if p.returncode != 0:
        raise Exception("{} failed".format(subscript_exe))
    return json.load(p.stdout)

print ("creating service...".format(), file = sys.stderr )
output = subscript_call("create-service.py", input_json)
print ("done creating service...".format(), file = sys.stderr )

if "credential_paths" in input_json:
    print ("creating dummy app...".format(), file = sys.stderr )
    dummy_app_json = subscript_call("cf-push-app.py",
                                    {"app_name": "cf-boot-refapp",
                                     "cf_home": input_json["cf_home"]})
    
    print ("extracting service credentials for {}...".format(instance_name),
           file = sys.stderr)
    creds = subscript_call("extract-service-credentials.py",
                           {"app_guid": dummy_app_json["app_guid"],
                            "service_instance_guid": output["SERVICE_GUID"],
                            "cf_home": input_json["cf_home"],
                            "credential_paths": input_json["credential_paths"]})

    # need to leave credentials at the top level to enable their extraction in project specs
    # output["credentials"] = creds
    overwriten = set(output.keys()).intersection(creds.keys())
    if overwriten:
        raise Exception("credential keys overwriting: {}"
                        .format(overwriten))

    output.update(creds)
    
json.dump(output, sys.stdout, indent = 2)
