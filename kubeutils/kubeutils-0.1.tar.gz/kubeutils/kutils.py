#!/usr/bin/env python

import os
import shlex
import subprocess
import sys

from kubernetes import client, config

config.load_kube_config()

dir_path = os.path.dirname(os.path.realpath(__file__))

class ArgvConsumer:
  def __init__(self):
    self.position = 1

  def done(self):
    return self.position >= len(sys.argv)

  def get_value(self, value_name):
    if self.done():
      print 'Missing argument: %s.' % value_name
      sys.exit(0)

    ret = sys.argv[self.position]
    self.position += 1
    return ret

def get_script_path(script_name):
  script_path = os.path.join(dir_path, "scripts/%s" % script_name)
  return script_path
  

def print_commands(with_intro=True):
  if with_intro:
    print 'kubeutils is a set of Kubernetes utility commands.'
    print
  print 'Commands:'
  print '  %-16s %s' % ('ssh', 'SSH to a pod')
  print '  %-16s %s' % ('podmaps', 'Print mapping from pod name to node name')
  print
  print 'Kubernetes on Google Container Engine (GKE) commands:'
  # print '  %-16s %s' % ('resize-wait', 'Resizes a cluster and waits until resize is done')
  print '  %-16s %s' % ('instance-group', 'Get instance group name for a cluster')
  print '  %-16s %s' % ('node-count', 'Get number of nodes in a cluster')
  print

def ssh_to(pod_name):
  print 'SSH-ing to %s' % pod_name
  command = "kubectl exec -ti %s bash" % pod_name
  ret = subprocess.call(shlex.split(command))
  return ret

def command_ssh():
  v1 = client.CoreV1Api()
  ret = v1.list_pod_for_all_namespaces(watch=False)

  name = None
  if not argv.done():
    name = argv.get_value('name')

  candidates = []
  for i in ret.items:
    if i.metadata.namespace != 'kube-system':
      if (not name) or (name in i.metadata.name):
        candidates.append(i.metadata.name)

  if len(candidates) == 0:
    print "No pods found with that name."
  elif len(candidates) == 1:
    ssh_to(candidates[0]);
  else:
    print "Multiple pods found:"
    for i in range(0, len(candidates)):
      print "%d) %s" % (i, candidates[i])
    choice = raw_input("Choice: ")
    index = int(choice)

    ssh_to(candidates[index]);


def command_podmaps():
  extra_params = ' '.join(sys.argv[2:])
  command = "kubectl get pods %s -o jsonpath='{range .items[*]}{.metadata.name} {.spec.nodeName}|{end}'" % extra_params
  output = subprocess.check_output(shlex.split(command))
  pods = output.split('|')[:-1]
  for pod in pods:
    (pod_name, node_name) = pod.split(' ')
    print '%-50s : %s' % (pod_name, node_name)


def command_instance_group():
  script_path = get_script_path("instance-group.sh")

  cluster = argv.get_value("cluster")

  ret = subprocess.check_output(shlex.split(script_path + " " + cluster))
  print ret,

def command_node_count():
  script_path = get_script_path("node-count.sh")

  cluster = argv.get_value("cluster")

  ret = subprocess.check_output(shlex.split(script_path + " " + cluster))
  print ret,


def main():
  global argv
  name = None
  argv = ArgvConsumer()

  command_handlers = {
    'ssh': command_ssh,
    'podmaps': command_podmaps,
    'instance-group': command_instance_group,
    'node-count': command_node_count
  }

  if argv.done():
    print_commands()
  else:
    name = argv.get_value("command")

    if not name in command_handlers.keys():
      print 'Invalid command: %s.' % name
      print
      print_commands(with_intro=False)

    handler = command_handlers[name]
    handler()
