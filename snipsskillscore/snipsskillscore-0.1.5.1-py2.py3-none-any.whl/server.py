# -*-: coding utf-8 -*-
""" Snips core server. """

import json
import time

from socket import error as socket_error

import paho.mqtt.client as mqtt

from snipsskillscore import logging
from snipsskillscore.logging import log
from snipsskillscore.thread_handler import ThreadHandler
from snipsskillscore.intent_parser import IntentParser


class Server():
    """ Snips core server. """

    def __init__(self, config, registry, handle_intent):
        """ Initialisation.

        :param config: a YAML configuration.
        :param assistant: the client assistant class, holding the
                          intent handler and intents registry.
        """
        self.config = config
        self.registry = registry
        self.handle_intent = handle_intent
        self.threading = ThreadHandler()

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.mqtt_hostname = config.mqtt_hostname
        self.mqtt_port = config.mqtt_port

        logging.LOGGING_ENABLED = config.logging

    def start(self):
        """ Start the MQTT client. """
        self.threading.run(target=self.start_blocking)
        self.threading.start_run_loop()

    def start_blocking(self, run_event):
        """ Start the MQTT client, as a blocking method.

        :param run_event: a run event object provided by the thread handler.
        """
        topic = "#"
        log("Connecting to {} on port {}".format(self.mqtt_hostname,
                                                 str(self.mqtt_port)))
        while True and run_event.is_set():
            try:
                log("Trying to connect to {}".format(self.mqtt_hostname))
                self.client.connect(self.mqtt_hostname, self.mqtt_port, 60)
                break
            except socket_error:
                time.sleep(5)
        self.client.subscribe(topic, 0)
        while run_event.is_set():
            self.client.loop()

    # pylint: disable=unused-argument,no-self-use
    def on_connect(self, client, userdata, flags, result_code):
        """ Callback when the MQTT client is connected.

        :param client: the client being connected.
        :param userdata: unused.
        :param flags: unused.
        :param result_code: result code.
        """
        log("Connected with result code {}".format(result_code))
        # self.state_handler.set_state(C.State.welcome)

    # pylint: disable=unused-argument
    def on_disconnect(self, client, userdata, result_code):
        """ Callback when the MQTT client is disconnected. In this case,
            the server waits five seconds before trying to reconnected.

        :param client: the client being disconnected.
        :param userdata: unused.
        :param result_code: result code.
        """
        log("Disconnected with result code " + str(result_code))
        # self.state_handler.set_state(C.State.goodbye)
        time.sleep(5)
        self.start()

    # pylint: disable=unused-argument
    def on_message(self, client, userdata, msg):
        """ Callback when the MQTT client received a new message.

        :param client: the MQTT client.
        :param userdata: unused.
        :param msg: the MQTT message.
        """
        log("New message on topic {}: {}".format(msg.topic, str(msg.payload)))
        if msg.topic == "hermes/nlu/intentParsed" and msg.payload:
            payload = json.loads(msg.payload.decode('utf-8'))
            intent = IntentParser.parse(payload, self.registry.intent_classes)
            if self.handle_intent:
                self.handle_intent(intent)

        # if msg.topic == "hermes/hotword/toggleOn":
        #     self.state_handler.set_state(C.State.hotword_toggle_on)
        # elif msg.topic == "hermes/hotword/detected":
        #     if not self.first_hotword_detected:
        #         self.client.publish(
        #             "hermes/feedback/sound/toggleOff", payload=None, qos=0, retain=False)
        #         self.first_hotword_detected = True
        #     else:
        #         self.state_handler.set_state(C.State.hotword_detected)
        # elif msg.topic == "hermes/asr/toggleOn":
        #     self.state_handler.set_state(C.State.asr_toggle_on)
        # elif msg.topic == "hermes/asr/textCaptured":
        #     self.state_handler.set_state(C.State.asr_text_captured)
        # elif (msg.topic == "hermes/nlu/intentParsed" or msg.topic == "system") and msg.payload:
        #     self.handle_intent(json.loads(msg.payload.decode('utf-8')))
        # elif (msg.topic == "hermes/leds") and msg.payload:
        #     self.handle_leds(json.loads(msg.payload.decode('utf-8')))
        # elif (msg.topic == "hermes/sound") and msg.payload:
        #     self.handle_sound(json.loads(msg.payload.decode('utf-8')))
