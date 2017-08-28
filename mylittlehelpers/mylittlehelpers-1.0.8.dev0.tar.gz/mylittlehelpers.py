from __future__ import print_function, unicode_literals
__all__ = ('encrypt', 'decrypt')

import getpass
import json
import os
import time
import smtplib
from math import trunc

import sys

import argparse
import os
import struct
import sys

from os.path import exists, splitext

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from pbkdf2 import PBKDF2


SALT_MARKER = b'$'
ITERATIONS = 1000


class ImproperlyConfigured(BaseException):
    pass


def __except__(exception, replacement_function):
    def _try_wrap(function):
        def __try_wrap(*__args, **__kwargs):
            try:
                return function(*__args, **__kwargs)
            except exception as e:
                return replacement_function(*__args, **__kwargs)
        return __try_wrap
    return _try_wrap


class InterfaceSettings:

    SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
    CONF_NAME = "conf.conf"

    def __init__(self, settings_dir, conf_name):
        InterfaceSettings.SETTINGS_DIR = settings_dir
        InterfaceSettings.CONF_NAME = conf_name

    @staticmethod
    def gather_secrets_location(create, designate):
        if create:
            secrets_location = input("1 selected. Please specify the full path containing your secrets file: "
                                          "(/path/containing/secrets/)")\
                                .replace("\n", "").replace("\\", "/").replace("//", "/")
            try:
                file = open(os.path.join(secrets_location, 'secrets.json'), 'w')
                file.close()

            except FileNotFoundError:
                print("Could not create secrets at that location. Please check your input and try again.\n\n")
                return InterfaceSettings.gather_secrets_location(create, designate)

        elif designate:
            secrets_location = input("2 selected. Please specify the name of your secrets file "
                                          "(/path/to/secrets.json): ").replace("\n", "")
            try:
                file = open(os.path.join(secrets_location), 'r')
                file.close()

            except FileNotFoundError:
                print("Could not find secrets at that location. Please check your input and try again.\n\n")
                return InterfaceSettings.gather_secrets_location(create, designate)
        else:
            raise Exception("1 or 2 expected as input.")

        return secrets_location

    @staticmethod
    def set_secrets():
        create, designate = False, False
        create_or_designate = str(input('Would you like to: \n'
                       '\t1: Create a new file named secrets.json and store it in a specified path?\n'
                       '\t2: Specify the full path of an existing secrets file?\n'))
        if '1' in create_or_designate:
            create = True
        elif '2' in create_or_designate:
            designate = True
        else:
            print('Please specify option 1 or 2 by typing 1 or 2.')
            return

        SECRETS_LOCATION = InterfaceSettings.gather_secrets_location(create, designate)

        if create:
            with open(os.path.join(InterfaceSettings.SETTINGS_DIR, InterfaceSettings.CONF_NAME)) as conf:
                USE_FLAT_FILES = json.load(conf)['USE_FLAT_FILES']
            SECRETS_LOCATION = os.path.join(SECRETS_LOCATION, 'secrets.json')
            secrets = {
                "CLIENT_ID": input("Please input your Client ID for API development: "),
                "CLIENT_SECRET": getpass.getpass("Client Secret: "),
                "EMAIL_ADDRESS": input("Default gmail address for API Interface used in helpers.send_mail(): "),
                "EMAIL_PASSWORD": getpass.getpass("Default gmail password for API Interface used in helpers.send_mail(): "),
                "DB_USER": input("PostgreSQL database login role username. (Database used to store access and API tokens): "),
                "DB_PASSWORD": getpass.getpass("PostgreSQL database login role password. (Database used to store access and API tokens): "),
            }
            with open(os.path.join(InterfaceSettings.SETTINGS_DIR, InterfaceSettings.CONF_NAME), 'w') as new_conf:
                new_conf_dict = {"USE_FLAT_FILES": USE_FLAT_FILES, "SECRETS_LOCATION": SECRETS_LOCATION}
                new_conf.write(json.dumps(new_conf_dict, indent=4))
            with open(os.path.join(SECRETS_LOCATION), 'w') as new_secrets:
                new_secrets.write(json.dumps(secrets, indent=4))

        elif designate:
            with open(os.path.join(InterfaceSettings.SETTINGS_DIR, InterfaceSettings.CONF_NAME)) as conf:
                USE_FLAT_FILES = json.load(conf)['USE_FLAT_FILES']
            with open(os.path.join(InterfaceSettings.SETTINGS_DIR, InterfaceSettings.CONF_NAME), 'w') as new_conf:
                new_conf_dict = {"USE_FLAT_FILES": USE_FLAT_FILES, "SECRETS_LOCATION": SECRETS_LOCATION}
                new_conf.write(json.dumps(new_conf_dict, indent=4))

    @staticmethod
    def set_conf():
        use_flat_or_not = input("Would you like to use an SQLite or PostgreSQL database for token storage? \n"
                                "\t1: PostgreSQL Database\n"
                                "\t2: SQLite Database (Default)\n\n"
                                "Note: PostgreSQL is really only necessary for high concurrency; SQLite will suffice in "
                                "most use cases.\n")

        if '1' in use_flat_or_not:
            flat = False
        else:
            flat = True

        print(f'{2 if flat else 1} selected.')

        try:
            with open(os.path.join(InterfaceSettings.SETTINGS_DIR, InterfaceSettings.CONF_NAME)) as conf:
                SECRETS_LOCATION = json.load(conf).get('SECRETS_LOCATION')

        except FileNotFoundError:
            SECRETS_LOCATION = "secrets.json"

        with open(os.path.join(InterfaceSettings.SETTINGS_DIR, InterfaceSettings.CONF_NAME), 'w') as new_conf:
            new_conf_dict = {"USE_FLAT_FILES": flat, "SECRETS_LOCATION": SECRETS_LOCATION}
            new_conf.write(json.dumps(new_conf_dict, indent=4))

    @staticmethod
    def create_conf():
        InterfaceSettings.set_conf()
        return InterfaceSettings.load_conf()

    @staticmethod
    def create_secrets():
        InterfaceSettings.set_secrets()
        return InterfaceSettings.load_secrets()

    @staticmethod
    @__except__(FileNotFoundError, lambda: InterfaceSettings.create_conf())
    def load_conf():
        try:
            with open(os.path.join('interface.conf'), 'r') as conf:
                conf = json.load(conf)
        except FileNotFoundError:
            with open(os.path.join(InterfaceSettings.SETTINGS_DIR, InterfaceSettings.CONF_NAME)) as conf:
                conf = json.load(conf)
        return conf

    @staticmethod
    @__except__(FileNotFoundError, lambda: InterfaceSettings.create_secrets())
    def load_secrets():
        conf = InterfaceSettings.load_conf()
        with open(conf['SECRETS_LOCATION']) as secrets:
            secrets = json.load(secrets)

        try:
            USE_FLAT_FILES = conf["USE_FLAT_FILES"]
            CLIENT_ID = secrets["CLIENT_ID"]
            CLIENT_SECRET = secrets["CLIENT_SECRET"]
            EMAIL_ADDRESS = secrets["EMAIL_ADDRESS"]
            EMAIL_PASSWORD = secrets["EMAIL_PASSWORD"]
            DB_USER = secrets["DB_USER"]
            DB_PASSWORD = secrets["DB_PASSWORD"]
        except KeyError as e:
            if "USE_FLAT_FILES" in e.args[0]:
                raise ImproperlyConfigured(f'{e.args[0]} not found in {InterfaceSettings.CONF_NAME}')
            else:
                raise ImproperlyConfigured(f'{e.args[0]} not found in {conf["SECRETS_LOCATION"]}')
        return secrets


