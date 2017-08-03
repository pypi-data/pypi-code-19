
from spark_basic_python.com.tf56.sparkbasic.contextfactory import ContextFactory
from spark_basic_python.com.tf56.util import configloader
from pyspark.streaming.kafka import KafkaUtils


class CreateKafkaDstream:
    def __init__(self):
        print("")

    @staticmethod
    def buildkafkadstream():
        config_map = configloader.buildconfig("sparkbasic.ini")
        kafka_params = {"metadata.broker.list": config_map.get("kafka", "metadata.broker.list"),
                        "group.id": config_map.get("group.id"),
                        "auto.offset.reset": config_map.get("kafka", "auto.offset.reset")}

        kvs = KafkaUtils.createDirectStream(ContextFactory.buildstreamingcontext(),
                                            [config_map.get("kafka", "kafka.consumer.topic")],
                                            kafka_params)
        return kvs


