#!/usr/bin/python
from __future__ import print_function
import subprocess, os, json, random, sys
import time, re
from os.path import join

input_json = json.load(sys.stdin)

required_input = ["instance_name",
            	  "service",
            	  "plan",
            	  "cf_home"]

missing = filter(lambda key: key not in input_json, required_input)
if missing:
    raise Exception("missing input argument(s) {}"
                    .format(",".join(missing)))

#optional payload argument
payload_args = []
if "payload" in input_json:
		payload_args = ["-c", json.dumps(input_json["payload"])]


if_exists = input_json.get("if_exists", "ignore")
IF_EXIST_OPTS = ("ignore", "delete", "update")
if if_exists not in IF_EXIST_OPTS:
    raise Exception("if_exists must be one of {}".format(IF_EXIST_OPTS))


def cf_home_space_guid ( cf_home ):
    "obtain cf target info (api, org, space)"
    config_fn = join(cf_home, ".cf", "config.json")
    config = json.load(open(config_fn))
    return config["SpaceFields"]["GUID"]

cf_home = input_json["cf_home"]
service_label = input_json["service"]
service_plan = input_json["plan"]
instance_name = input_json["instance_name"]
space_guid = cf_home_space_guid(cf_home)

child_env = os.environ.copy()
child_env["CF_HOME"] = cf_home

def cf_curl ( *args ):
    full_args = ["cf", "curl"] + list(args)
    out = subprocess.check_output(full_args, env = child_env)
    return json.loads(out)

def subprocess_call ( args ):
    p = subprocess.Popen(args, env = child_env, stdout = sys.stderr)
    p.wait()
    if p.returncode != 0:
        raise Exception("subprocess {} had non-zero exit"
                    .format(args))


def instance_guid ( cf_home, instance_name, space_guid ):
    out = cf_curl("/v2/spaces/{}/service_instances?q=name:{}"
                  .format(space_guid, instance_name))
    if out["total_results"]:
        guid = out["resources"][0]["metadata"]["guid"]
        return guid

#  check if instance exists
guid = instance_guid(cf_home, instance_name, space_guid)
create_or_update = "create-service"

if guid:
    if if_exists=="ignore":
        print ("service already exists. skipping... {}".format(instance_name), file = sys.stderr)
        print (json.dumps({"SERVICE_GUID" : guid}))
        exit(0)
    elif if_exists=="delete":
        # if if_exists=="force_delete":
        if True:
            print ("deleting bindings for {}...".format(instance_name), file = sys.stderr)
            bindings = cf_curl("/v2/service_instances/{}/service_bindings"
                                    .format(guid))
            binding_guids = [binding["metadata"]["guid"] for binding in bindings["resources"]]
            for binding_guid in binding_guids:
                # does not return valid JSON, cannot use cf_curl
                subprocess_call(["cf", "curl", "-X", "DELETE",
                                      "/v2/service_bindings/{}".format(binding_guid)])

        print ("deleting {}...".format(instance_name), file = sys.stderr)
        subprocess_call(["cf", "delete-service", "-f", instance_name])
    elif if_exists=="update":
        print ("updating {}...".format(instance_name), file = sys.stderr)
        create_or_update = "update-service"
    else:
        assert(False)

if create_or_update=="create-service":
    args = ["cf", "create-service", service_label, service_plan, instance_name]\
       + payload_args
elif create_or_update=="update-service":
    args = ["cf", "update-service", instance_name, "-p", service_plan ]\
       + payload_args

subprocess_call(args)

guid = instance_guid(cf_home, instance_name, space_guid)
if guid==None:
    raise Exception("service instance {} was not created".format(instance_name))

DELAY_SECS = 10
#  wait for possibly async provisioning
while True:
    out = subprocess.check_output(
            ["cf", "curl", "v2/service_instances/{}".format(guid)],
            env = child_env)
    last_operation = json.loads(out)["entity"]["last_operation"]
    (op_type, op_status) = last_operation["type"], last_operation["state"]
    if op_type=="create" and op_status=="progress":
        print ("provisioning in progress: {} {}. sleeping for {} secs..."
               .format(op_type, op_status, DELAY_SECS),
               file = sys.stderr)
        time.sleep(DELAY_SECS)
    else:
        break

print (json.dumps({"SERVICE_GUID" : guid}))
