#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#
import random
from examples.util import mockup_samples

import itculate_sdk as itsdk
from unix_dates import UnixDate, UnixTimeDelta

# please contact admin@itculate.io for api_key and api_secret

collector_id = "vpc_flow_logs"
topology = "payload-processing"


# publish to pypi
# http://peterdowns.com/posts/first-time-with-pypi.html


class Service(object):
    def __init__(self,
                 service,
                 elb,
                 asg,
                 ec2s,
                 rdses,
                 redshifts,
                 redises,
                 elastic_searches):
        self.service = service
        self.elb = elb
        self.asg = asg
        self.ec2s = ec2s
        self.rdses = rdses
        self.redshifts = redshifts
        self.redises = redises
        self.elastic_searches = elastic_searches

    @property
    def vertices(self):
        result = [self.service, self.elb, self.asg]
        if self.ec2s:
            result += self.ec2s
        if self.rdses:
            result += self.rdses
        if self.redshifts:
            result += self.redshifts
        if self.redises:
            result += self.redises
        if self.elastic_searches:
            result += self.elastic_searches
        return result


def create_microservice(name, ec2_count=3, rds_count=0, redis_count=0, redshift_count=0, elastic_search_count=0):
    """
    :rtype: Service
    """
    # Simple helper method to create  a Microservice
    # Note that the vertex_type can be anything. The user decided what types are going to be available.

    # create the Microservice vertex
    service = itsdk.add_vertex(collector_id=collector_id,
                               name=name,
                               vertex_type="Service",
                               keys="vfl-service-{}".format(name))

    # create the ELB vertex
    elb = itsdk.add_vertex(collector_id=collector_id,
                           name="{}-elb".format(name),
                           vertex_type="AWS_ELB",
                           keys="vfl-service-load-balancer-{}".format(name))

    # create the Auto Scaling Group vertex
    asg = itsdk.add_vertex(collector_id=collector_id,
                           name="{}-asg".format(name),
                           vertex_type="AWS_Auto_Scaling_Group",
                           keys="vfl-service-auto-scaling-group-{}".format(name),
                           instance_count=ec2_count)

    # Connect elb and asg to the  Microservice
    itsdk.connect(collector_id=collector_id, source=service, target=elb, topology=topology)
    itsdk.connect(collector_id=collector_id, source=elb, target=asg, topology="auto_scaling_group")

    # Create EC2 instances and connect them to the asg
    ec2s = []
    for i in range(ec2_count):
        ec2 = itsdk.add_vertex(collector_id=collector_id,
                               name="i-34451660{}".format(i),
                               vertex_type="AWS_Instance",
                               keys="vfl-service-{}-ec2-{}".format(name.split(",")[0], i))
        itsdk.connect(collector_id=collector_id, source=asg, target=ec2, topology="auto_scaling_group")
        ec2s.append(ec2)

    # Create RDS and connect them to the Microservice
    rdses = []
    for i in range(rds_count):
        rds = itsdk.add_vertex(collector_id=collector_id,
                               name="MySQL {}-db{}".format(name, i),
                               vertex_type="AWS_RDS",
                               keys="vfl-service-{}-db-{}".format(name, i))
        rdses.append(rds)

        itsdk.connect(collector_id=collector_id, source=asg, target=rds, topology="uses-rds$group")

        for ec2 in ec2s:
            itsdk.connect(collector_id=collector_id, source=ec2, target=rds, topology="uses-rds")

    # Create Redshift and connect them to the Microservice
    redshifts = []
    for i in range(redshift_count):
        redshift = itsdk.add_vertex(collector_id=collector_id,
                                    name="Redshift db{}".format(i),
                                    vertex_type="AWS_Redshift",
                                    keys="vfl-service-{}-redshift-{}".format(name, i))

        redshifts.append(redshift)
        itsdk.connect(collector_id=collector_id, source=asg, target=redshift, topology="uses-redshift$group")
        for ec2 in ec2s:
            itsdk.connect(collector_id=collector_id, source=ec2, target=redshift, topology="uses-redshift")

    # Create Redis and connect them to the Microservice
    redises = []
    for i in range(redis_count):
        redis = itsdk.add_vertex(collector_id=collector_id,
                                 name="Redis cache-{}".format(i),
                                 vertex_type="AWS_Redis",
                                 keys="vfl-service-{}-cache-{}".format(name, i))

        redises.append(redis)
        itsdk.connect(collector_id=collector_id, source=asg, target=redis, topology="uses-redis$group")
        for ec2 in ec2s:
            itsdk.connect(collector_id=collector_id, source=ec2, target=redis, topology="uses-redis")

    # Create Elastic Search and connect them to the Microservice
    elastic_searches = []
    for i in range(elastic_search_count):
        es = itsdk.add_vertex(collector_id=collector_id,
                              name="ElasticSearch-{}".format(i),
                              vertex_type="AWS_Elastic_Search",
                              keys="vfl-service-{}-elastic-search{}".format(name, i))

        elastic_searches.append(es)
        itsdk.connect(collector_id=collector_id, source=asg, target=es, topology="uses-elastic-search$group")
        for ec2 in ec2s:
            itsdk.connect(collector_id=collector_id, source=ec2, target=es, topology="uses-elastic-search")

    service = Service(service=service,
                      elb=elb,
                      asg=asg,
                      ec2s=ec2s,
                      rdses=rdses,
                      redshifts=redshifts,
                      redises=redises,
                      elastic_searches=elastic_searches)
    return service


