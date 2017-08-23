# -*- coding: UTF-8 -*-
 
import sys
import argparse
import re
import os
import platform

from subprocess import call
import subprocess
import shlex

from os.path import exists
from os import makedirs

from build_scenarist.utility import cd, run
from build_scenarist.info import Info
from build_scenarist.config import bcolors

def getTargets(pathToScript):
    with open(pathToScript) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    # content = [x.strip() for x in content]
    # for i in content:
        # print i

    targetPositions = []
    for i, val in enumerate(content):
        # print i, val
        if bool(re.match("^(\[+.*\]+)$", val)):
            targetPositions.append(i)
    targetPositions
    # print targetPositions

    targets = {}
    fro=0
    to=0
    targetName="None"
    for i, val in enumerate(targetPositions):
        fro = targetPositions[i]+1
        if i+1 < len(targetPositions):
            to = targetPositions[i+1]
        else:
            to = len(content)
        targetName = content[targetPositions[i]][1:-2]
        targetCode = '\n'.join(content[fro:to])
        targets[targetName] = targetCode
    # print targets
    return targets

def targetsNotInScript(targets, pathToScript):
    targetsCode = getTargets(pathToScript)
    result = []
    for target in targets:
        if not(target in targetsCode):
            result.append(target)
    return result

def executeTargets(targets, pathToScript):
    notFoundTargets = targetsNotInScript(targets, pathToScript)
    isFaill = False
    if len(notFoundTargets) != 0:
        for target in notFoundTargets:
            isFaill = True
            print bcolors.FAIL + "\nError: Target %s not found in %s" % (target, pathToScript) + bcolors.ENDC
            sys.stdout.flush()

    if isFaill == False:
        targetsCode = getTargets(pathToScript)
        for target in targets:
            print bcolors.OKGREEN + "\nRun target " + target + " ..." + bcolors.ENDC
            sys.stdout.flush()
            exec(targetsCode[target])
    else:
        print bcolors.FAIL + "\nError: Please, specify existed targets name!" + bcolors.ENDC
        sys.stdout.flush()

def executeTargetsInImage(targets, pathToScript, image):
    notFoundTargets = targetsNotInScript(targets, pathToScript)
    isFaill = False
    if len(notFoundTargets) != 0:
        for target in notFoundTargets:
            isFaill = True
            print bcolors.FAIL + "\nError: Target %s not found in %s" % (target, pathToScript) + bcolors.ENDC
            sys.stdout.flush()

    if isFaill == False:
        run("""
            sudo docker run -v %s:/repo %s bash -exc '
                apt-get update
                apt-get -y install python2.7 python-setuptools

                hasPacket=$(apt-cache search python-pip)
                if [ -n "$hasPacket" ]; then
                    apt-get -y install python2.7 python-setuptools python-pip
                else
                    easy_install pip
                fi
                
                pip install build-scenarist

                cd /repo
                scenarist.py info
                scenarist.py run %s
            '
            """ % (os.getcwd(), image, " ".join(targets)))
    else:
        print bcolors.FAIL + "\nError: Please, specify existed targets name!" + bcolors.ENDC
        sys.stdout.flush()