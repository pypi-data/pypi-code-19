#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import DEFAULT_STR_EMPTY
from ..inmem_store import ENTRY_DICT
from ..utils.misc import getOrgname, doSkipImageRebuild
from ..utils.config import KEY_SDKBASE, KEY_STAGEDIR, SECTION_WB

import os
import string
import subprocess

DIRNAME = os.path.dirname(os.path.realpath(__file__))
SCRIPT_PATH = os.path.abspath(os.path.join(DIRNAME, '..', '..', 'build', 'image',
                                           'image_snapshot.sh'))

class ImageBuild(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'build')

    def getSubcmdDescripton(self):
        return 'Build a catalog image from a Dockerfile.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('-b', '--basedir', metavar='BASEDIR', type=str,
                               required=True, action="store",
                               help='Directory path where the Dockerfile and '
                                    'related files are located.')
        subparser.add_argument('-d', '--distroid', metavar='DISTRO_ID', type=str,
                               required=False, action='store', default=None,
                               help="EPIC catalog entry's distro id to which this "
                               "image will be assigned to. If a catalog entry "
                               "is either loaded or is being created in the "
                               "current workbench session, this option is not "
                               "required.")
        subparser.add_argument('-v', '--imgversion', metavar='IMAGE_VERSION',
                               type=str, dest='version', required=True,
                               help='Container Image version in the form of a '
                                    '"major.minor" string.')
        subparser.add_argument('--os', metavar="OS", dest="os", required=True,
                               choices=['centos6', 'rhel6', 'centos7', 'rhel7',
                                        'ubuntu16'], action='store',
                               help="The OS distribution of the container image.")

    def run(self, pargs):
        stagingDir = self.config.get(SECTION_WB, KEY_STAGEDIR)
        sdkBase = self.config.get(SECTION_WB, KEY_SDKBASE)
        scriptPath = os.path.join(sdkBase, "appbuild", "image", "image_snapshot.sh")

        if not os.path.exists(stagingDir):
            os.makedirs(stagingDir)

        absBaseDir = os.path.abspath(pargs.basedir)
        if not os.path.exists(absBaseDir):
            print("ERROR: '%s' does not exist.")
            return False

        ## Construct the nametag options for building it. We need three pieces
        ## for that: orgname/distroid:version

        if pargs.distroid == None:
            entryDict = self.inmemStore.getDict(ENTRY_DICT)
            if entryDict.has_key('distro_id'):
                distroid = entryDict['distro_id']
            else:
                print ("ERROR: Either -d/--distroid must be specified or a "
                       "catalog entry with a valid distroid specification "
                       "must be loaded.")
                return False
        else:
            orgname = getOrgname(self.inmemStore, self.config)
            if orgname == None:
                return False

            distroid = "%s/%s" % (orgname, pargs.distroid)


        nametag = "%s-%s:%s" %(distroid, pargs.os, pargs.version)
        destFilename = nametag.replace('/', '-').replace(':','-')
        destPath = os.path.join(stagingDir, "%s%s" % (destFilename, ".tar.gz"))
        md5File = destPath + '.md5sum'

        if not doSkipImageRebuild(destPath, md5File):
            script = ["bash", scriptPath,
                        "--basedir", absBaseDir,
                        "--nametag", nametag,
                        "--filename", destPath]

            try:
                subprocess.check_call(' '.join(script), shell=True,
                                      stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as cpe:
                print(cpe)
                return False

        try:
            with open(md5File, 'r') as mf:
                md5 = mf.readline().split()[0]

            return self.workbench.onecmd(str("image file --filepath %s --md5sum %s --os %s"
                                                %(destPath, md5, pargs.os)))
        except:
            return self.workbench.onecmd(str("image file --filepath %s --os %s"
                        %(destPath, pargs.os)))

        return True

    def complete(self, text, argsList):
        return []
