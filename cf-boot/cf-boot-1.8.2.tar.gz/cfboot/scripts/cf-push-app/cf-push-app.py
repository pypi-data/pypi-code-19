#!/usr/bin/python
from __future__ import print_function
import subprocess, os, json, random, sys, re
from os.path import realpath, join, dirname, exists

def check_output ( args, env ):
    "on exception, show output"
    p = subprocess.Popen(args, env = env,
                         stdout = subprocess.PIPE,
                         stderr = subprocess.PIPE)
    [out, err] = p.communicate()
    if p.returncode != 0:
        raise Exception("{} returned non-zero exit status {}\nstderr: {}"
                        .format(args, p.returncode, out+err))
    else:
        return out

def cf_target_info ( cf_home ):
    "obtain cf target info (api, org, space)"
    config_fn = join(cf_home, ".cf", "config.json")
    config = json.load(open(config_fn))
    return {"org": config["OrganizationFields"]["Name"],
            "space": config["SpaceFields"]["Name"],
            "space_guid": config["SpaceFields"]["GUID"]}

def create_dummy_app ( app_name, space_guid, child_env ):
    "POST an app object to cf. no upload or start"
    data = {"name" : app_name,
            "space_guid": space_guid,
            "memory": 1}
    subprocess.check_output(["cf", "curl", "/v2/apps",
                             "-X", "POST",
                             "-d", json.dumps(data)], env = child_env)

def url_basename ( git_url ):
    return os.path.splitext(os.path.basename(git_url))[0]

def git_clone_app ( git_url, proxy ):
    child_env = os.environ.copy()
    proxy = proxy or ""
    child_env["https_proxy"] = proxy
    child_env["http_proxy"] = proxy
    child_env["HTTPS_PROXY"] = proxy
    child_env["HTTP_PROXY"] = proxy

    app_clone_name = url_basename(git_url)
    deployer_apps = join("/tmp", "deployer-apps")
    if not exists(deployer_apps):
        os.mkdir(deployer_apps)

    path = join(deployer_apps, app_clone_name)

    if not exists(path):
        os.chdir(deployer_apps)
        check_output(["git", "clone", git_url], env = child_env)
        if not exists(path):
            raise Exception("git clone {} didn't create {} in {}"
                            .format(git_url, app_clone_name, os.getcwd()))
    else:
        # pull the latest changes
        os.chdir(path)
        check_output(["git", "pull", "origin", "master"],
                                env = child_env)
    return path

def cf_push_app ( app_name, path, child_env, host_name,
                  buildpack = None, stack = None, domain = None ):
    "push the app"
    cf_push_args = ["cf", "push", app_name,
                    "--no-start", "--no-manifest",
                    "-p", path,
                    "--hostname", host_name,
                    "-m", "500M"]
    if buildpack:
        cf_push_args += ["-b", buildpack]
    if stack:
        cf_push_args += ["-s", stack]
    if domain:
        cf_push_args += ["-d", domain]
    print ( " ".join(cf_push_args), file = sys.stderr )
    p = subprocess.Popen(cf_push_args, env = child_env, stdout=sys.stderr)
    p.wait()
    if p.returncode != 0:
        raise Exception("push failed: {}".format(" ".join(cf_push_args)))

def cf_bind_services ( app_name, services, child_env ):
    for instance_name in services:
        bind_args = ["cf", "bind-service", app_name, instance_name]
        print ( " ".join(bind_args), file = sys.stderr)
        check_output(bind_args, env = child_env)

def cf_set_envs ( app_name, envs_map, child_env ):
    for (k, v) in envs_map.iteritems():
        setenv_args = ["cf", "set-env", app_name, k, v]
        print ( " ".join(setenv_args), file = sys.stderr)
        check_output(setenv_args, env = child_env)

def cf_start ( app_name, child_env ):
    # start app
    # don't use check_output, which buffers entire output
    p = subprocess.Popen(["cf", "start", app_name],
                         env = child_env, stdout=sys.stderr)
    p.wait()
    if p.returncode != 0:
        raise Exception("cf start {} failed".format(app_name))

def main (  ):
    input_json = json.load(sys.stdin)

    cf_home = input_json.get("cf_home")
    app_name = input_json.get("app_name")
    git_url = input_json.get("git_url")

    if not cf_home:
        raise Exception( "missing cf_home")

    if not (app_name or git_url):
        raise Exception( "either app_name or git_url must be provided" )

    app_name = app_name or url_basename(git_url)

    child_env = os.environ.copy()
    child_env["CF_HOME"] = cf_home

    cf_target = cf_target_info(cf_home)
    cf_org = cf_target["org"]
    cf_space = cf_target["space"]
    cf_space_guid = cf_target["space_guid"]
    cf_org_sanitized = re.sub("[^a-zA-Z0-9-]", "-", cf_org)

    # git_url is optional. if not provided, use dummy "push"
    dummy = not git_url

    if dummy:
        # create an app for binding purposes only
        # save time on git clone, cf upload and app start
        create_dummy_app(app_name, cf_space_guid, child_env)
    else:
        # actual git clone, cf push
        no_proxy = input_json.get("git_clone_no_proxy")
        proxy = "" if no_proxy else os.environ.get("https_proxy")
        buildpack = input_json.get("buildpack")
        stack = input_json.get("stack")
        domain = input_json.get("domain")


        app_path = git_clone_app(git_url, proxy)
        host_name = "-".join([app_name, cf_org_sanitized, cf_space])

        cf_push_app(app_name, app_path, child_env, host_name,
                    buildpack = buildpack,
                    stack = stack,
                    domain = domain)



    services = input_json.get("services") or []
    cf_bind_services(app_name, services, child_env)


    if not dummy:
        # set requested environment variables
        envs = input_json.get("envs") or {}
        cf_set_envs(app_name, envs, child_env)

        cf_start(app_name, child_env)


    def cf_curl ( *args ):
        out = subprocess.check_output(["cf", "curl"] + list(args),
                                      env = child_env)
        return json.loads(out)

    # extract app guid and url
    resp = cf_curl("/v2/spaces/{}/apps?q=name:{}"
                   .format(cf_space_guid, app_name))

    app = resp["resources"][0]
    app_guid = app["metadata"]["guid"]

    url = None
    try:
        routes = cf_curl("/v2/apps/{}/routes".format(app_guid))["resources"]
        if routes:
            route = routes[0]
            route_host = route["entity"]["host"]
            domain_url = route["entity"]["domain_url"]
            domain_name = cf_curl(domain_url)["entity"]["name"]

            url = "https://{}.{}".format(route_host, domain_name)
    except:
        pass

    json.dump({"app_name" : app_name,
               "app_guid": app_guid,
               "app_url": url }, sys.stdout)

if __name__ == '__main__':
    main()
