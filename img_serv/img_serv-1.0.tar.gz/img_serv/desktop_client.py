import cv2
import requests
import os

class DesktopClient():
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
        cam = cv2.VideoCapture(0)
        while(True):
            _ , frame = cam.read()
            cv2.imshow(self.windowTitle, frame)
            ch = cv2.waitKey(20)

            if chr(ch & 255) == self.exitKey:
                break

            if chr(ch & 255) == self.captureKey:
                if not os.path.exists(self.location):
                    os.makedirs(self.location)

                path = os.path.join(self.location, self.filename)
                cv2.imwrite(path,frame)
                with open(path, 'rb') as f:
                    r = requests.post(self.url, files={self.filename: f})

        cam.release()
        cv2.destroyAllWindows()

