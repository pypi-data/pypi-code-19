from subprocess import *
import subprocess
import paramiko
from socket import *
import time
import os
import datetime as dt
import threading
import ssl
import sys
import sh
import requests
from tempfile import mkstemp
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from colorama import init
init()  # make ansi terminal codes work on win32


class MyAdapter(HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block=False):
        ca_certs = "/etc/ssl/certs/ca-certificates.crt"
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       cert_reqs='CERT_REQUIRED',
                                       ca_certs=ca_certs,
                                       ssl_version=ssl.PROTOCOL_SSLv3)
http = requests.Session()
http.mount('https://', MyAdapter())


class Timer:

    def __init__(self):
        self.start = dt.datetime.now()

    def __str__(self):
        return str(dt.datetime.now() - self.start)

    def __repr__(self):
        return str(dt.datetime.now() - self.start)


class bgcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


from colors import black,  green, yellow, blue, magenta, cyan, white, color


def format_bytes(mem):
    if mem is None:
        return ""
    return '{0:.2f}GB'.format(float(mem) / 1024)


def format_mem(mem):
    if mem is None:
        return ""
    return '{0:.2f}GB'.format(float(mem)/1024)


def format_space(space):
    if space is None:
        return ""
    return str(space/1024/1024/1024) + "GB"


def get_colored_percent(percentage, factor=1):
    if percentage > 90 / factor:
        percentage = colored("%.0f%%" % percentage, 'red')
    elif percentage > 70 / factor:
        percentage = colored("%.0f%%" % percentage, 'yellow')
    else:
        percentage = colored("%.0f%%" % percentage, 'green')
    return "@ %s" % (percentage)


def white(s):
    return s


def orange(s):
    return color(s, fg=3)


def gray(msg):
    return color(msg, fg=242)


def red(msg):
    return color(msg, fg=196)


def print_info(str):
    sys.stderr.write(bgcolors.HEADER + str + bgcolors.ENDC)


def print_ok(str):
    sys.stderr.write(green(str))


def print_fail(str):
    sys.stderr.write(red(str))


def ping(host, port):
    s = socket(AF_INET, SOCK_STREAM)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception, e:
        s.close()
        return False


def call_async(func, args):
    t = threading.Thread(target=func, args=args)
    t.daemon = True
    t.start()

    def null():
        pass

    return null


def stream_process_results(p, prefix=''):
    out = ""
    while True:
        line = p.stdout.readline()
        if not line:
            p.poll()
            print_info("[%s] " % prefix)
            print_ok(line + "\n")
            if p.returncode == 0:
                print_info(prefix + " ")
                print_ok("[0]\n")
            else:
                print_info(prefix + " ")
                print_fail("[%s]" % p.returncode + "\n")

            print


def print_process_result(p, prefix='', full=False):
    out = ""
    while True:
        line = p.stdout.readline()
        if not line:
            p.poll()
            if p.returncode == 0:
                print_info(prefix + " ")
                print_ok("[0]\n")
                if full:
                    print out
            else:
                print_info(prefix + " ")
                print_fail("[%s]" % p.returncode + "\n")
                print out
            return out
        out += line + "\n"


def print_process(p, prefix=''):
    while True:
        line = p.stdout.readline()
        if not line:
            p.poll()
            if p.returncode == 0:
                print_info(prefix + " ")
                print_ok("[0]\n")
            else:
                print_info(prefix + " ")
                print_fail("[%s]" % p.returncode + "\n")
            return p.returncode
        print line


def print_response(r):
    if r.status_code >= 200 and r.status_code < 300:
        print_ok(str(r.status_code) + "\n")
    else:
        print_fail("[%s]\n %s\n" % (str(r.status_code), r.text))


def http_post(url, data, headers={}, username=None, password=None, cookies=None):
    try:

        print_info(url + " ..  ")
        headers['User-Agent'] = 'Mozilla'
        r = requests.post(url, data=data, verify=False, auth=(
            username, password), headers=headers, allow_redirects=False, cookies=cookies)
        if r.status_code > 300 and r.status_code < 400:
            print_ok(" -> " + r.headers['Location'] + "\n")
            return http_post(r.headers['Location'], data=data, headers=headers, username=username, password=password, cookies=cookies)
        print_response(r)
        return r
    except Exception, e:
        print_fail(str(e))


def http_get(url, username=None, password=None, cookies=None):
    try:
        print_info(url + " ..  ")
        r = requests.get(url, verify=False, headers={"User-Agent": 'Mozilla'}, auth=(
            username, password), cookies=cookies,  allow_redirects=False)
        if r.status_code > 300 and r.status_code < 400:
            print_ok(" -> " + r.headers['Location'] + "\n")
            return http_get(r.headers['Location'],  username, password, cookies)
        print_response(r)
        return str(r.text)
    except Exception, e:
        print_fail(str(e))


def execute(command, async=False,  env=os.environ):
    print_info("executing ")
    print command

    p = Popen(command, stdout=subprocess.PIPE, shell=True, env=os.environ)
    if async:
        call_async(print_process_result, [p, command])
    else:
        return print_process_result(p, command)


def execute_ssh(host, username, password, cmd):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(host, username=username, password=password)
    print cmd
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
    print ssh_stderr.readlines()
    print ssh_stdout.readlines()


def ansible_playbook(playbook, host, inventory=None, extra_vars=None, group=None, private_key_file=None, remote_user=None):
    print "running play %s on %s" % (playbook, host)
    ansible = sh.Command('ansible-playbook')
    args = [playbook, "-l", host]
    if inventory != None:
        args.append("-i")
        args.append(inventory)
    if extra_vars != None:
        for k, v in extra_vars.items():
            args.append('-e')
            args.append("%s=%s" % (k, v))

    print args

    def out(line):
        sys.stdout.write(blue(playbook) + gray("/" + host) + " " + line)
    ansible(args, _out=out, _err=out)


def read(path):
    with open(path, 'r') as f:
        return f.read()


def wait(condition, sleep=1):
    result = condition()
    while result is False:
        result = condition()
        time.sleep(sleep)


def async(func, args):
    t = threading.Thread(target=func, args=args)
    t.daemon = True
    t.start()

    def null(args):
        pass

    return null
