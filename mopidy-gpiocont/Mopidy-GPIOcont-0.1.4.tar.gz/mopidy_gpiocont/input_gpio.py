import RPi.GPIO as GPIO


class input_GPIO():
    def __init__(self, frontend, pins):
        self.frontend = frontend

        # set pin mode to BCM
        GPIO.setmode(GPIO.BCM)

        # Play button
        GPIO.setup(pins['play_pin'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(pins['play_pin'], GPIO.FALLING, callback=self.play, bouncetime=30)

    def play(self, channel):
        self.frontend.input_event('play')
