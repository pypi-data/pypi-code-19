import os

HOME_DIR = os.path.expanduser('~')

LOCAL_DIR = os.path.join(HOME_DIR, ".keyman")

DB_PATH = os.path.join(LOCAL_DIR, "data.keydb")
# CONFIG_PATH = os.path.join(LOCAL_DIR, "keyman.cfg")

KEY = b"Keyman4E5Ciphkey"  # 16-bytes password for AES cipher
# 16-bytes initialization vector for AES cipher
IV = b'\xebg\xfa\x95\xbb\x1d\x91\xae\xcc\xd0\xf8y\xb9\xadP\xdb'
