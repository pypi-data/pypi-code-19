import fedmsg.config
import koji
import sys

from robosignatory.tagconsumer import TagSignerConsumer
import robosignatory.utils as utils
import robosignatory.work

import logging
logging.basicConfig(level=logging.INFO)


def buildsigner():
    if len(sys.argv) != 4:
        print 'Usage: %s <koji-instance> <build-nvr> <key>' % sys.argv[0]
        sys.exit(1)

    koji_instance = sys.argv[1]
    build_nvr = sys.argv[2]
    key = sys.argv[3]

    config = fedmsg.config.load_config()

    if koji_instance not in config['robosignatory.koji_instances'].keys():
        print 'Koji instance %s not configured' % koji_instance
        sys.exit(1)

    koji_session = koji.ClientSession(
        config['robosignatory.koji_instances'][koji_instance]['url'])

    signing_config = self.hub.config['robosignatory.signing']
    signer = utils.get_signing_helper(**signing_config)

    rpms = utils.get_rpms(koji_session, build_nvr)
    print 'Signing %s' % ', '.join(rpms)

    cmd_line = signer.build_sig_cmdline(key, rpms, koji_instance)

    ret, stdout, stderr = utils.run_command(cmd_line)
    if ret != 0:
        print 'Something went wrong signing!'
        print 'Error code: %s' % ret
        print 'Output: %s' % stdout
        print 'Error: %s' % stderr


def tagsigner():
    if len(sys.argv) != 5:
        print 'Usage: %s <koji-instance> <build-nvr> <curtag> <skiptag>' % sys.argv[0]
        print 'skiptag: yes or no'
        sys.exit(1)

    koji_instance = sys.argv[1]
    build_nvr = sys.argv[2]
    curtag = sys.argv[3]
    skiptag = sys.argv[4] == 'yes'

    signer = TagSignerConsumer(None)
    signer.dowork(build_nvr, None, curtag, koji_instance, skiptag)


def atomicsigner():
    if len(sys.argv) != 3:
        print 'Usage: %s <ref> <commitid>' % sys.argv[0]
        sys.exit(1)

    ref = sys.argv[1]
    commitid = sys.argv[2]

    config = fedmsg.config.load_config([], None)

    signing_config = self.hub.config['robosignatory.signing']
    signer = utils.get_signing_helper(**signing_config)

    if ref not in config['robosignatory.ostree_refs']:
        print 'Ref %s not found' % ref
        sys.exit(1)

    val = config['robosignatory.ostree_refs'][ref]

    robosignatory.work.process_atomic(signer, ref, commitid, **val)

def modulesigner():
    if len(sys.argv) != 3:
        print 'Usage: %s <koji-instance> <module-tag>' % sys.argv[0]
        sys.exit(1)

    koji_instance = sys.argv[1]
    tag = sys.argv[2]

    signer = TagSignerConsumer(None)
    signer.sign_modular_tag(koji_instance, tag)
