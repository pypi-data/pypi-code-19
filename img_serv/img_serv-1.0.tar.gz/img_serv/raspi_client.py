from picamera import PiCamera
from time import sleep
from datetime import datetime

class RaspiClient():
    def __init__(self, filename = 'image.jpg', location = 'images', ip = 'localhost', port = 12222, exitKey = 'x', captureKey = 'c', windowTitle = 'ImgServ DesktopClient'):
        self.filename = filename
        self.location = location
        self.ip = ip
        self.port = port
        self.url = 'http://' + self.ip + ':' + str(self.port)

        self.windowTitle = windowTitle
        self.exitKey = exitKey
        self.captureKey = captureKey

    def start(self):
        cam = PiCamera()
        cam.start_preview()

        while(True):
            response = input('Enter \''+ self.captureKey + '\' to capture the image\n')

            if response == self.captureKey:
                cam.capture(self.filename)

                with open(self.filename, 'rb') as f:
                    r = requests.post(self.url, files={self.filename: f})
            elif response == self.exitKey:
                break

        cam.stop_preview()


