from time import sleep
from threading import Thread


class Cube:

    def __init__(self, faces):
        self.faces = faces
        self.threads = []

    def start(self):
        self.threads = []

        for index, face in enumerate(self.faces):
            face.set_index(index)
            thread = Thread(target=face.start, daemon=True)
            self.threads.append(thread)

        for thread in self.threads:
            thread.start()

        try:
            while True:
                sleep(1337)
        except KeyboardInterrupt:
            try:
                print('Soft stopping...')

                for face in self.faces:
                    print('Sending stop request')
                    face.request_stop()

                for thread in self.threads:
                    print('Waiting for this face...')
                    thread.join()
                    print('Face stopped.')

            except KeyboardInterrupt:
                print('Force stop!')

        print('Cube stopped.')