if __name__ == '__main__':
    # Initialize SDK to send data directly to the cloud

    # itsdk.init(server_url="http://localhost:5000/api/v1", api_key=api_key, api_secret=api_secret)
    # itsdk.init(role="cloudoscope")
    itsdk.init(server_url="http://localhost:5000/api/v1")

    ########################################################################
    # Step 1 - Create Topology
    ########################################################################

    # Create the s3 Vertex:
    bucket = itsdk.add_vertex(collector_id=collector_id,
                              name="raw-payload",
                              vertex_type="S3",
                              keys="vfl-raw-payload")

    # Defining the first service:
    # Create the s3 Vertex:
    a_lambda = itsdk.add_vertex(collector_id=collector_id,
                                name="raw-payload-uploaded",
                                vertex_type="Lambda",
                                keys="vfl-lambda-payload-uploaded")

    tenant_management_service = create_microservice(name="tenant-management",
                                                    ec2_count=4,
                                                    redis_count=1,
                                                    rds_count=1)

    malware_analyzer = create_microservice(name="malware-analyzer",
                                           ec2_count=4,
                                           rds_count=1,
                                           redis_count=2,
                                           elastic_search_count=1)

    # connect the  bucket to lambda to Microservice
    itsdk.connect(collector_id=collector_id,
                  source=bucket,
                  target=a_lambda,
                  topology=topology)

    itsdk.connect(collector_id=collector_id,
                  source=a_lambda,
                  target=malware_analyzer.service,
                  topology="malware_analyzer-service")

    for ec2 in malware_analyzer.ec2s:
        itsdk.connect(collector_id=collector_id,
                      source=ec2,
                      target=tenant_management_service.rdses[0],
                      topology="uses-rds")

    itsdk.connect(collector_id=collector_id,
                  source=malware_analyzer.asg,
                  target=tenant_management_service.rdses[0],
                  topology="uses-rds$group")

    # Flush and commit topology
    itsdk.flush_all()

    # mockup timeseries
    feel_pain_vertices = [tenant_management_service.service, tenant_management_service.elb,
                          tenant_management_service.asg] + tenant_management_service.ec2s
    cause_pain_vertices = [malware_analyzer.service, malware_analyzer.elb, malware_analyzer.asg] + malware_analyzer.ec2s
    contention_vertices = [tenant_management_service.rdses[0]]

    feel_pain = None
    for fp in feel_pain_vertices:
        if fp.type in ("AWS_ELB", "AWS_ALB"):
            feel_pain = fp
            break
    cause_pain = None
    for cp in cause_pain_vertices:
        if cp.type in ("AWS_ELB", "AWS_ALB"):
            cause_pain = cp
            break

    vertex_unhealthy = None
    for cv in contention_vertices:
        vertex_unhealthy = cv
        break

    message = "ELB {} is experiencing High Latency as a result of contention on RDS {}. " \
              "That contention is cause by high request activity from ELB {}".format(feel_pain.name,
                                                                                     vertex_unhealthy.name,
                                                                                     cause_pain.name)

    mockup_samples(itsdk=itsdk,
                   vertices=tenant_management_service.vertices + malware_analyzer.vertices + [a_lambda],
                   feel_pain_vertices=feel_pain_vertices,
                   cause_pain_vertices=cause_pain_vertices,
                   contention_vertices=contention_vertices,
                   message=message,
                   vertex_unhealthy=vertex_unhealthy)



