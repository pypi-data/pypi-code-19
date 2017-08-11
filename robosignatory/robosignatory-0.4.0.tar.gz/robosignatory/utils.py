import abc
import pkg_resources
import subprocess
import koji

import logging
log = logging.getLogger('robosignatory.utils')


class Struct:
    def __init__(self, **entries):
            self.__dict__.update(entries)


def get_rpms(koji_client, build_nvr=None, build_id=None, sigkey=None):
    if not build_id:
        build_id = koji_client.findBuildID(build_nvr)
    rpms = koji_client.listRPMs(build_id)
    rpminfo = {}
    for rpm in rpms:
        info = {'id': rpm['id']}
        if sigkey:
            sigs = koji_client.queryRPMSigs(rpm_id=rpm['id'],
                                            sigkey=sigkey)
            info['signed'] = len(sigs) != 0
        rpminfo['%s.%s' % (rpm['nvr'], rpm['arch'])] = info
    return rpminfo

def get_builds_in_tag(koji_client, tag):
    """ Return the list of builds in Koji tag. """

    try:
        rpms, builds = koji_client.listTaggedRPMS(tag, latest=True)
    except koji.GenericError as e:
        log.exception("Failed to list rpms in tag %r" % tag)
        # If the tag doesn't exist.. then there are no rpms in that tag.
        return []

    return builds


def run_command(command):
    child = subprocess.Popen(command, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    stdout, stderr = child.communicate()
    ret = child.wait()
    return ret, stdout, stderr


def get_signing_helper(backend, *args, **kwargs):
    """ Instantiate and return the appropriate signing backend. """
    points = pkg_resources.iter_entry_points('robosignatory.signing.helpers')
    classes = dict([(point.name, point.load()) for point in points])
    log.debug("Found the following installed signing helpers %r" % classes)
    cls = classes[backend]
    log.debug("Instantiating helper %r from backend key %r" % (cls, backend))
    return cls(*args, **kwargs)


class BaseSigningHelper(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def build_cmdline(self, *args):
        pass

    @abc.abstractmethod
    def build_sign_cmdline(self, *args):
        pass

    @abc.abstractmethod
    def build_atomic_cmdline(self, *args):
        pass


class EchoHelper(BaseSigningHelper):
    """ A dummy "hello world" helper, used for debugging. """
    def __init__(self, *args, **kwargs):
        log.info("Constructing EchoHelper(%r, %r)" % (args, kwargs))

    def build_cmdline(self, *args, **kwargs):
        result = ['echo', ' '.join(['build_cmdline:', str(args), str(kwargs)])]
        log.info(result)
        return result

    def build_sign_cmdline(self, *args, **kwargs):
        result = ['echo', ' '.join(['build_sign_cmdline:', str(args), str(kwargs)])]
        log.info(result)
        return result

    def build_atomic_cmdline(self, *args, **kwargs):
        result = ['echo', ' '.join(['build_atomic_cmdline:', str(args), str(kwargs)])]
        log.info(result)
        return result


class SigulHelper(BaseSigningHelper):
    def __init__(self, user, passphrase_file, config_file=None):
        self.user = user
        self.passphrase_file = passphrase_file
        self.config_file = config_file

    def build_cmdline(self, *args):
        cmdline = ['sigul', '--batch', '--user-name', self.user,
                   '--passphrase-file', self.passphrase_file]
        if self.config_file:
            cmdline.extend(["--config-file", self.config_file])
        cmdline.extend(args)
        return cmdline

    def build_sign_cmdline(self, key, rpms, koji_instance=None):
        if len(rpms) == 1:
            sigul_cmd = "sign-rpm"
        else:
            sigul_cmd = "sign-rpms"

        command = self.build_cmdline(sigul_cmd, '--store-in-koji',
                                     '--koji-only')
        if koji_instance:
            command.extend(['-k', koji_instance])

        # TODO: See if this always needs to be set or optional
        # if self.v3:
        command.append('--v3-signature')

        command.append(key)

        return command + rpms

    def build_atomic_cmdline(self, key, checksum, input_file, output_file):
        command = self.build_cmdline('sign-ostree', key, checksum, input_file,
                                     '--output', output_file)
        return command
