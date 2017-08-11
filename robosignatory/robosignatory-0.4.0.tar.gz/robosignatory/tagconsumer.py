import koji

import fedmsg
import fedmsg.consumers
import robosignatory.utils as utils

import logging
log = logging.getLogger("robosignatory.tagconsumer")

class MultipleStreamsError(ValueError):
    pass

class TagSignerConsumer(fedmsg.consumers.FedmsgConsumer):
    config_key = 'robosignatory.enabled.tagsigner'

    def __init__(self, hub):
        if hub:
            super(TagSignerConsumer, self).__init__(hub)
            self.config = self.hub.config
        else:
            # No hub, we are in ad-hoc mode
            self.config = fedmsg.config.load_config()
            logging.basicConfig(level=logging.DEBUG)

        prefix = self.config.get('topic_prefix')
        env = self.config.get('environment')
        self.topic = [
            '%s.%s.buildsys.tag' % (prefix, env)
        ]

        self.module_prefixes = \
            tuple(self.config['robosignatory.module_prefixes'])

        signing_config = self.config['robosignatory.signing']
        self.signer = utils.get_signing_helper(**signing_config)

        self.koji_clients = {}
        for instance in self.config['robosignatory.koji_instances']:
            instance_info = self.config[
                'robosignatory.koji_instances'][instance]
            client = koji.ClientSession(instance_info['url'],
                                        instance_info['options'])

            if instance_info['options']['authmethod'] == 'ssl':
                client.ssl_login(instance_info['options']['cert'],
                                 None,
                                 instance_info['options']['serverca'])
            elif instance_info['options']['authmethod'] == 'kerberos':
                kwargs = {}
                for opt in ('principal', 'keytab', 'ccache'):
                    if opt in instance_info['options']:
                        kwargs[opt] = instance_info['options'][opt]
                client.krb_login(**kwargs)
            else:
                raise Exception('Only SSL and kerberos authmethods supported')

            instance_obj = {'client': client,
                            'tags': {},
                            'module_key': None,
                            'module_keyid': None}
            for tag in instance_info['tags']:
                if tag['from'] in instance_obj['tags']:
                    raise Exception('From detected twice: %s' % tag['from'])
                instance_obj['tags'][tag['from']] = {'to': tag['to'],
                                                     'key': tag['key'],
                                                     'keyid': tag['keyid']}

            if ("module_key" in instance_info
                    and "module_keyid" in instance_info):
                instance_obj["module_key"] = instance_info["module_key"]
                instance_obj["module_keyid"] = instance_info["module_keyid"]

            self.koji_clients[instance] = instance_obj

            log.info('TagSignerConsumer ready for service')

    def consume(self, msg):
        topic = msg['topic']
        if topic not in self.topic:
            return

        msg = msg['body']['msg']

        #  {u'build_id': 799208,
        #   u'name': u'python-fmn-rules',
        #   u'tag_id': 374,
        #   u'instance': u'primary',
        #   u'tag': u'epel7-infra',
        #   u'user': u'puiterwijk',
        #   u'version': u'0.9.1',
        #   u'owner': u'sayanchowdhury',
        #   u'release': u'1.el7'}}

        build_nvr = '%(name)s-%(version)s-%(release)s' % msg
        build_id = msg['build_id']
        tag = msg['tag']
        koji_instance = msg['instance']

        log.info('Build %s (%s) tagged into %s on %s',
                 build_nvr, build_id, tag, koji_instance)

        if koji_instance not in self.koji_clients:
            log.info('Koji instance not known, skipping')
            return

        instance = self.koji_clients[koji_instance]
        if tag in instance['tags']:
            self.dowork(build_nvr, build_id, tag, koji_instance,
                        skip_tagging=False)
        elif tag.startswith(self.module_prefixes):
            self.sign_modular_rpms(build_nvr, build_id, tag, koji_instance)

    def sign_modular_rpms(self, build_nvr, build_id, tag, koji_instance):
        # Skip the -build tag.
        if tag.endswith("-build"):
            log.info("Skipping build tag %s" % tag)
            return

        instance = self.koji_clients[koji_instance]
        if not instance["module_key"] or not instance["module_keyid"]:
            log.info("Skipping tag %s - module_key or module_keyid not "
                     "defined." % tag)
            return

        tag_info = {}
        tag_info["to"] = tag
        tag_info["key"] = instance["module_key"]
        tag_info["keyid"] = instance["module_keyid"]
        self.dowork(build_nvr, build_id, tag, koji_instance,
                    tag_info=tag_info)


    def dowork(self, build_nvr, build_id, tag, koji_instance,
               skip_tagging=False, tag_info=None):
        instance = self.koji_clients[koji_instance]

        if not build_id:
            build_id = instance['client'].findBuildID(build_nvr)

        if not tag_info:
            if tag not in instance['tags']:
                log.info('Tag not autosigned, skipping')
                return

            tag_info = instance['tags'][tag]

        log.info('Going to sign %s with %s (%s) and move to %s',
                 build_nvr, tag_info['key'], tag_info['keyid'],
                 tag_info['to'])

        rpms = utils.get_rpms(instance['client'],
                              build_nvr=build_nvr,
                              build_id=build_id,
                              sigkey=tag_info['keyid'])
        log.info('RPMs to sign and move: %s',
                 ['%s (%s, signed: %s)' %
                    (key, rpms[key]['id'], rpms[key]['signed'])
                    for key in rpms.keys()])
        if len(rpms) < 1:
            log.info('Build contains no rpms, skipping signing and writing')

        if all([rpms[rpm]['signed'] for rpm in rpms]) or len(rpms) < 1:
            log.debug('All RPMs are already signed')
        else:
            to_sign = [key for key in rpms.keys() if not rpms[key]['signed']]
            log.debug('RPMs needing signing: %s' % to_sign)
            cmdline = self.signer.build_sign_cmdline(tag_info['key'],
                                                     to_sign,
                                                     koji_instance)
            log.debug('Signing command line: %s' % cmdline)

            ret, stdout, stderr = utils.run_command(cmdline)
            if ret != 0:
                log.error('Error signing! Signing output: %s, stdout: '
                          '%s, stderr: %s', ret, stdout, stderr)
                return

        if len(rpms) > 1:
            log.info('Build was succesfully signed, telling koji to write with key'
                     ' %s', tag_info['keyid'])

            for rpm in rpms:
                instance['client'].writeSignedRPM(rpms[rpm]['id'],
                                                  tag_info['keyid'])

            log.info('Signed RPMs written out')

        if skip_tagging:
            log.info('Tagging skipped, done')
        else:
            log.info('Packages correctly signed, moving to %s' %
                     tag_info['to'])
            if tag == tag_info['to']:
                log.info('Non-gated, not moving')
            else:
                instance['client'].tagBuild(tag_info['to'], build_id, False,
                                            tag)

    def sign_modular_tag(self, koji_instance, tag):
        """
        Signs all the latest RPMs in a modular tag
        """
        if koji_instance not in self.koji_clients:
            log.error('Koji instance not known.')
            return

        # Get the list of all builds in the tag.
        instance = self.koji_clients[koji_instance]
        builds = utils.get_builds_in_tag(instance["client"], tag)
        if not builds:
            log.info("No build to sign in given tag.")
            return

        # Sign the builds in tag.
        for build in builds[1:]:
            self.sign_modular_rpms(build["nvr"], build["build_id"], tag,
                                   koji_instance)
