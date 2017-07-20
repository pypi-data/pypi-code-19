import itculate_sdk as itsdk


def build_itculate():
    itsdk.init(server_url="http://localhost:5000/api/v1")

    id = "collector_id"

    # shared infrastructure
    workers = [itsdk.add_vertex(collector_id=id,
                                vertex_type="AnalyticsWorker",
                                name="analytics-prod-worker-{}".format(i),
                                keys="analytics-prod-worker-{}".format(i),
                                file="/backend/server/worker.py",
                                description="Worker to any type od Message",
                                wiki="docs.itculate.io/wiki/digest_api/troubleshooting",
                                version="1.21",
                                line=351,
                                Developer={
                                    "email": "tom.silvia@itculate.io",
                                    "Mobile": "857-881-6711",
                                    "Group": "Boston"
                                }) for i in range(4)]

    cassandras = [itsdk.add_vertex(collector_id=id,
                                   vertex_type="Cassandra",
                                   name="Cassandra-{}".format(i),
                                   keys="Cassandra-{}".format(i),
                                   ) for i in range(3)]

    ##########################################
    # Digest workflow
    ##########################################

    topology_digest = "digest"

    s3_bucket = itsdk.add_vertex(collector_id=id,
                                 vertex_type="AWS_S3_Bucket",
                                 name="itculate.io-uploaded",
                                 keys="itculate.io-uploaded",
                                 capacity=itsdk.CapacityDataType.value(20.0))

    lambda_uploaded = itsdk.add_vertex(collector_id=id,
                                       vertex_type="AWS_Lambda",
                                       name="ops_log_collection_package_uploaded",
                                       keys="ops_log_collection_package_uploaded",
                                       code_size=3056591,
                                       runtime="python2.7",
                                       timeout=30)

    api_collectors_post = itsdk.add_vertex(collector_id=id,
                                           vertex_type="API",
                                           name="api.collectors.post",
                                           keys="api.collectors.post",
                                           file="/portal/api/collectors.py",
                                           description="Process collector post request from S3",
                                           wiki="docs.itculate.io/wiki/Aggregator/troubleshooting",
                                           version="1.21",
                                           line=99,
                                           Developer={
                                               "email": "krishnan.mahadi@itculate.io",
                                               "Mobile": "857-881-6711",
                                               "Group": "Bangalore"
                                           })

    api_upload_post = itsdk.add_vertex(collector_id=id,
                                       vertex_type="API",
                                       name="api.upload.post",
                                       keys="api.upload.post",
                                       file="/portal/api/collectors.py",
                                       description="Process collector post request from S3",
                                       wiki="docs.itculate.io/wiki/Aggregator/troubleshooting",
                                       version="1.21",
                                       line=99,
                                       Developer={
                                           "email": "krishnan.mahadi@itculate.io",
                                           "Mobile": "857-881-6711",
                                           "Group": "Bangalore"
                                       })

    worker_dispatcher = itsdk.add_vertex(collector_id=id,
                                         vertex_type="Dispatcher",
                                         name="Digest on upload",
                                         keys="worker.on_upload",
                                         file="/backend/server/worker.py",
                                         description="Package was uploaded / payload arrived. Trigger digest!",
                                         wiki="docs.itculate.io/wiki/upload/troubleshooting",
                                         version="1.21",
                                         line=182,
                                         Developer={
                                             "email": "krishnan.mahadi@itculate.io",
                                             "Mobile": "857-881-6711",
                                             "Group": "Bangalore"
                                         })

    worker_digest_s3 = itsdk.add_vertex(collector_id=id,
                                        vertex_type="Importer",
                                        name="S3 package Importer",
                                        keys="worker.importer.s3",
                                        file="/backend/server/digest/package_import.py",
                                        description="Process Package from S3",
                                        wiki="docs.itculate.io/wiki/importer_s3/troubleshooting",
                                        version="1.21",
                                        line=166,
                                        Developer={
                                            "email": "tom.silvia@itculate.io",
                                            "Mobile": "857-881-6711",
                                            "Group": "Boston"
                                        })

    worker_digest_api = itsdk.add_vertex(collector_id=id,
                                         vertex_type="Importer",
                                         name="API Importer",
                                         keys="worker.importer.api",
                                         file="/backend/server/digest/package_import.py",
                                         description="Process package from API",
                                         wiki="docs.itculate.io/wiki/importer_api/troubleshooting",
                                         version="1.21",
                                         line=351,
                                         Developer={
                                             "email": "tom.silvia@itculate.io",
                                             "Mobile": "857-881-6711",
                                             "Group": "Boston"
                                         })

    itsdk.connect(collector_id=id, source=s3_bucket, target=lambda_uploaded, topology=topology_digest)
    itsdk.connect(collector_id=id, source=lambda_uploaded, target=api_collectors_post, topology=topology_digest)
    itsdk.connect(collector_id=id, source=api_collectors_post, target=worker_dispatcher, topology=topology_digest)
    itsdk.connect(collector_id=id, source=api_upload_post, target=worker_dispatcher, topology=topology_digest)
    itsdk.connect(collector_id=id, source=worker_dispatcher, target=worker_digest_s3, topology=topology_digest)
    itsdk.connect(collector_id=id, source=worker_dispatcher, target=worker_digest_api, topology=topology_digest)
    itsdk.connect(collector_id=id, source=worker_digest_s3, target=workers, topology=topology_digest)
    itsdk.connect(collector_id=id, source=worker_digest_api, target=workers, topology=topology_digest)
    itsdk.connect(collector_id=id, source=workers, target=cassandras, topology="cassandra")

    ##########################################
    # Add Grouping
    ##########################################

    workers_group = itsdk.add_vertex(collector_id=id, keys="Workers-Pool", name="Workers", vertex_type="Pool")
    itsdk.connect(collector_id=id, source=workers_group, target=workers, topology="members")
    itsdk.enable_grouper_algorithm(group_vertex_type=workers_group.type,
                                   member_vertex_type=workers[0].type,
                                   topology="members")

    cassandra_cluster = itsdk.add_vertex(collector_id=id, keys="Cassandras-Cluster", name="Cassandras",
                                         vertex_type="Cluster")
    itsdk.connect(collector_id=id, source=cassandra_cluster, target=cassandras, topology="uses")
    itsdk.enable_grouper_algorithm(group_vertex_type=cassandra_cluster.type,
                                   member_vertex_type=cassandras[0].type,
                                   topology="uses")


    ##########################################
    # Aggregator workflow
    ##########################################

    topology_aggregator = "Aggregator"

    tasks_aggregate_exchange = itsdk.add_vertex(collector_id=id,
                                                vertex_type="RabbitMQ_Exchange",
                                                name="Tasks-Aggregate",
                                                keys="tasks.aggregate.exchange")
    timeseries_aggregator_queue = itsdk.add_vertex(collector_id=id,
                                                   vertex_type="RabbitMQ_Queue",
                                                   name="FifteenMinuteTenantEvent TenantTimeseriesAggregator",
                                                   keys="FifteenMinuteTenantEvent-TenantTimeseriesAggregator")
    tenant_aggregator_queue = itsdk.add_vertex(collector_id=id,
                                               vertex_type="RabbitMQ_Queue",
                                               name="DailyTenantEvent VertexTimeseriesAggregator",
                                               keys="DailyTenantEvent-VertexTimeseriesAggregator")

    timeseries_aggregator = itsdk.add_vertex(collector_id=id,
                                             vertex_type="Aggregator",
                                             name="TimeSeries Aggregator",
                                             keys="TimeSeriesAggregator",
                                             data={
                                                 "Developer email": "tom.silvia@itculate.io",
                                                 "Developer Mobile": "857-881-6711",
                                                 "Wiki": "docs.itculate.io/wiki/Aggregator/troubleshooting",
                                                 "Description": "Anomaly detection result saved on ElasticSearch",
                                                 "Version": "1.21",
                                                 "File": __file__.replace("/Users/ran/Develop/", ""),
                                                 "Package": __package__,
                                                 "Group": "Data Analysis Group"
                                             })

    tenant_aggregator = itsdk.add_vertex(collector_id=id,
                                         vertex_type="Aggregator",
                                         name="Tenant Aggregator",
                                         keys="TenantAggregator",
                                         data={
                                             "Developer email": "tom.silvia@itculate.io",
                                             "Developer Mobile": "857-881-6711",
                                             "Wiki": "docs.itculate.io/wiki/Aggregator/troubleshooting",
                                             "Description": "Anomaly detection result saved on ElasticSearch",
                                             "Version": "1.21",
                                             "File": __file__.replace("/Users/ran/Develop/", ""),
                                             "Package": __package__,
                                             "Group": "Data Analysis Group"
                                         })

    aggregators = [timeseries_aggregator, tenant_aggregator]

    itsdk.connect(collector_id=id,
                  source=tasks_aggregate_exchange,
                  target=[timeseries_aggregator_queue, tenant_aggregator_queue],
                  topology=topology_aggregator)
    itsdk.connect(collector_id=id,
                  source=tenant_aggregator_queue,
                  target=tenant_aggregator,
                  topology=topology_aggregator)
    itsdk.connect(collector_id=id,
                  source=timeseries_aggregator_queue,
                  target=timeseries_aggregator,
                  topology=topology_aggregator)
    itsdk.connect(collector_id=id,
                  source=aggregators,
                  target=workers,
                  topology=topology_aggregator)

    itsdk.flush_all()


def add_group(collector_id,
              members,
              vertex_type,
              topology,
              name,
              keys,
              data=None,
              **kwargs):
    """
    Adds a vertex group to the uploader

    :param str collector_id: Unique name identifying the reporter of this topology
    :type members: str|dict|Vertex|collections.Iterable[dict]|collections.Iterable[Vertex]|collections.Iterable[str]
    :param str vertex_type: Group Vertex type
    :param str topology: Edge type to connect the Group to the Members
    :param dict[str,str]|str keys: A set of unique keys identifying this vertex group. If str, 'pk' will be used as key
    :param str name: Name for vertex
    :param dict data: Set of initial values to assign to vertex group (optional)
    :param kwargs: Any additional key:value pairs that should be assigned to vertex group.
    :rtype: Vertex
    """

    group_vertex = itsdk.add_vertex(vertex_type=vertex_type,
                                    name=name,
                                    keys=keys,
                                    data=data,
                                    **kwargs)

    itsdk.connect(collector_id=collector_id, source=group_vertex, target=members, topology=topology)

    return group_vertex


if __name__ == '__main__':
    build_itculate()
