# Copyright (c) 2015-2016 Avere Systems, Inc.  All Rights Reserved.             
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

SERVICE_DATA = {
    'auth':{ 'username':'user','password':'pass'},
    'machinetypes':['small','medium','large'],
    'instances':{
        'inst-12341':{'type':'large','addresses':['10.10.200.10','10.10.200.11','10.10.200.12'], 'tags':{'Owner':'woodwardj', 'Department':'QA'}, 'disks':[{'type':'standard','boot':'yes','size':50, 'name':'root'},{'type':'ssd','size':400, 'name':'aggr'}]},
        'inst-12342':{'type':'large','addresses':['10.10.200.13','10.10.200.14','10.10.200.15'], 'tags':{'Owner':'woodwardj', 'Department':'QA'}, 'disks':[{'type':'standard','boot':'yes','size':50, 'name':'root'},{'type':'ssd','size':400, 'name':'aggr'}]},
        'inst-12344':{'type':'large','addresses':['10.10.200.16','10.10.200.17','10.10.200.18'], 'tags':{'Owner':'woodwardj', 'Department':'QA'}, 'disks':[{'type':'standard','boot':'yes','size':50, 'name':'root'},{'type':'ssd','size':400, 'name':'aggr'}]},
        'inst-12344':{'type':'large','addresses':['10.10.200.19','10.10.200.20','10.10.200.21'], 'tags':{'Owner':'woodwardj', 'Department':'QA'}, 'disks':[{'type':'standard','boot':'yes','size':50, 'name':'root'},{'type':'ssd','size':400, 'name':'aggr'}]},
        'inst-12345':{'type':'large','addresses':['10.10.200.22','10.10.200.23','10.10.200.24'], 'tags':{'Owner':'woodwardj', 'Department':'QA'}, 'disks':[{'type':'standard','boot':'yes','size':50, 'name':'root'},{'type':'ssd','size':400, 'name':'aggr'}]},
        'inst-12346':{'type':'large','addresses':['10.10.200.25','10.10.200.26','10.10.200.27'], 'tags':{'Owner':'woodwardj', 'Department':'QA'}, 'disks':[{'type':'standard','boot':'yes','size':50, 'name':'root'},{'type':'ssd','size':400, 'name':'aggr'}]},
        'inst-12347':{'type':'large','addresses':['10.10.200.28','10.10.200.29','10.10.200.30'], 'tags':{'Owner':'woodwardj', 'Department':'QA'}, 'disks':[{'type':'standard','boot':'yes','size':50, 'name':'root'},{'type':'ssd','size':400, 'name':'aggr'}]},
        'inst-12348':{'type':'large','addresses':['10.10.200.31','10.10.200.32','10.10.200.33'], 'tags':{'Owner':'woodwardj', 'Department':'QA'}, 'disks':[{'type':'standard','boot':'yes','size':50, 'name':'root'},{'type':'ssd','size':400, 'name':'aggr'}]},
        'inst-12349':{'type':'large','addresses':['10.10.200.34','10.10.200.35','10.10.200.36'], 'tags':{'Owner':'woodwardj', 'Department':'QA'}, 'disks':[{'type':'standard','boot':'yes','size':50, 'name':'root'},{'type':'ssd','size':400, 'name':'aggr'}]},
    }
}

class Service(ServiceBase):
    '''Mock service class'''

    def __init__(self, username, passwod):
        self.username = username
        self.password = password
        self.data     = SERVICE_DATA 
        self.connection_test()

    def connection_test(self):
        if self.username != self.data['auth']['username'] or \
           self.password != self.data['auth']['password']:
            raise vFXTConfigurationException("Failed to establish connection to service")

    def find_instances(self, filterdict): raise Exception("Not implemented")
    def get_instances(self, instance_ids): raise Exception("Not implemented")
    def get_instance(self, instance_id): raise Exception("Not implemented")
    def wait_for_status(self, instance, status, retries=120): raise Exception("Not implemented")
    def wait_for_service_checks(self, instance, retries=600): raise Exception("Not implemented")
    def stop(self, instance): raise Exception("Not implemented")
    def start(self, instance): raise Exception("Not implemented")
    def restart(self, instance): raise Exception("Not implemented")
    def destroy(self, instance): raise Exception("Not implemented")
    def is_on(self, instance): raise Exception("Not implemented")
    def is_off(self, instance): raise Exception("Not implemented")
    def name(self, instance): raise Exception("Not implemented")
    def instance_id(self, instance): raise Exception("Not implemented")
    def ip(self, instance): raise Exception("Not implemented")
    def fqdn(self, instance): raise Exception("Not implemented")
    def status(self, instance): raise Exception("Not implemented")
    def refresh(self, instance): raise Exception("Not implemented")

    def create_instance(self, machine_type, name, **options): raise Exception("Not implemented")
    def create_node(self, node_name, cfg, node_opts, instance_options): raise Exception("Not implemented")
    def create_cluster(self, cluster, **options): raise Exception("Not implemented")
    def add_cluster_nodes(self, cluster, count, **options): raise Exception("Not implemented")
    def load_cluster_information(self, cluster, **options): raise Exception("Not implemented")

    def shelve(self, serviceinstance): raise Exception("Not implemented")
    def unshelve(self, serviceinstance): raise Exception("Not implemented")

    # storage/buckets
    def create_bucket(self, name): raise Exception("Not implemented")
    def delete_bucket(self, name): raise Exception("Not implemented")
    def authorize_bucket(self, cluster, name): raise Exception("Not implemented")
    # networking
    def get_default_router(self): raise Exception("Not implemented")
    def get_dns_servers(self): raise Exception("Not implemented")
    def get_ntp_servers(self): raise Exception("Not implemented")
    def get_available_addresses(self, count=1): raise Exception("Not implemented")

    def export(self): raise Exception("Not implemented")


