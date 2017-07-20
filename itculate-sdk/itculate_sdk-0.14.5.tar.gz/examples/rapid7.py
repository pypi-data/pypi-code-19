from collections import defaultdict
import pprint
from itculate_sdk.connection import ApiConnection

import itculate_sdk as itsdk
import re

# server_url = "http://localhost:5000/api/v1"
server_url = "https://api.itculate.io/api/v1"

api_key = "fwvU0f5H1eLmcKyqcauXE4nEDhPZQzWT"
api_secret = "KgelEfRDLTESk2olOnH2CJq_g2zEYrIBlYTuNzktd6HjmzCFu7_79ygQdgjh-h1D"


class Rapid7Client(object):
    def __init__(self):
        self.cid = "collector_id"

        itsdk.init(server_url=server_url, api_key=api_key, api_secret=api_secret)

        # collect instance-ids that attached to ELB (auto discovered by ITculate)
        self.elb_instances_ids = set()

        # Vertex-Type->Product->Service->Vertices
        self.tags_to_instances = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        self.service_name_to_service = {}

    @classmethod
    def create_product_key(cls, product, account):
        return {
            "old": "product:{}".format(product),
            "key": "{}|product:{}".format(account, product)
        }

    @classmethod
    def create_service_key(cls, product, service, account):
        return {
            "old": "product:{}|service:{}".format(product, service),
            "key": "{}|product:{}|service:{}".format(account, product, service)
        }

    def read_instances_from_itculate_server(self):
        """
        return a dict of dicts from the tags to list of instances

        :rtype: dict[str, dict[str, dict[str, ServerVertex]]]
        """

        tenant = "3nvQ3n6nk1j1X6nji34PB"

        service_to_products = defaultdict(lambda: defaultdict(list))

        connection = ApiConnection(api_key=api_key, api_secret=api_secret, server_url=server_url)
        raw_vertices = connection.get("tenants/{}/vertices?filter=&limit=5000".format(tenant))
        for raw_vertex in raw_vertices:
            if raw_vertex["_type"] not in ("AWS_Instance",
                                           "AWS_ELB",
                                           "AWS_S3_Bucket",
                                           "AWS_RDS",
                                           "AWS_Redis"):
                continue

            vertex = ServerVertex(rid=raw_vertex["_rid"],
                                  name=raw_vertex["_name"],
                                  region=raw_vertex["region"],
                                  vertex_type=raw_vertex["_type"],
                                  tags=raw_vertex.get("tags"),
                                  keys=raw_vertex["_keys"],
                                  service_instances_ids={v["instance-id"] for v in raw_vertex.get("instances", [])},
                                  instance_id=raw_vertex.get("instance-id"),
                                  account=raw_vertex["account"])

            if vertex.product is None or vertex.service is None:
                continue

            self.tags_to_instances[vertex.vertex_type][vertex.product][vertex.service].append(vertex)

            service_to_products[str(vertex.service)][str(vertex.product)].append(
                "{} {}".format(vertex.vertex_type.replace("AWS_", ""),
                               vertex.name))

            self.elb_instances_ids.update(vertex.service_instances_ids)

        service_to_products = {k: dict(v) for k, v in service_to_products.iteritems() if len(v) > 1}
        pprint.pprint(service_to_products)
        print service_to_products

    def create_topology(self):

        self.read_instances_from_itculate_server()

        for vertex_type, vertex_type_items in self.tags_to_instances.iteritems():

            for product, product_items in vertex_type_items.iteritems():
                # create the Product vertex
                first_vertex = product_items.values()[0][0]
                account = first_vertex.account
                region = first_vertex.region
                product_key = self.create_product_key(product=product, account=account)
                product_vertex = itsdk.add_vertex(collector_id=self.cid,
                                                  vertex_type="Product",
                                                  name=product,
                                                  keys=product_key)

                for service, service_items in product_items.iteritems():
                    # create the Service vertex, because service name can be the same cross Products
                    # the service name is product@service
                    name = ServerVertex.get_full_service_name(product=product, service=service, region=region)
                    service_key = self.create_service_key(product=product,
                                                          service=service,
                                                          account=account)
                    service_vertex = itsdk.add_vertex(collector_id=self.cid,
                                                      vertex_type="Service",
                                                      name=name,
                                                      keys=service_key)

                    self.service_name_to_service[name] = service_vertex

                    # Connect the product_vertex with service_vertex
                    itsdk.connect(collector_id=self.cid,
                                  source=product_vertex.keys,
                                  target=service_vertex.keys,
                                  topology="owns-{}".format(service))

                    if vertex_type == "AWS_Instance":
                        # the EC2 will be connected through the ELB
                        # none_elb_vertex_type_items = [v for v in service_items if
                        #                               v.instance_id not in self.elb_instances_ids]
                        # if len(none_elb_vertex_type_items) == 0:
                        #     # if all the EC2 instances belongs to ELB, do nothing
                        #     continue

                        # for the EC2 instances that do not belong to ELB, place them in the Auto Scaling Group
                        ec2_group_to_ec2s = defaultdict(list)
                        for v in service_items:
                            ec2_group_to_ec2s[v.instance_group_key].append(v)

                        for instance_group_key, ec2_instances in ec2_group_to_ec2s.iteritems():
                            # if len(ec2_instances) == 1:
                            #     # connect the instance directly to the service
                            #     itsdk.connect(collector_id=self.cid,
                            #                   source=service_vertex.keys,
                            #                   target=ec2_instances[0].keys,
                            #                   topology="ec2")
                            # else:

                            # group name is auto_scaling_group name if exist else
                            # the service name with @EC2 as suffix
                            group_name = ec2_instances[0].instance_group_name
                            group_type = ec2_instances[0].instance_group_type

                            if group_type == "AWS_Auto_Scaling_Group":
                                group_vertex_keys = group_name
                                group_topology = "auto_scaling_group"
                            elif group_type == "Cluster":
                                continue

                            else:
                                assert False, "unsupported group_type {}".format(group_type)

                            # Connect the Auto-Scaling-Group or Cluster Vertex to the Service Vertex
                            itsdk.connect(collector_id=self.cid,
                                          source=service_vertex.keys,
                                          target=group_vertex_keys,
                                          topology=group_topology)

                    else:  # it AWS resource (e.g. RDS, S3)
                        for item in service_items:
                            # Connect all the AWS resources to the Service
                            topology = vertex_type.replace("AWS_", "").lower()
                            itsdk.connect(collector_id=self.cid,
                                          source=service_vertex.keys,
                                          target=item.keys,
                                          topology=topology)

    def connect_vertices(self):
        pass
        # for source_key in (
        #         "i-0433ff11d8838a23e",
        #         "i-0c6c5007f56a05e3a",
        #         "i-021323aa101d4ed12",
        #         "i-0c107ea588df91264",
        #         "i-02b8d06bd67bfc495",
        #         "i-0cbffbf44318178d7",
        #         "i-0454e49469c935bdc",
        #         "i-07d9537d564ac7864"):
        #     itsdk.connect(collector_id=self.cid,
        #                   source=source_key,
        #                   target="arn:aws:rds:us-east-1:716756199562:db:collectorapp-replica-razor-prod-1",
        #                   topology="rest")
        #     itsdk.connect(collector_id=self.cid,
        #                   source=source_key,
        #                   target="arn:aws:rds:us-east-1:716756199562:db:collectorapp-master-razor-prod-1",
        #                   topology="rest")

        # itsdk.enable_grouper_algorithm(group_vertex_type="AWS_ELB", member_vertex_type="AWS_Instance", topology="uses")

        #
        # for target_key in ("i-0afc1f29306cbac85",
        #                    "i-0d46a1d46f61333aa",
        #                    "i-0c229d0441ff2c219",
        #                    "i-0d5021be16d175982",
        #                    "i-0f17a146475ddcee8",
        #                    "i-02372b3a8523ba46e",
        #                    "i-0939ccb9364c7e03e",
        #                    "i-06aff5281fd35d1f6",
        #                    "i-08721a4d5d8c10956",
        #                    "i-0ba6262166fff8884"):
        #
        #     itsdk.connect(collector_id=self.collector_id, source=source_key, target=target_key, topology="rest")

    def create_data_processing_pipeline(self):

        # get the service to connect
        doc_normalizer = self.service_name_to_service["insightidr@doc-normalizer/us-east-1"]
        attribution = self.service_name_to_service["insightidr@attribution/us-east-1"]
        behavior_generation = self.service_name_to_service["insightidr@behavior-generation/us-east-1"]
        incident_generation = self.service_name_to_service["insightidr@incident-generation/us-east-1"]
        rabbitmq2 = self.service_name_to_service["platform@rabbitmq2/us-east-1"]

        # the initial read s3 upload bucket key (same as name)
        s3_upload_key = "com.rapid7.razor.upload"
        topology = "s3-upload"
        itsdk.connect(collector_id=self.cid, source=s3_upload_key, target=doc_normalizer, topology=topology)

        # topology = "data-processing-pipeline"

        # topology = "queue"
        # queue = itsdk.add_vertex(collector_id=self.cid,
        #                          vertex_type="RabbitMQ_Queue",
        #                          name="doc_normalizer",
        #                          keys="normalizer")
        # itsdk.connect(collector_id=self.cid, source=doc_normalizer, target=queue, topology=topology)
        # itsdk.connect(collector_id=self.cid, source=queue, target=attribution, topology=topology)
        itsdk.connect(collector_id=self.cid,
                      source=doc_normalizer,
                      target=attribution,
                      topology="uses-attribution")

        # queue = itsdk.add_vertex(collector_id=self.cid,
        #                          vertex_type="RabbitMQ_Queue",
        #                          name="attribution",
        #                          keys="attribution")
        #
        # itsdk.connect(collector_id=self.cid, source=attribution, target=queue, topology=topology)
        # itsdk.connect(collector_id=self.cid, source=queue, target=behavior_generation, topology=topology)
        itsdk.connect(collector_id=self.cid, source=attribution,
                      target=behavior_generation,
                      topology="uses-behavior_generation")

        # queue = itsdk.add_vertex(collector_id=self.cid,
        #                          vertex_type="RabbitMQ_Queue",
        #                          name="behavior generation",
        #                          keys="behavior_generation")
        # itsdk.connect(collector_id=self.cid, source=behavior_generation, target=queue, topology=topology)
        # itsdk.connect(collector_id=self.cid, source=queue, target=behavior_incident, topology=topology)
        itsdk.connect(collector_id=self.cid,
                      source=behavior_generation,
                      target=incident_generation,
                      topology="uses-incident_generation")

        s3_payload_key = "com.rapid7.razor.payload"
        topology = "s3-payload"
        itsdk.connect(collector_id=self.cid, source=s3_payload_key, target=doc_normalizer, topology=topology)
        itsdk.connect(collector_id=self.cid, source=s3_payload_key, target=attribution, topology=topology)
        itsdk.connect(collector_id=self.cid, source=s3_payload_key, target=behavior_generation, topology=topology)
        itsdk.connect(collector_id=self.cid, source=s3_payload_key, target=incident_generation, topology=topology)

    def create_razor_ui(self):

        # Direct attach all the datastores to the razor_ui
        razor_ui_service = self.service_name_to_service["insightidr@razor-ui/us-east-1"]

        itsdk.connect(collector_id=self.cid,
                      source=razor_ui_service,
                      target="arn:aws:rds:us-east-1:716756199562:db:customer-master-razor-prod-1",
                      topology="rds-datastores")
        itsdk.connect(collector_id=self.cid,
                      source=razor_ui_service,
                      target="arn:aws:rds:us-east-1:716756199562:db:customer-replica-razor-prod-1",
                      topology="rds-datastores")
        itsdk.connect(collector_id=self.cid,
                      source=razor_ui_service,
                      target="arn:aws:elasticache:us-east-1:716756199562:cluster:ec1bb15a4d1dce67827d",
                      topology="redis-datastores")
        itsdk.connect(collector_id=self.cid,
                      source=razor_ui_service,
                      target="arn:aws:elasticache:us-east-1:716756199562:cluster:ec1875edc13ff0069446",
                      topology="redis-datastores")
        itsdk.connect(collector_id=self.cid,
                      source=razor_ui_service,
                      target="insightidr@rapid7-cassandra|razor",
                      topology="cassandra-datastores")
        itsdk.connect(collector_id=self.cid,
                      source=razor_ui_service,
                      target="escqrazorinvestigation-razor-d0prod-r01-v005",
                      topology="elastic-search-datastores")
        itsdk.connect(collector_id=self.cid,
                      source=razor_ui_service,
                      target="escqrazornotableevents-razor-d0prod-r01-v005",
                      topology="elastic-search-datastores")

        # connect service dependencies
        service_dependencies = [
            self.service_name_to_service["insightidr@statistics/us-east-1"],
            self.service_name_to_service["insightidr@process-registry-app/us-east-1"],
            self.service_name_to_service["insightidr@endpoint-boss-app/us-east-1"],
            self.service_name_to_service["insightidr@endpoint-attribution-app/us-east-1"],
            self.service_name_to_service["insightidr@endpoint-forensics-app/us-east-1"],
            self.service_name_to_service["insightidr@razor-scheduler/us-east-1"],
            self.service_name_to_service["insightidr@endpoint-process-analyzer-app/us-east-1"],

            # insightops PRODUCT
            self.service_name_to_service["insightops@endpoint-stats-app/us-east-1"],

            # platform PRODUCT
            self.service_name_to_service["platform@platform-collector-app/us-east-1"],
            self.service_name_to_service["platform@platform-organization-app/us-east-1"],
            self.service_name_to_service["platform@platform-shuflr-app/us-east-1"],
            self.service_name_to_service["platform@cloud-monitoring/us-east-1"],
        ]

        for sd in service_dependencies:
            itsdk.connect(collector_id=self.cid,
                          source=razor_ui_service,
                          target=sd,
                          topology="uses-{}".format(sd.name))

    def connect_collector_services(self):
        platform_collector = self.service_name_to_service["platform@platform-collector-app/us-east-1"]
        insightidr_collector = self.service_name_to_service["insightidr@collector-boss/us-east-1"]
        endpoint_ingress_app = self.service_name_to_service["insightidr@endpoint-ingress-app/us-east-1"]
        itsdk.connect(collector_id=self.cid,
                      source=insightidr_collector,
                      target=platform_collector,
                      topology="uses-platform@platform-collector-app")
        itsdk.connect(collector_id=self.cid,
                      source=insightidr_collector,
                      target=endpoint_ingress_app,
                      topology="uses-insightidr@endpoint-ingress-app")


