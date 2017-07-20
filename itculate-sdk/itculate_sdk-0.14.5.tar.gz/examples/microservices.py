#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

from examples.util import mockup_samples

import itculate_sdk as itsdk

# please contact admin@itculate.io for api_key and api_secret

collector_id = "data_process_pipeline"
topology = "payload-processing"

vertices = {}

rds_with_event = None
asg_with_event = None
service_with_event = None


def create_microservice(name, ec2_count=3, rds_count=0, redis_count=0, redshift_count=0):
    # Simple helper method to create  a Microservice
    # Note that the vertex_type can be anything. The user decided what types are going to be available.

    # create the Microservice vertex
    service = itsdk.add_vertex(collector_id=collector_id,
                               name=name,
                               vertex_type="Service",
                               keys="service-{}".format(name))

    vertices[service.name] = service
    global service_with_event
    service_with_event = service

    # create the ELB vertex
    elb = itsdk.add_vertex(collector_id=collector_id,
                           name="{}-elb".format(name),
                           vertex_type="AWS_ELB",
                           keys="service-load-balancer-{}".format(name))
    vertices[elb.name] = elb

    # create the Auto Scaling Group vertex
    asg = itsdk.add_vertex(collector_id=collector_id,
                           name="{}-asg".format(name),
                           vertex_type="AWS_Auto_Scaling_Group",
                           keys="service-auto-scaling-group-{}".format(name),
                           instance_count=ec2_count)
    vertices[asg.name] = asg
    global asg_with_event
    asg_with_event = asg

    # Connect elb and asg to the  Microservice
    itsdk.connect(collector_id=collector_id, source=service, target=elb, topology="uses-elb")
    itsdk.connect(collector_id=collector_id, source=elb, target=asg, topology="uses-asg")

    # Create EC2 instances and connect them to the asg
    for i in range(ec2_count):
        ec2 = itsdk.add_vertex(collector_id=collector_id,
                               name="i-51660{}".format(i),
                               vertex_type="AWS_Instance",
                               keys="service-{}-ec2-{}".format(name, i))
        itsdk.connect(collector_id=collector_id, source=asg, target=ec2, topology="uses-ec2")
        vertices[ec2.name] = ec2

    # Create RDS and connect them to the Microservice
    for i in range(rds_count):
        rds = itsdk.add_vertex(collector_id=collector_id,
                               name="MySQL db-{}-{}".format(name, i),
                               vertex_type="AWS_RDS",
                               keys="service-{}-db-{}".format(name, i),
                               data={
                                   "instance-type": "db.m3.2xlarge",
                                   "engine": "mariadb",
                               })
        itsdk.connect(collector_id=collector_id, source=asg, target=rds, topology="uses-rds")
        vertices[rds.name] = rds
        global rds_with_event
        rds_with_event = rds

    # Create Redshift and connect them to the Microservice
    for i in range(redshift_count):
        redshift = itsdk.add_vertex(collector_id=collector_id,
                                    name="redshift-{}{}".format(name, i),
                                    vertex_type="AWS_Redshift",
                                    keys="service-{}-redshift-{}".format(name, i))
        itsdk.connect(collector_id=collector_id, source=asg, target=redshift, topology="uses-redshift")
        vertices[redshift.name] = redshift

    # Create Redis and connect them to the Microservice
    for i in range(redis_count):
        redis = itsdk.add_vertex(collector_id=collector_id,
                                 name="Redis-{}-{}".format(name, i),
                                 vertex_type="AWS_Redis",
                                 keys="service-{}-cache-{}".format(name, i))
        itsdk.connect(collector_id=collector_id, source=asg, target=redis, topology="uses-redis")
        vertices[redis.name] = redis

    return service


if __name__ == '__main__':
    # itsdk.init(server_url="http://localhost:5000/api/v1", api_key=api_key, api_secret=api_secret)
    itsdk.init(role="cloudoscope")
    # itsdk.init(server_url="http://localhost:5000/api/v1")

    ########################################################################
    # Step 1 - Create Topology
    ########################################################################

    # Create the s3 Vertex:
    bucket = itsdk.add_vertex(collector_id=collector_id,
                              name="uploaded_bucket",
                              vertex_type="S3",
                              keys="uploaded-bucket")

    # Defining the first service:
    # Create the s3 Vertex:
    a_lambda = itsdk.add_vertex(collector_id=collector_id,
                                name="payload-uploaded",
                                vertex_type="Lambda",
                                keys="lambda-payload-uploaded")

    # create 4 Microservice
    normalizer = create_microservice(name="normalizer", ec2_count=6, redis_count=1, rds_count=1)

    fraud_analyzer = create_microservice(name="fraud-analyzer", ec2_count=3, redis_count=2, redshift_count=1)

    abnormal_detection = create_microservice(name="abnormal-detection", ec2_count=2, redis_count=1, rds_count=1)

    event_distributer = create_microservice(name="event-distributer", ec2_count=2, rds_count=1)

    # connect the  bucket to lambda to Microservice
    itsdk.connect(collector_id=collector_id,
                  source=bucket,
                  target=a_lambda,
                  topology=topology)

    itsdk.connect(collector_id=collector_id,
                  source=a_lambda,
                  target=normalizer,
                  topology="normalizer-service")

    itsdk.connect(collector_id=collector_id,
                  source=normalizer,
                  target=fraud_analyzer,
                  topology="fraud-analyzer-service")

    itsdk.connect(collector_id=collector_id,
                  source=fraud_analyzer,
                  target=abnormal_detection,
                  topology="abnormal_detection-service")

    itsdk.connect(collector_id=collector_id,
                  source=fraud_analyzer,
                  target=event_distributer,
                  topology="event-distributer-service")

    # Flush and commit topology
    itsdk.flush_all()

    # mockup timeseries

    mockup_samples(itsdk=itsdk,
                   vertices=vertices.values(),
                   rds_connection_utilization_vertices=[rds_with_event, asg_with_event, service_with_event],
                   hour_of_event=15)

    # Flush and commit timeseries
    # itsdk.flush_all()


