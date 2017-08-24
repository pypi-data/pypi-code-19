import random
import itculate_sdk as itsdk
from unix_dates import UnixDate, UnixTimeDelta


# collector if

def build_topology(service, exchange, cassandra):
    # bucket_read = itsdk.add_vertex(collector_id=collector_id,
    #                                name="Bucket Read",
    #                                vertex_type="AWS_S3_Bucket",
    #                                keys=service + "Bucket Read")
    bucket_write = itsdk.add_vertex(collector_id=collector_id,
                                    name="Bucket Write",
                                    vertex_type="AWS_S3_Bucket",
                                    keys=service + "Bucket Write")
    queue = itsdk.add_vertex(collector_id=collector_id,
                             name="Queue",
                             vertex_type="RabbitMQ_Queue",
                             keys=service + "RabbitMQ_Queue")
    attribution_svc = itsdk.add_vertex(collector_id=collector_id,
                                       name=service,
                                       vertex_type="Service",
                                       keys=service + "Attribution-service")
    rds = itsdk.add_vertex(collector_id=collector_id,
                           name="RDS",
                           vertex_type="AWS_RDS",
                           keys=service + "RDS")
    rds_replica = itsdk.add_vertex(collector_id=collector_id,
                                   name="RDS Mirror",
                                   vertex_type="AWS_RDS",
                                   keys=service + "RDS-Mirror")

    itsdk.connect(collector_id=collector_id,
                  source=exchange,
                  target=queue,
                  topology="razor")
    itsdk.connect(collector_id=collector_id,
                  source=queue,
                  target=attribution_svc,
                  topology="razor")
    # itsdk.connect(collector_id=collector_id,
    #               source=bucket_read,
    #               target=attribution_svc,
    #               topology="razor")
    itsdk.connect(collector_id=collector_id,
                  source=attribution_svc,
                  target=bucket_write,
                  topology="razor")
    itsdk.connect(collector_id=collector_id,
                  source=attribution_svc,
                  target=rds,
                  topology="razor")
    itsdk.connect(collector_id=collector_id,
                  source=rds,
                  target=rds_replica,
                  topology="replica")
    itsdk.connect(collector_id=collector_id,
                  source=attribution_svc,
                  target=cassandra,
                  topology="razor")


if __name__ == '__main__':
    itsdk.init(server_url="http://localhost:5000/api/v1")

    collector_id = "collector_id"

    exchange_vertex = itsdk.add_vertex(collector_id=collector_id,
                                name="Exchange",
                                vertex_type="RabbitMQ_Exchange",
                                keys="RabbitMQ_Exchange")

    cassandra_vertex = itsdk.add_vertex(collector_id=collector_id,
                                 name="Cassandra",
                                 vertex_type="Cassandra",
                                 keys="Cassandra")

    build_topology("Attribution", exchange_vertex, cassandra_vertex)
    build_topology("Annotation", exchange_vertex, cassandra_vertex)

    itsdk.flush_all()