class ServerVertex(object):
    def __init__(self, rid, name, region, vertex_type, keys, tags, service_instances_ids, instance_id, account):
        """
        :param str rid: the vertex id
        :param str vertex_type: the type of the vertex
        :param dict keys: the type of the vertex
        :param dict[str, str] tags: tags of the vertex
        :param set[str] service_instances_ids: set of instance-id used by the service (currently only ELB)
        :param str vertex_type: the ec2 instance id
        """
        self.rid = rid
        self.name = name
        self.region = region
        self.keys = keys
        self.vertex_type = vertex_type
        self.tags = tags if tags else {}
        self.service_instances_ids = service_instances_ids
        self.instance_id = instance_id
        self.account = account

        # convert from camel_case to snake-case
        # I noticed that sometimes it is CamelCase and most of the time snake-case
        self.product = self.fix_camel_case(self.tags.get("Product"))
        self.service = self.fix_camel_case(self.tags.get("Service"))

        if name == "mysql scandb-master-razor-prod-1":
            self.service = "scan-blob-processor-service"
            self.product = "exposure-analytics"

        # fix service name
        if self.service:

            # fix product insightidr
            if self.service in ("process-registry-app", "endpoint-ingress-app"):
                self.product = "insightidr"

            # fix name for:
            #     platform-org-app-razor-prod-1
            #     org-app-public-razor-prod-1
            #     mysql platform-org-app-master-razor-prod-1
            self.service = self.service.replace("-org-", "-organization-")

            # fix dev port from dev-portal to devportal
            if self.service in ('dev-portal',):
                self.service = self.service.replace("-", "")

            # sometimes the service missing -app suffix (e.g. RDS) fix it
            elif self.service in ('endpoint-attribution',
                                  "endpoint-process-analyzer",
                                  "platform-certificate-management",
                                  "process-registry",
                                  "endpoint-boss",
                                  ):
                self.service += "-app"

            # the service tag for ELB or ELB instances sometimes endswith "-service" fix it.
            elif self.service.endswith("-service"):
                self.service = self.service.replace("-service", "")

            if self.tags and self.product and self.service:
                self.full_service_name = self.get_full_service_name(product=self.product,
                                                                    service=self.service,
                                                                    region=self.region)
                if "aws:autoscaling:groupName" in self.tags:
                    # str () temp solution for unicode bug, will be fixed in the next sdk release 0.10.1 ...
                    self.instance_group_name = str(self.tags.get("aws:autoscaling:groupName"))
                    self.instance_group_key = self.instance_group_name
                    self.instance_group_type = "AWS_Auto_Scaling_Group"
                elif "Cluster" in self.tags:
                    # str () temp solution for unicode bug, will be fixed in the next sdk release 0.10.1 ...
                    self.instance_group_name = str(self.tags.get("Cluster"))
                    self.instance_group_type = "Cluster"
                    self.instance_group_key = "{}|{}".format(self.full_service_name, self.instance_group_name)

                else:
                    self.instance_group_name = "{} EC2".format(self.full_service_name)
                    self.instance_group_type = "Cluster"
                    self.instance_group_key = self.instance_group_name
            else:
                self.full_service_name = None
                self.instance_group_name = None
                self.instance_group_type = None
                self.instance_group_key = None

    @classmethod
    def get_full_service_name(cls, product, service, region):
        return "{}@{}/{}".format(product, service, region)

    def __str__(self):
        return "{}.{} {} ({})".format(self.product, self.service, self.name, self.vertex_type)

    @classmethod
    def fix_camel_case(cls, name):
        if name is None:
            return None

        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()


if __name__ == '__main__':
    client = Rapid7Client()
    client.create_topology()
    client.connect_vertices()
    client.create_razor_ui()
    client.create_data_processing_pipeline()
    client.connect_collector_services()
    # itsdk.vertex_unhealthy(vertex="i-079388e1b76348bfb", message="Failed ....")
    # itsdk.vertex_healthy(vertex="i-079388e1b76348bfb", message="Failed ....")
    # itsdk.vertex_event(vertex="i-079388e1b76348bfb", message="Failed ....")
    itsdk.flush_all()


