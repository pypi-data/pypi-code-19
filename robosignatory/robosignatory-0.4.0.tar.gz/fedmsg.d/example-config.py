import socket
hostname = socket.gethostname()

config = {
    'robosignatory.enabled.tagsigner': True,
    'robosignatory.enabled.atomicsigner': True,
    'robosignatory.pdc_url': 'https://pdc.fedoraproject.org/rest_api/v1',
    'robosignatory.module_prefixes': ['module-'],

    'robosignatory.signing': {
        # This should be the name of an entrypoint plugin that provides
        # SigningHelper functionality.
        'backend': 'sigul',
        # These are arguments to the __init__ method of that helper.
        'user': 'robosignatory',
        'passphrase_file': 'robosignatory.pass',
        'config_file': '/etc/sigul/client.conf',
    },

    # The keys here need to be the same in the sigul bridge
    'robosignatory.koji_instances': {
        'primary': {
            'url': 'http://koji.fedoraproject.org/kojihub',
            'module_key': 'fedora26',
            'module_keyid': 'xxxxxxx',
            'options': {
                # Only ssl and kerberos are supported at the moment
                'authmethod': 'ssl',
                'cert': 'robosignatory.cert',
                'serverca': 'servcer-ca.cert',
            },
            'tags': [
                {
                    'from': 'rawhide-signcandidate',
                    'to': 'rawhide',
                    'key': 'fedora26',
                    'keyid': 'xxxxxxxx'
                },
            ],
        },
    },

    'robosignatory.ostree_refs': {
        'fedora-atomic/25/x86_64/docker-host': {
            'directory': '/mnt/koji/compose/atomic/25/',
            'key': 'fedora-25'
        }
    }
}
