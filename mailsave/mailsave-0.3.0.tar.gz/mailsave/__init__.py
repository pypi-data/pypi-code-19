import os
import sys

from datetime import datetime
from os.path import join


def save(content, folder='.'):
    try:
        os.makedirs(folder, exist_ok=True)
    except FileExistsError:
        print('{} is a file'.format(folder), file=sys.stderr)
    else:
        file_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.mbox')
        file_path = join(folder, file_name)
        mode = 'wb' if isinstance(content, bytes) else 'w'

        with open(file_path, mode) as output:
            output.write(content)
