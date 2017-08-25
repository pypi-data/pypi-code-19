import getpass
import json
import os
import time
import smtplib
from math import trunc

import sys


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


def print_duration(start):
    current_time = time.time()
    hours, rem = divmod(current_time - start, 3600)
    minutes, seconds = divmod(rem, 60)
    time_string = f'{trunc(hours):02d}:{trunc(minutes):02d}:{trunc(seconds):02d}'
    return f'{time_string:>12}'


def time_bomb(action, countdown, dots=3):
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