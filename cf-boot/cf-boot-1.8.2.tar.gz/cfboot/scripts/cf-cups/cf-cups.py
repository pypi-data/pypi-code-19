#!/usr/bin/python
import subprocess, os, json, random, sys
from subprocess import Popen, check_output

DEVNULL = open(os.devnull, 'wb')

input_json = json.load(sys.stdin)

required_input = ["instance_name",
				  "credentials", "cf_home"]

missing = filter(lambda key: key not in input_json, required_input)
if missing:
    raise Exception("missing input argument(s) {}"
                    .format(",".join(missing)))

instance_name = input_json["instance_name"]

#optional payload argument

child_env = os.environ.copy()
child_env["CF_HOME"] = input_json["cf_home"]

Popen(["cf", "create-user-provided-service", instance_name],
                     env = child_env, stdout = DEVNULL, stderr = DEVNULL).wait()
#it's ok to fail above, as long as we can successfuly get the guid
guid = check_output(
		["cf", "service", instance_name, "--guid"],
		env = child_env).rstrip()

#perform update
update_payload = { k: input_json[k] for k in
                   ["route_service_url", "syslog_drain_url", "credentials"]
                   if k in input_json}

args = ["cf", "curl",
                  "/v2/user_provided_service_instances/{}".format(guid),
		"-X", "PUT", "-d", json.dumps(update_payload)]
p = Popen(args, env = child_env, stdout = DEVNULL, stderr = sys.stderr)
p.wait()

if p.returncode != 0:
    raise Exception("updating user-provided service failed with args"
                    .format(args))

print (json.dumps({"SERVICE_GUID" : guid}))
