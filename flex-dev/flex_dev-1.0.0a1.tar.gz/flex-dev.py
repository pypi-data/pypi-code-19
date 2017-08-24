import json
import subprocess
import sys

import os


def install_docker():
    subprocess.call("brew install wget", shell=True)
    subprocess.call('wget https://download.docker.com/mac/stable/Docker.dmg', shell=True)
    subprocess.call("hdiutil mount Docker.dmg", shell=True)
    subprocess.call("cp -R /Volumes/Docker/Docker.app /Applications", shell=True)
    subprocess.call("hdiutil unmount /Volumes/Docker/", shell=True)
    print "You can close the window prompting you to copy Docker to Applications."
    subprocess.call("open -a Docker", shell=True)
    subprocess.call("rm Docker.dmg", shell=True)
    subprocess.call("pip install --user --upgrade awscli", shell=True)
    print "Installed all dependencies. Will attempt to perform initial configuration"
    configure()


def run_in_shell(cmd):
    subprocess.call(cmd, shell=True)


def get_local_config():
    with open(os.path.expanduser('~/.flex_dev')) as data_file:
        data = json.load(data_file)
    return data


def configure():
    run_in_shell("mkdir ~/.aws")
    config = get_local_config()
    server_url = config["config_server_url"]
    server_user = config["config_server_user"]
    run_in_shell("scp {}@{}:aws_docker_read_config ~/.aws/config".format(server_user, server_url))
    run_in_shell("scp {}@{}:aws_docker_read_credentials ~/.aws/credentials".format(server_user, server_url))
    print "Configuration complete!"


def get_micro_dump():
    aws_docker_login_command = subprocess.check_output("aws ecr get-login --no-include-email --region us-west-1", shell=True)
    run_in_shell(aws_docker_login_command)
    run_in_shell("brew services stop postgresql")
    config = get_local_config()
    docker_registry_url = config["docker_registry_url"]
    run_in_shell("docker run -d --rm --name flex_db {}/flexdb".format(docker_registry_url))


if __name__ == "__main__":
    arguments = sys.argv
    if arguments[1] == "install":
        install_docker()
    elif arguments[2] == "configure":
        configure()
    elif arguments[3] == "micro_dump":
        get_micro_dump()