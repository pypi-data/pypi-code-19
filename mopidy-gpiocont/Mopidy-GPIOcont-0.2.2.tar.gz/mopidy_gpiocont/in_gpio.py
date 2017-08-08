import logging
logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
except ImportError:
    logger.error("GPIOcont: Could not open GPIO")




logger.debug("GPIOcont: input_gpio.py called.")


class in_GPIO():
    def __init__(self, frontend, conf):
        self.frontend = frontend
        self.conf = conf

        deb_time = 200  # The debounce time for the buttons in ms
        vol_deb_time = conf['vol_bounce_time'] #Debounce time for rotary encoder in ms


        try:
            # set pin mode to BCM
            GPIO.setmode(GPIO.BCM)


            # Play button
            GPIO.setup(conf['play_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(conf['play_pin'], GPIO.FALLING, callback=self.play, bouncetime=deb_time)

            #Next/previous
            GPIO.setup(conf['next_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(conf['prev_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(conf['next_pin'], GPIO.FALLING, callback=self.switch, bouncetime=deb_time)
            GPIO.add_event_detect(conf['prev_pin'], GPIO.FALLING, callback=self.switch, bouncetime=deb_time)

            #Volume rotary encoder
            GPIO.setup(conf['vol_a_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(conf['vol_b_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(conf['vol_a_pin'], GPIO.BOTH, callback=self.volume, bouncetime=vol_deb_time)

            #Dedicated playlist pins
            GPIO.setup(conf['list1_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(conf['list2_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(conf['list3_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(conf['list4_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)

            GPIO.add_event_detect(conf['list1_pin'], GPIO.FALLING, callback=self.list, bouncetime=deb_time)
            GPIO.add_event_detect(conf['list2_pin'], GPIO.FALLING, callback=self.list, bouncetime=deb_time)
            GPIO.add_event_detect(conf['list3_pin'], GPIO.FALLING, callback=self.list, bouncetime=deb_time)
            GPIO.add_event_detect(conf['list4_pin'], GPIO.FALLING, callback=self.list, bouncetime=deb_time)


            logger.debug("GPIOcont: pin events added.")
        except RuntimeError:
            logger.error("GPIOcont: Not enough permission to open GPIO. do <sudo adduser mopidy gpio> to add the mopidy user to the gpio group")

    def play(self, channel):
        if GPIO.input(channel) == 0:
            self.frontend.input_event({'main': 'play', 'sub': 'none'})


    #Todo Make volume control more stable.
    def volume(self, channel):
        if GPIO.input(channel)==1: #it was a rising edge
            if GPIO.input(self.conf['vol_b_pin']) == 0: #clockwise movement
                self.frontend.input_event({'main': 'volume', 'sub': 'up'})
            else: #counterclockwise movemnt
                self.frontend.input_event({'main': 'volume', 'sub': 'down'})

        else: # it was a falling edge.
            if GPIO.input(self.conf['vol_b_pin']) == 1: #clockwise movement
                self.frontend.input_event({'main': 'volume', 'sub': 'up'})
            else: #counterclockwise movement
                self.frontend.input_event({'main': 'volume', 'sub': 'down'})

    def list(self, channel):
        if GPIO.input(self.conf['list1_pin']) == 0:
            self.frontend.input_event({'main': 'list', 'sub': self.conf['list1_name']})
        elif GPIO.input(self.conf['list2_pin']) == 0:
            self.frontend.input_event({'main': 'list', 'sub': self.conf['list2_name']})
        elif GPIO.input(self.conf['list3_pin']) == 0:
            self.frontend.input_event({'main': 'list', 'sub': self.conf['list3_name']})
        elif GPIO.input(self.conf['list4_pin']) == 0:
            self.frontend.input_event({'main': 'list', 'sub': self.conf['list4_name']})

    def switch(self, channel):
        if GPIO.input(self.conf['next_pin']) == 0:
            self.frontend.input_event({'main': 'switch', 'sub': 'next'})
        elif GPIO.input(self.conf['prev_pin']) == 0:
            self.frontend.input_event({'main': 'switch', 'sub': 'prev'})
