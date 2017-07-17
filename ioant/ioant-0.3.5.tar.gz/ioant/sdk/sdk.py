# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
import paho.mqtt.client as mqtt
import time
from .. import utils

# These imports are auto generated files.
import messages_pb2 as messages
import proto_io as ProtoIO
from google.protobuf.message import Message
# These imports are auto generated files.
import logging
logger = logging.getLogger(__name__)


class IOAnt:
    SDK_VERSION = "0.2.0"
    on_message_callback = None
    on_connect_callback = None
    mqtt_client = None
    loaded_configuration = None
    delay = 1000
    device_topic = None
    is_initial_connect = True

    def __init__(self, connect_callback, message_callback):
        """ Constructor """
        self.on_message_callback = message_callback
        self.on_connect_callback = connect_callback


    def setup(self, configuration):
        """ Setup """
        logger.debug("Attempting connect to: " +
                     configuration['ioant']['mqtt']['broker'] +
                     " " + str(configuration['ioant']['mqtt']['port']))
        self.loaded_configuration = configuration
        self.mqtt_client = mqtt.Client(configuration['ioant']['mqtt']['client_id'])
        self.mqtt_client.username_pw_set(configuration['ioant']['mqtt']['user'], configuration['ioant']['mqtt']['password'])
        self.mqtt_client.on_connect = self.__on_connect
        self.mqtt_client.on_message = self.__on_message
        self.mqtt_client.connect(configuration['ioant']['mqtt']['broker'],
                                 configuration['ioant']['mqtt']['port'],
                                 60)
        self.delay = configuration['ioant']['communication_delay']
        self.device_topic = self.get_topic_structure()
        self.device_topic['top'] = 'live'
        self.device_topic['global'] = configuration['ioant']['mqtt']['global']
        self.device_topic['local'] = configuration['ioant']['mqtt']['local']
        self.device_topic['client_id'] = configuration['ioant']['mqtt']['client_id']

    def update_loop(self):
        """ Updates the mqtt loop - checking for messages """
        logger.debug("Loop Tick!")
        time.sleep(self.delay/1000)
        rc = self.mqtt_client.loop()
        if rc is not 0:
            logger.error("No connection!")
            self.mqtt_client.reconnect()

    def subscribe(self, topic):
        """ subscribe to a topic """
        subscription = topic['top'] +\
                       "/" + topic['global'] +\
                       "/" + topic['local'] +\
                       "/"+ topic['client_id']+"/"

        if topic['message_type'] == -1:
            subscription += '+/'
        else:
            subscription += str(topic['message_type'])+"/"

        if topic['stream_index'] == -1:
            subscription += '#'
        else:
            subscription += str(topic['stream_index'])

        logger.debug("Subscribed to:" + subscription)
        self.mqtt_client.subscribe(subscription)

    def publish(self, message, topic=None):
        """ publish message with topic """
        payload = message.SerializeToString()
        stream_index = 0
        if topic is None:
            topic = self.device_topic
        if topic['stream_index'] >= 0:
            stream_index = topic['stream_index']
        if topic['top'] == '+' or len(topic['top']) < 1:
            topic['top'] = self.device_topic['top']
        if topic['global'] == '+' or len(topic['global']) < 1:
            topic['global'] = self.device_topic['global']
        if topic['local'] == '+' or len(topic['local']) < 1:
            topic['local'] = self.device_topic['local']
        if topic['client_id'] == '+' or len(topic['client_id']) < 1:
            topic['client_id'] = self.loaded_configuration['ioant']['mqtt']['client_id']

        topic_string = topic['top'] + "/" + topic['global'] + "/" + topic['local'] + "/" + topic['client_id'] + "/" + str(ProtoIO.message_type_index_dict[message.DESCRIPTOR.name]) + "/" + str(stream_index)
        (result, mid) = self.mqtt_client.publish(topic_string, bytearray(payload))

        if result is not 0:
            logger.debug("Message sent with topic:" + topic_string)
            return True
        else:
            logger.debug("Failed to publish message with topic:" + topic_string)
            return False

    def __on_message(self, client, obj, message):
        """ When message is recieved from broker """
        logger.debug("Message received")
        if self.on_message_callback is not None:
            topic_dict = self.get_topic_from_string(str(message.topic))
            try:
                decoded_message = ProtoIO.create_proto_message(topic_dict['message_type'])
                decoded_message.ParseFromString(message.payload)
            except:
                logger.debug("Failed to decode message")
                return

            self.on_message_callback(topic_dict, decoded_message)

    def __publish_bootinfo(self):
        """ Publish boot info """
        logger.debug("Boot info")
        bootinfo_msg = self.create_message("BootInfo")
        bootinfo_msg.platform = bootinfo_msg.Platforms.Value('OTHER')
        bootinfo_msg.information = "start"
        bootinfo_msg.ip_address = '0.0.0.0'
        bootinfo_msg.sdk_version = self.SDK_VERSION
        bootinfo_msg.proto_version = messages.ProtoVersion.Value('VERSION')
        bootinfo_msg.communication_delay = self.loaded_configuration["ioant"]["communication_delay"]
        bootinfo_msg.broker_connect_attempts = 1
        bootinfo_msg.longitude = self.loaded_configuration["ioant"]["longitude"]
        bootinfo_msg.latitude = self.loaded_configuration["ioant"]["latitude"]
        bootinfo_msg.app_generic_a = self.loaded_configuration["ioant"]["app_generic_a"]
        bootinfo_msg.app_generic_b = self.loaded_configuration["ioant"]["app_generic_b"]
        bootinfo_msg.app_generic_c = self.loaded_configuration["ioant"]["app_generic_c"]

        self.publish(bootinfo_msg)

    def __on_connect(self, client, userdata, flags, rc):
        """ When client connects to broker """
        logger.debug("Connected with rc code: " + str(rc))
        if rc == 0:
            if self.is_initial_connect:
                self.__publish_bootinfo()
                self.is_initial_connect = False
            self.on_connect_callback()
        else:
            logger.error("Failed to connect to mqtt broker: " + str(rc))

    def get_topic_structure(self):
        """ Return a empty topic structure """
        topic_dict = {}
        topic_dict['top'] = "+"
        topic_dict['global'] = "+"
        topic_dict['local'] = "+"
        topic_dict['client_id'] = "+"
        topic_dict['message_type'] = -1
        topic_dict['stream_index'] = -1
        return topic_dict

    def get_topic_from_string(self, topic):
        """ Return a populated topic structure """
        sub_topics_list = topic.split('/')
        if len(sub_topics_list) is not 6:
            return None
        else:
            topic_dict = {}
            topic_dict['top'] = sub_topics_list[0]
            topic_dict['global'] = sub_topics_list[1]
            topic_dict['local'] = sub_topics_list[2]
            topic_dict['client_id'] = sub_topics_list[3]
            topic_dict['message_type'] = int(sub_topics_list[4])
            topic_dict['stream_index'] = int(sub_topics_list[5])
            return topic_dict

    def get_message_type(self, message_name):
        """ Return message type of the given message name """
        return ProtoIO.message_type_index_dict[message_name]

    def get_message_type_name(self, message_type):
        """ Return message name of the given message type """
        return ProtoIO.index_message_type_dict[message_type]

    def get_configuration(self):
        """ Return message name of the given message type """
        return self.loaded_configuration

    def create_message(self, message_name):
        """ Return message based on message_name """
        return ProtoIO.create_proto_message(ProtoIO.message_type_index_dict[message_name])
