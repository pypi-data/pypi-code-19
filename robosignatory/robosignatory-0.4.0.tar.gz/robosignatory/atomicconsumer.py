import fedmsg.consumers
import robosignatory.utils as utils
import robosignatory.work

import logging
log = logging.getLogger("robosignatory.atomicconsumer")


class AtomicSignerConsumer(fedmsg.consumers.FedmsgConsumer):
    config_key = 'robosignatory.enabled.atomicsigner'

    def __init__(self, *args, **kwargs):
        super(AtomicSignerConsumer, self).__init__(*args, **kwargs)

        prefix = self.hub.config.get('topic_prefix')
        env = self.hub.config.get('environment')
        self.topic = [
            '%s.%s.pungi.compose.ostree' % (prefix, env),
            '%s.%s.bodhi.ostree.compose.finish' % (prefix, env),
        ]

        signing_config = self.hub.config['robosignatory.signing']
        self.signer = utils.get_signing_helper(**signing_config)

        self.refs = {}
        for ref in self.hub.config['robosignatory.ostree_refs']:
            val = self.hub.config['robosignatory.ostree_refs'][ref]
            if 'ref_to' in val:
                raise ValueError('ref_to in %s found. This is depricated' %
                                 ref)
            self.refs[ref] = val

        log.info('AtomicSignerConsumer ready for service')

    def consume(self, msg):
        topic = msg['topic']
        if topic not in self.topic:
            return

        msg = msg['body']['msg']

        # Common parts of the messages:
        #  {u'ref': u'fedora-atomic/25/x86_64/docker-host',
        #   u'commitid': u'f99114401f....'}
        # Pungi added:
        #  {u'arch': u'x86_64',
        #   u'variant': u'Atomic',
        #   u'location': u'http://kojipkgs....',
        #   u'compose_id': u'Fedora-25-20161002.n.0'}
        # Bodhi added:
        #  {u'tag': 'fc25'}

        ref = msg['ref']
        commitid = msg['commitid']

        if topic.endswith('.pungi.compose.ostree'):
            disp = ('%(ref)s (%(commitid)s, variant %(variant)s, arch %(arch)s'
                    ')' % msg)
            source = 'pungi'
        elif topic.endswith('.bodhi.ostree.compose.finish'):
            disp = ('%(ref)s (%(commitid)s, tag %(tag)s)' % msg)
            source = 'bodhi'
        else:
            log.info('Unknown topic: %s. Skipping' % topic)
            return

        log.info('%s composed %s' % (source, disp))

        if ref not in self.refs:
            log.info('Unknown reference %s. Skipping' % ref)
            return

        val = self.refs[ref]

        robosignatory.work.process_atomic(self.signer, ref, commitid,
                                          **val)
