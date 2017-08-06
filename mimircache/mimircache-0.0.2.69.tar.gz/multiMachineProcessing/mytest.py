

import os, base64, traceback, time, sys, pickle
import socket
import paramiko

HOSTNAME="node3"
HOSTNAME="mjolnir.mathcs.emory.edu"
PORT=22
USERNAME="jason"



# key = paramiko.RSAKey(data=base64.b64decode(b'AAA...'))


try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOSTNAME, PORT))
except Exception as e:
    print('*** Connect failed: ' + str(e))
    traceback.print_exc()
    sys.exit(1)


t = paramiko.Transport(sock)
try:
    t.start_client()
except paramiko.SSHException:
    print('*** SSH negotiation failed.')
    sys.exit(1)

try:
    keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
except IOError:
    try:
        keys = paramiko.util.load_host_keys(os.path.expanduser('~/ssh/known_hosts'))
    except IOError:
        print('*** Unable to open host keys file')
        keys = {}

key = t.get_remote_server_key()
print(key.encode())


if HOSTNAME not in keys:
    print('*** WARNING: Unknown host key!')
elif key.get_name() not in keys[HOSTNAME]:
    print('*** WARNING: Unknown host key!')
elif keys[HOSTNAME][key.get_name()] != key:
    print('*** WARNING: Host key has changed!!!')
    sys.exit(1)
else:
    print('*** Host key OK.')



# client = paramiko.SSHClient()
# host_keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
# print(host_keys)
# # client.get_remote_server_key()
# # client.get_host_keys().add('ssh.example.com', 'ssh-rsa', key)
# client.connect('node3', username='jason', password='JYFZ290128!')
# stdin, stdout, stderr = client.exec_command('ls')
# for line in stdout:
#     print('... ' + line.strip('\n'))
# client.close()