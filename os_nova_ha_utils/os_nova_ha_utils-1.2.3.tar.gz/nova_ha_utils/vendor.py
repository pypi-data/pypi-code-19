import subprocess


def get_vendor_name():
    return subprocess.check_output(['dmidecode', '-s', 'system-manufacturer']).rstrip()
