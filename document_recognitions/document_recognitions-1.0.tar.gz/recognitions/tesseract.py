import logging
import os
import shlex
import subprocess
import tempfile

tesseract_cmd = 'tesseract'


def run_tesseract(input_filename, output_filename_base, lang=None, config=None):
    command = [tesseract_cmd, input_filename, output_filename_base]
    if lang is not None:
        command += ['-l', lang]

    if config:
        command += shlex.split(config)
    subprocess.call(command)


def cleanup(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def get_errors(error_string):
    error_string = error_string.decode('utf-8')
    lines = error_string.splitlines()
    error_lines = tuple(line for line in lines if line.find('Error') >= 0)
    if len(error_lines) > 0:
        return '\n'.join(error_lines)
    else:
        return error_string.strip()


def temp_name(prefix):
    temp_file = tempfile.NamedTemporaryFile(prefix=prefix)
    return temp_file.name


class TesseractError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        self.args = (status, message)
        self.logger = logging.getLogger(__name__)


def image_to_string(image_path, lang=None, config=None):
    output_file_name_base = temp_name(prefix='tess_')
    output_file_name = '%s.txt' % output_file_name_base
    try:
        run_tesseract(
            image_path,
            output_file_name_base,
            lang=lang,
            config=config
        )
        with open(output_file_name, 'rb') as f:
            return f.read().decode('utf-8').strip()
    finally:
        cleanup(output_file_name)
