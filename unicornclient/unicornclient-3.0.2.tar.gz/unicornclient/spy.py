import os
import socket
import subprocess

def get_machine_id():
    machine_id = None
    with open('/etc/machine-id', 'r') as id_file:
        machine_id = id_file.read().strip()
    return machine_id

def get_serial():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"

    handle = open('/proc/cpuinfo', 'r')
    for line in handle:
        if line[0:6] == 'Serial':
            cpuserial = line[10:26]
    handle.close()

    return cpuserial

def get_hostname():
    return socket.gethostname()

def get_local_ip():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(5)
    client.connect(("8.8.8.8", 53))
    local_ip = client.getsockname()[0]
    client.close()
    return local_ip

def get_macs():
    result = {}
    root_dir = '/sys/class/net'
    interfaces = os.listdir(root_dir)
    for interface in interfaces:
        if interface == 'lo' or interface.startswith('br') or interface.startswith('docker') or interface.startswith('veth'):
            continue
        with open(os.path.join(root_dir, interface, 'address'), 'r') as interface_file:
            result[interface] = interface_file.read().strip()
    return result

def get_ssid():
    try:
        ssid = subprocess.check_output('iwgetid -r', shell=True)
    except subprocess.CalledProcessError:
        return None
    return ssid.decode().strip()

def get_temp():
    path = "/sys/class/thermal/thermal_zone0/temp"
    if not os.path.exists(path):
        return None
    temp_file = open(path, "r")
    temp_raw = int(temp_file.read().strip())
    temp_file.close()
    temp = float(temp_raw / 1000.0)
    return temp

def get_signal_level():
    path = "/proc/net/wireless"
    if not os.path.exists(path):
        return None
    wireless_file = open(path, "r")
    lines = wireless_file.read().strip().split("\n")
    wireless_file.close()
    if len(lines) < 3:
        return None
    last_line = lines[-1]
    values = last_line.split()
    if len(values) < 4:
        return None
    return int(float(values[3]))

def get_written_kbytes():
    base_path = '/sys/fs/ext4/mmcblk0p2'
    files = ['session_write_kbytes', 'lifetime_write_kbytes']

    found = False
    result = {}
    for file_name in files:
        path = os.path.join(base_path, file_name)
        if os.path.exists(path):
            stat_file = open(path, "r")
            name = file_name.split('_')[0]
            result[name] = int(stat_file.read().strip())
            stat_file.close()
            found = True

    if found:
        return result
    return None

def get_uptime():
    path = '/proc/uptime'
    if not os.path.exists(path):
        return None

    uptime_file = open(path, "r")
    uptime_seconds = float(uptime_file.readline().split()[0])
    uptime_file.close()
    return uptime_seconds
