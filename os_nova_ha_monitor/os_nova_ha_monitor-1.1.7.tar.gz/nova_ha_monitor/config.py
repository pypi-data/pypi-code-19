
import logging
import json

import consul


class ConsulConfig(object):
    CONSUL_CONFIG_BASE_PATH = ''
    CONSUL_CONFIG_DEFAULT = {}

    # TODO: Check if it makes sense to merge _get_consul_path with _get_consul_key in future
    #       Unit test this class
    def _get_consul_path(self, key):
        """ Returns required k/v path string for a given key """

        return "{0}/{1}/{2}".format(self.CONSUL_CONFIG_BASE_PATH, self.node, key)

    def _get_consul_key(self, key):
        """ Fetch key value from consul and load it as a json """
        _, value = self.consul.kv.get(self._get_consul_path(key))

        return value.get('Value')

    def _put_consul_key(self, key, value):
        """ Puts key/value into consul """

        return self.consul.kv.put(self._get_consul_path(key), str(value))

    def _initialize_consul_schema(self):
        """ Initialize consul k/v schema according to preset variables. """

        for key, value in self.CONSUL_CONFIG_DEFAULT.iteritems():
            if not self.consul.kv.get(self._get_consul_path(key))[1]:
                self._put_consul_key(key, value)

    def __init__(self, node):
        self.consul = consul.Consul()
        self.node = node

    #
    # Get Node Health

    def get_health(self):
        """ Returns node health status """
        return self.consul.health.node(self.node)[1]

class ConsulHAConfig(ConsulConfig):
    """
        This class is used to access following nodes on consul KV:
            ha_cluster/ha_nodes/{{ ha-node }}/config/os_cloud
            ha_cluster/ha_nodes/{{ ha-node }}/config/nova_mountpoint
            ha_cluster/ha_nodes/{{ ha-node }}/status/in_use
            ha_cluster/ha_nodes/{{ ha-node }}/general
    """

    CONSUL_CONFIG_BASE_PATH = 'ha_cluster/ha_nodes'
    CONSUL_COMPUTE_BASE_PATH = 'ha_cluster/compute_nodes'


    CONSUL_CONFIG_DEFAULT = {
        'general': '',
        'status/in_use': False,
        'config/os_cloud': 'cloud_v3_api',
        'config/nova_mountpoint': '/var/lib/nova/instances'
    }

    def __init__(self, ha_node):
        super(ConsulHAConfig, self).__init__(ha_node)

        # TODO We are running schema check for every class instance,
        #       this might be a problem
        self._initialize_consul_schema()

    #
    # Return list of compute nodes defined in consul cluster
    # TODO: unittests
    def get_compute_nodes(self):
        compute_nodes_keys = self.consul.kv.get(self.CONSUL_COMPUTE_BASE_PATH, recurse=True,
                                                keys=False)[1]

        return list(set([key.get('Key').split('/')[2] for key in compute_nodes_keys]))

    #
    # status keys access methods

    def get_status_in_use(self):
        """ Returns status/in_use value """
        key = 'status/in_use'

        return self._get_consul_key(key)

    def set_status_in_use(self, value=False):
        """ Creates status/in_use k/v entry in consul """
        key = 'status/in_use'

        if self.get_status_in_use():
            logging.error('Resetting %s to False when already,\
                            True needs to be done manually.', key)
            # FIXME Raise an error here as we can't do anything here
            return
        return self._put_consul_key(key, value)

    #
    # cloud config access methods

    def get_os_cloud(self):
        """ Returns config/os_cloud value """
        key = 'config/os_cloud'

        return self._get_consul_key(key)

    def set_os_cloud(self, value=False):
        """ Creates config/os_cloud k/v entry in consul """
        key = 'config/os_cloud'

        return self._put_consul_key(key, value)

    def get_nova_mountpoint(self):
        """ Returns config/nova_mountpoint value """
        key = 'config/nova_mountpoint'

        return self._get_consul_key(key)

    def set_nova_mountpoint(self, value=False):
        """ Creates config/nova_mountpoint k/v entry in consul """
        key = 'config/nova_mountpoint'

        return self._put_consul_key(key, value)


