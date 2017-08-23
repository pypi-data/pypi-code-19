import os
import random
import subprocess
import time
import http.server


MAC_CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


class Peeker:
    def __init__(self, prefix='kaeru_', ext='.html'):
        self.tempfile_name = (
            prefix + ''.join(random.sample('harukaeru0123456789', 9)) + ext
        )

    def write_in_tempfile(self, text):
        with open(self.tempfile_name, 'w') as f:
            f.write(text)

    def delete_tempfile(self):
        os.remove(self.tempfile_name)

    def open(self):
        subprocess.run([MAC_CHROME, self.tempfile_name])

    def message(self):
        print('Start Chrome')


class FixPeeker(Peeker):
    """Using http server. This class is used in Vagrant"""

    def __init__(self, prefix='kaeru_fixpeekertemp', ext='.html'):
        self.tempfile_name = prefix + ext

    def open(self):
        httpd = http.server.HTTPServer(
            ("0.0.0.0", 9000), http.server.SimpleHTTPRequestHandler
        )
        httpd.serve_forever()

    def message(self):
        location = f"http://localhost:9000/{self.tempfile_name}"
        print(f"Open Browser and Check {location}")


def peek(text, peeker_class=Peeker):
    if text == '':
        print('No text')
    peeker = peeker_class()
    try:
        peeker.write_in_tempfile(text)
        peeker.message()
        peeker.open()
        while 1:
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        peeker.delete_tempfile()


def fixpeek(text):
    peek(text, peeker_class=FixPeeker)
