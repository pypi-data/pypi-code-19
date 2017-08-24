import random
import itculate_sdk as itsdk
from unix_dates import UnixDate, UnixTimeDelta


# collector if

def build_topology():
    client = itsdk.add_vertex(collector_id=collector_id,
                              name="Client",
                              vertex_type="Client",
                              keys="client")

    client_payload_s3 = itsdk.add_vertex(collector_id=collector_id,
                                         name="Client Payload",
                                         vertex_type="AWS_S3_Bucket",
                                         keys="client-payload")

    queue = itsdk.add_vertex(collector_id=collector_id,
                             name="New Payload Queue",
                             vertex_type="RabbitMQ_Queue",
                             keys="new-payload-queue")

    normalizer = itsdk.add_vertex(collector_id=collector_id,
                                  name="Normalizer",
                                  vertex_type="Service",
                                  keys="data-normalizer")

    changes_tracker = itsdk.add_vertex(collector_id=collector_id,
                                       name="Changes",
                                       vertex_type="Tracker",
                                       keys="changes-tracker")

    changes_queue = itsdk.add_vertex(collector_id=collector_id,
                                     name="New Changes Queue",
                                     vertex_type="RabbitMQ_Queue",
                                     keys="new-changes-queue")

    abnormal_tracker = itsdk.add_vertex(collector_id=collector_id,
                                        name="Abnormal",
                                        vertex_type="Tracker",
                                        keys="Abnormal-tracker")

    abnormal_queue = itsdk.add_vertex(collector_id=collector_id,
                                      name="New Abnormal Queue",
                                      vertex_type="RabbitMQ_Queue",
                                      keys="new-abnormal-queue")

    violations_tracker = itsdk.add_vertex(collector_id=collector_id,
                                          name="Violations",
                                          vertex_type="Tracker",
                                          keys="violations-tracker")

    violations_queue = itsdk.add_vertex(collector_id=collector_id,
                                        name="New Violations Queue",
                                        vertex_type="RabbitMQ_Queue",
                                        keys="new-violations-queue")

    rds = itsdk.add_vertex(collector_id=collector_id,
                           name="normalizer-rds",
                           vertex_type="AWS_RDS",
                           keys="normalizer-rds")

    rds_replica = itsdk.add_vertex(collector_id=collector_id,
                                   name="normalizer-rds-mirror",
                                   vertex_type="AWS_RDS",
                                   keys="normalizer-rds-mirror")

    itsdk.connect(collector_id=collector_id,
                  source=rds,
                  target=rds_replica,
                  topology="replica")

    topology = "upload-high-level"
    itsdk.connect(collector_id=collector_id,
                  source=client,
                  target=client_payload_s3,
                  topology=topology)
    itsdk.connect(collector_id=collector_id,
                  source=client_payload_s3,
                  target=queue,
                  topology=topology)
    itsdk.connect(collector_id=collector_id,
                  source=queue,
                  target=normalizer,
                  topology=topology)
    itsdk.connect(collector_id=collector_id,
                  source=normalizer,
                  target=rds,
                  topology=topology)

    itsdk.connect(collector_id=collector_id,
                  source=normalizer,
                  target=changes_tracker,
                  topology=topology)
    itsdk.connect(collector_id=collector_id,
                  source=normalizer,
                  target=abnormal_tracker,
                  topology=topology)
    itsdk.connect(collector_id=collector_id,
                  source=normalizer,
                  target=violations_tracker,
                  topology=topology)

    itsdk.connect(collector_id=collector_id,
                  source=abnormal_tracker,
                  target=abnormal_queue,
                  topology=topology)
    itsdk.connect(collector_id=collector_id,
                  source=changes_tracker,
                  target=changes_queue,
                  topology=topology)
    itsdk.connect(collector_id=collector_id,
                  source=violations_tracker,
                  target=violations_queue,
                  topology=topology)


if __name__ == '__main__':
    itsdk.init(server_url="http://localhost:5000/api/v1")

    collector_id = "collector_id"

    build_topology()
    itsdk.flush_all()
