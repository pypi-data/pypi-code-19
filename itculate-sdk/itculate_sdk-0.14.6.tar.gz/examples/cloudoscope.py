#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#


# -----------------------------------------------------------------------------
# SDK Example: group_example
#
# This example shows how to build a number of "clusters" with multiple hosts
# grouped within each one of them.
#
# The grouping is a powerful mechanism that allows decluttering and high level
# overview of the environment.
#
# -----------------------------------------------------------------------------


import itculate_sdk as itsdk


# please contact admin@itculate.io for api_key and api_secret
api_key = None  # When None, the SDK will try to look for a 'credentials' file in '~/.itculate/'
api_secret = None

# please contact admin@itculate.io for api_key and api_secret

if __name__ == '__main__':
    # Initialize SDK to send data directly to the cloud
    itsdk.init(role="cloudoscope")
    # itsdk.init(server_url="http://localhost:5000/api/v1")

    collector_id = "group_example1"
    topology = "example"
    grouping_edge = "grouping"
    using_edge = "using"

    number_of_clusters = 2
    number_of_hosts_per_cluster = 4

    for cluster_number in range(1, number_of_clusters + 1):
        # Create the cluster
        grp_cluster = itsdk.add_vertex(collector_id=collector_id,
                                       name="Cluster %d" % cluster_number,
                                       vertex_type="Cluster",
                                       keys="cluster-%d" % cluster_number,
                                       # add any number of custom attributes
                                       developer="John Proctor",
                                       email="john.proctor@itculate.io",
                                       )
        # Create an ELB
        elb = itsdk.add_vertex(collector_id=collector_id,
                               name="LB %d" % cluster_number,
                               vertex_type="LoadBalancer",
                               keys="LB-%d" % cluster_number,
                               # add any number of custom attributes
                               developer="John Proctor",
                               email="john.proctor@itculate.io",
                               )

        # Activate the grouping with regards to the Cluster and its members
        itsdk.enable_grouper_algorithm(group_vertex_type='Cluster', member_vertex_type='Host', topology=grouping_edge)
        # itsdk.enable_grouper_algorithm(group_vertex_type='Cluster', member_vertex_type='Host', topology=using_edge)

        for worker_number in range(1, number_of_hosts_per_cluster + 1):
            # Create a host (a worker node within a cluster)
            a_worker = itsdk.add_vertex(collector_id=collector_id,
                                        name="Worker %s_%s" % (cluster_number, worker_number),
                                        vertex_type="Host",
                                        keys="worker-%d-%d" % (cluster_number, worker_number),
                                        # add any number of custom attributes
                                        developer="John Proctor",
                                        email="john.proctor@itculate.io",
                                        )

            # Connect to the group
            itsdk.connect(collector_id=collector_id,
                          source=grp_cluster,
                          target=a_worker,
                          topology=grouping_edge)

            # Use the ELB
            itsdk.connect(collector_id=collector_id,
                          source=a_worker,
                          target=elb,
                          topology=using_edge)

    itsdk.flush_all()
