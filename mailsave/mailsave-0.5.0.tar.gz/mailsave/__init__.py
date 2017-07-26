import os
import sys

from datetime import datetime
from mailbox import mboxMessage
from os.path import join


__version__ = '0.5.0'


def save(content, folder='.', filename=None):
    mbox = mboxMessage(message=content)
    to = mbox['to']
    from_ = mbox.get_from()

    try:
        os.makedirs(folder, exist_ok=True)
    except FileExistsError:
        print('{} is a file'.format(folder), file=sys.stderr)
    else:
        date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_name = filename or '{date}.mbox'
        file_name = file_name.format(date=date, to=to, from_=from_)
        file_path = join(folder, file_name)
        mode = 'wb' if isinstance(content, bytes) else 'w'

        with open(file_path, mode) as output:
            output.write(content)
