import random

import itculate_sdk as itsdk
from unix_dates import UnixDate, UnixTimeDelta

api_key = "5PLZZM6T94UPTXOUS3LPW2AN0"
api_secret = "+r7BEShhSmDldVgwxQa3NgXcJloiOVhxsLVvDvpqIlQ"

itsdk.init(api_key=api_key, api_secret=api_secret)

collector_id = "cimpress_sdk"
topology = "data-process-pipeline"


# NiFi connects to FTP/SFTP/HTTPS data sources.
# The downloaded data is in XML/CSV/JSON format.
# NiFi parses the data and converts it to JSON.
protocol_vertices = []
kafka_topics_vertices = []
for protocol in ["FTP", "SFTP", "HTTPS"]:
    # create vertex per protocol
    protocol_vertex = itsdk.add_vertex(collector_id=collector_id,
                                       name=protocol,
                                       vertex_type="NiFi-Connector",
                                       keys="nifi-connector-{}".format(protocol.lower()))
    protocol_vertices.append(protocol_vertex)

    # NiFi sends the JSON to Kafka topics
    kafka_topic_vertex = itsdk.add_vertex(collector_id=collector_id,
                                          name="{}-topic".format(protocol),
                                          vertex_type="Kafka_Topic",
                                          keys="kafka-topic-{}".format(protocol.lower()))

    kafka_topics_vertices.append(kafka_topic_vertex)

    itsdk.connect(collector_id=collector_id, source=protocol_vertex, target=kafka_topic_vertex, topology=topology)


# Cimpress teams send JSON messages to AWS API Gateway
# JSON messages go to Kafka topics -> #3
api_gateway_vertex = itsdk.add_vertex(collector_id=collector_id,
                                      name="team.post",
                                      vertex_type="AWS_API_Gateway",
                                      keys="team.post")

kafka_api_topic_vertex = itsdk.add_vertex(collector_id=collector_id,
                                          name="api-post-topic",
                                          vertex_type="Kafka_Topic",
                                          keys="api-post-topic")

itsdk.connect(collector_id=collector_id, source=api_gateway_vertex, target=kafka_api_topic_vertex, topology=topology)


# Spark jobs
# - take messages off Kafka topics
# - parse the messages
# - store the messages in Redshift
spark_job_vertex = itsdk.add_vertex(collector_id=collector_id,
                                    name="message-processor",
                                    vertex_type="Spark_Jobs",
                                    keys="message-processor")

# connect all the kafka topic vertices to the spark job
itsdk.connect(collector_id=collector_id, source=kafka_api_topic_vertex, target=spark_job_vertex, topology=topology)
itsdk.connect(collector_id=collector_id, source=kafka_topics_vertices, target=spark_job_vertex, topology=topology)


# create the Redshift database
redshift_vertex = itsdk.add_vertex(collector_id=collector_id,
                                   name="database",
                                   vertex_type="AWS_Redshift",
                                   keys="redshift")

itsdk.connect(collector_id=collector_id, source=spark_job_vertex, target=redshift_vertex, topology=topology)


# create the Redshift database
looker_vertex = itsdk.add_vertex(collector_id=collector_id,
                                 name="user",
                                 vertex_type="Looker",
                                 keys="looker")

# connect the looker vertex to redshift
itsdk.connect(collector_id=collector_id, source=looker_vertex, target=redshift_vertex, topology=topology)

itsdk.flush_all()


# What I am interested in (As a prototype)
# - see that connection to a data source was done as scheduled
# - that every step was successful (download, parse, convert, kafka, spark, redshift etc)
# - the tricky part is to see that a specific piece of data made it all the way through after being downloaded