class ConsulComputeConfig(ConsulConfig):
    """
        This class is used to access following nodes on consul KV:

            ha_cluster/compute_nodes/{{ compute-node }}/status/failed | default(False)
            ha_cluster/compute_nodes/{{ compute-node }}/status/recovered | default(False)
            ha_cluster/compute_nodes/{{ compute-node }}/internal/number_fails  | default(0)
            ha_cluster/compute_nodes/{{ compute-node }}/internal/runtime_config  | default({})
            ha_cluster/compute_nodes/{{ compute-node }}/config/bmc/user
            ha_cluster/compute_nodes/{{ compute-node }}/config/bmc/password
            ha_cluster/compute_nodes/{{ compute-node }}/config/bmc/ip
            ha_cluster/compute_nodes/{{ compute-node }}/config/ssh/user
            ha_cluster/compute_nodes/{{ compute-node }}/config/ssh/password
            ha_cluster/compute_nodes/{{ compute-node }}/general
    """

    CONSUL_CONFIG_BASE_PATH = 'ha_cluster/compute_nodes'

    CONSUL_CONFIG_DEFAULT = {
        'general': '',
        'status/failed': False,
        'status/recovered': False,
        'internal/number_fails': 0,
        'internal/runtime_config': {},
        'config/bmc/ip': '',
        'config/bmc/user': 'test',
        'config/bmc/password': 'Test123.',
        'config/ssh/user': 'test',
        'config/ssh/password': 'Test123.'
    }

    def __init__(self, compute_node):
        super(ConsulComputeConfig, self).__init__(compute_node)

        # TODO We are running schema check for every class instance,
        #       this might be a problem
        self._initialize_consul_schema()

    #
    # status keys access methods

    def get_status_failed(self):
        """ Returns status/failed value """
        key = 'status/failed'

        return bool(self._get_consul_key(key))

    def set_status_failed(self, value=False):
        """ Creates status/failed k/v entry in consul """
        key = 'status/failed'

        if self.get_status_failed():
            logging.error('Resetting %s to False when already,\
                            True needs to be done manually.', key)
            # FIXME Raise an error here as we can't do anything here
            return
        return self._put_consul_key(key, value)


    def get_status_recovered(self):
        """ Returns status/recovered value """
        key = 'status/recovered'

        return bool(self._get_consul_key(key))

    def set_status_recovered(self, value=False):
        """ Creates status/recovered k/v entry in consul  """
        key = 'status/recovered'

        if self.get_status_failed():
            logging.error('Resetting %s to False when already,\
                            True needs to be done manually.', key)
            # FIXME Raise an error here as we can't do anything here
            return
        return self._put_consul_key(key, value)


    #
    # internal key access methods

    def get_runtime_config(self):
        """ Returns runtime_config for given node """
        key = 'internal/runtime_config'

        return json.loads(self._get_consul_key(key))

    def set_runtime_config(self, value):
        """ Creates runtime_config for given node """
        key = 'internal/runtime_config'

        return self._put_consul_key(key, json.dumps(value, sort_keys=True, indent=4))


    def get_number_fails(self):
        """ Returns number of fails """
        key = 'internal/number_fails'

        return int(self._get_consul_key(key))

    def set_number_fails(self, value):
        """ Sets internal/number_fails to requested value"""
        key = 'internal/number_fails'

        return self._put_consul_key(key, value)


    #
    # config key access methods

    def get_bmc_user(self):
        """ Returns bmc_user for node """
        key = 'config/bmc/user'

        return self._get_consul_key(key)

    def set_bmc_user(self):
        """ Creates bmc_user for node """
        pass

    def get_bmc_password(self):
        """ Returns bmc password for node """
        key = 'config/bmc/password'

        return self._get_consul_key(key)

    def set_bmc_password(self):
        """ Creates  """
        pass

    def get_bmc_ip(self):
        """ Returns bmc ip for node """
        key = 'config/bmc/ip'

        return self._get_consul_key(key)

    def set_bmc_ip(self):
        """ Creates  """
        pass


    def get_ssh_user(self):
        """ Returns ssh_user login for node """
        key = 'config/ssh/user'

        return self._get_consul_key(key)

    def set_ssh_user(self):
        """ Creates ssh_user for node """
        pass

    def get_ssh_password(self):
        """ Returns ssh user password for host """
        key = 'config/ssh/password'

        return self._get_consul_key(key)

    def set_ssh_password(self):
        """ Creates  """
        pass

    #
    # General access methods