def send_gmail(recipient, subject, body, user=None, pwd=None):
    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print('Email Sent.')
    except:
        print("failed to send mail")


def time_check(start):
    current_time = time.time()
    auto_refresh = False
    hours, rem = divmod(current_time - start, 3600)
    minutes, seconds = divmod(rem, 60)
    if minutes > 7:
        start = time.time()
        auto_refresh = True

    return start, auto_refresh


def time_elapsed(start):
    current_time = time.time()
    hours, rem = divmod(current_time - start, 3600)
    minutes, seconds = divmod(rem, 60)
    time_string = f'{trunc(hours):02d}:{trunc(minutes):02d}:{trunc(seconds):02d}'
    return f'{time_string:>12}'


def time_bomb(countdown, package=(print, ("BOOM",)), action="", dots=3):
    action = action if action else package[0].__name__
    sys.stdout.write(f"{action} in {countdown}")
    sys.stdout.flush()
    for i in range(countdown - 1, -1, -1):
        for j in range(dots):
            time.sleep(1.0/(dots + 1))
            sys.stdout.write(".")
            sys.stdout.flush()
        time.sleep(.25)
        sys.stdout.write(f"{i}")
        sys.stdout.flush()
    print("")
    package[0](*package[1])


SALT_MARKER = b'$'
ITERATIONS = 1000


