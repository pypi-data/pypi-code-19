import os
import random
import subprocess
import time


MAC_CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


class Peeker:
    def __init__(self, ext='.html'):
        self.tempfile_name = (
            'kaeru_' + ''.join(random.sample('harukaeru0123456789', 9)) + ext
        )

    def write_in_tempfile(self, text):
        with open(self.tempfile_name, 'w') as f:
            f.write(text)

    def delete_tempfile(self):
        os.remove(self.tempfile_name)

    def open_chrome(self):
        subprocess.run([MAC_CHROME, self.tempfile_name])


def peek(text):
    if text == '':
        print('No text')
    peeker = Peeker()
    try:
        peeker.write_in_tempfile(text)
        peeker.open_chrome()
        print('Start Chrome')
        while 1:
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        peeker.delete_tempfile()