def encrypt(infile, outfile, password, key_size=32, salt_marker=SALT_MARKER,
        kdf_iterations=ITERATIONS, hashmod=SHA256):
    """Encrypt infile and write it to outfile using password to generate key.

    The encryption algorithm used is symmetric AES in cipher-block chaining
    (CBC) mode.

    ``key_size`` may be 16, 24 or 32 (default).

    The key is derived via the PBKDF2 key derivation function (KDF) from the
    password and a random salt of 16 bytes (the AES block size) minus the
    length of the salt header (see below).

    The hash function used by PBKDF2 is SHA256 per default. You can pass a
    different hash function module via the ``hashmod`` argument. The module
    must adhere to the Python API for Cryptographic Hash Functions (PEP 247).

    PBKDF2 uses a number of iterations of the hash function to derive the key,
    which can be set via the ``kdf_iterations` keyword argumeent. The default
    number is 1000 and the maximum 65535.

    The header and the salt are written to the first block of the encrypted
    file. The header consist of the number of KDF iterations encoded as a
    big-endian word bytes wrapped by ``salt_marker`` on both sides. With the
    default value of ``salt_marker = b'$'``, the header size is thus 4 and the
    salt 12 bytes. The salt marker must be a byte string of 1-6 bytes length.

    The last block of the encrypted file is padded with up to 16 bytes, all
    having the value of the length of the padding.

    """
    if not 1 <= len(salt_marker) <= 6:
        raise ValueError('The salt_marker must be one to six bytes long.')
    elif not isinstance(salt_marker, bytes):
        raise TypeError('salt_marker must be a bytes instance.')

    if kdf_iterations >= 65536:
        raise ValueError('kdf_iterations must be <= 65535.')

    bs = AES.block_size
    header = salt_marker + struct.pack('>H', kdf_iterations) + salt_marker
    salt = os.urandom(bs - len(header))
    kdf = PBKDF2(password, salt, min(kdf_iterations, 65535), hashmod)
    key = kdf.read(key_size)
    iv = os.urandom(bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    outfile.write(header + salt)
    outfile.write(iv)
    finished = False

    while not finished:
        chunk = infile.read(1024 * bs)

        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = (bs - len(chunk) % bs) or bs
            chunk += (padding_length * chr(padding_length)).encode()
            finished = True

        outfile.write(cipher.encrypt(chunk))


def decrypt(infile, outfile, password, key_size=32, salt_marker=SALT_MARKER,
        hashmod=SHA256):
    """Decrypt infile and write it to outfile using password to derive key.

    See `encrypt` for documentation of the encryption algorithm and parameters.

    """
    mlen = len(salt_marker)
    hlen = mlen * 2 + 2

    if not 1 <= mlen <= 6:
        raise ValueError('The salt_marker must be one to six bytes long.')
    elif not isinstance(salt_marker, bytes):
        raise TypeError('salt_marker must be a bytes instance.')

    bs = AES.block_size
    salt = infile.read(bs)

    if salt[:mlen] == salt_marker and salt[mlen + 2:hlen] == salt_marker:
        kdf_iterations = struct.unpack('>H', salt[mlen:mlen + 2])[0]
        salt = salt[hlen:]
    else:
        kdf_iterations = ITERATIONS

    if kdf_iterations >= 65536:
        raise ValueError('kdf_iterations must be <= 65535.')

    iv = infile.read(bs)
    kdf = PBKDF2(password, salt, kdf_iterations, hashmod)
    key = kdf.read(key_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = b''
    finished = False

    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(infile.read(1024 * bs))

        if not next_chunk:
            padlen = chunk[-1]
            if isinstance(padlen, str):
                padlen = ord(padlen)
                padding = padlen * chr(padlen)
            else:
                padding = (padlen * chr(chunk[-1])).encode()

            if padlen < 1 or padlen > bs:
                raise ValueError("bad decrypt pad (%d)" % padlen)

            # all the pad-bytes must be the same
            if chunk[-padlen:] != padding:
                # this is similar to the bad decrypt:evp_enc.c
                # from openssl program
                raise ValueError("bad decrypt")

            chunk = chunk[:-padlen]
            finished = True

        outfile.write(chunk)


def main(args=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('-d', '--decrypt', action="store_true",
        help="Decrypt input file")
    ap.add_argument('-f', '--force', action="store_true",
        help="Overwrite output file if it exists")
    ap.add_argument('infile', help="Input file")
    ap.add_argument('outfile', nargs='?', help="Output file")

    args = ap.parse_args(args if args is not None else sys.argv[1:])

    if not args.outfile:
        if args.decrypt:
            args.outfile = splitext(args.infile)[0]
        else:
            args.outfile = args.infile + '.enc'

    if args.outfile == args.infile:
        print("Input and output file must not be the same.")
        return 1

    if exists(args.outfile) and not args.force:
        print("Output file '%s' exists. "
              "Use option -f to override." % args.outfile)
        return 1

    with open(args.infile, 'rb') as infile, \
            open(args.outfile, 'wb') as outfile:
        if args.decrypt:
            decrypt(infile, outfile, getpass.getpass("Enter decryption password: "))
        else:
            try:
                while True:
                    passwd = getpass.getpass("Enter encryption password: ")
                    passwd2 = getpass.getpass("Verify password: ")

                    if passwd != passwd2:
                        print("Password mismatch!")
                    else:
                        break
            except (EOFError, KeyboardInterrupt):
                return 1

            encrypt(infile, outfile, passwd)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
