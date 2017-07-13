import getpass
import json
import os
import re
import requests
import base58
import libnacl
import sys
import urllib.parse
import pickle


def get_known_zone_Id_mapping():
    return {
        "ACT": "Australia/Darwin",
        "AET": "Australia/Sydney",
        "AGT": "America/Argentina/Buenos_Aires",
        "ART": "Africa/Cairo",
        "AST": "America/Anchorage",
        "BET": "America/Sao_Paulo",
        "BST": "Asia/Dhaka",
        "CAT": "Africa/Harare",
        "CNT": "America/St_Johns",
        "CST": "America/Chicago",
        "CTT": "Asia/Shanghai",
        "EAT": "Africa/Addis_Ababa",
        "ECT": "Europe/Paris",
        "IET": "America/Indiana/Indianapolis",
        "IST": "Asia/Kolkata",
        "JST": "Asia/Tokyo",
        "MIT": "Pacific/Apia",
        "NET": "Asia/Yerevan",
        "NST": "Pacific/Auckland",
        "PLT": "Asia/Karachi",
        "PNT": "America/Phoenix",
        "PRT": "America/Puerto_Rico",
        "PST": "America/Los_Angeles",
        "SST": "Pacific/Guadalcanal",
        "VST": "Asia/Ho_Chi_Minh",
        "EST": "-05:00",
        "MST": "-07:00",
        "HST": "-10:00"
    }


class Common:

    def __init__(self):
        # init env url from args
        if len(sys.argv) == 1:
            script_name = os.path.basename(os.path.normpath(sys.argv[0]))
            print("\n\nUsage            : <script name> <agency-api-base-url>")
            print("For Demo env     : {} https://agency.evernym.com".format(script_name))
            print("For Sandbox env  : {} https://agency-sandbox.evernym.com".format(script_name))
            print("\n")
            exit(1)

        self.did = ""
        self.seed = ""

        self.envUrlPrefix = sys.argv[1]

        # create base dir
        agent_reporter_dir = ".agent-admin"
        base_dir_path = os.path.join(os.path.expanduser("~"),
                                     agent_reporter_dir)
        if not os.path.exists(base_dir_path):
            os.mkdir(base_dir_path)

        # init config file path
        self.config_file_path = os.path.join(base_dir_path, "config.py")

        # load config
        self.config =  {}
        self.load_saved_config()

    def load_saved_config(self):
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, 'rb') as handle:
                self.config = pickle.loads(handle.read())

    def store_config(self, k, v):
        self.config[k.lower()] = v
        with open(self.config_file_path, 'wb') as handle:
            pickle.dump(self.config, handle)

    def get_config(self, k):
        return self.config.get(k.lower())

    @staticmethod
    def take_input(prompt_text, required=False, default="", onlyAlphabets=False, minLength=0, maxLength=0):
        while True:
            inp = input(prompt_text)

            if onlyAlphabets and not inp.isalpha():
                print("    ERROR: only alphabets are expected")
                continue

            if required and inp == "":
                print \
                    ("    ERROR: it is required field, please provide appropriate data")
                continue

            if inp == "" and default != "":
                return default
            else:
                return inp

    @staticmethod
    def sign(message, seed):

        if len(seed) != libnacl.crypto_sign_SEEDBYTES:
            raise ValueError(
                "The seed must be exactly %d bytes long" %
                libnacl.crypto_sign_SEEDBYTES
            )

        seed_str = seed.encode('utf-8')
        seed_bytes = bytes(seed_str)
        _, signing_key = libnacl.crypto_sign_seed_keypair(seed_bytes)

        ser_msg = message.encode('utf-8')
        raw_signed = libnacl.crypto_sign(ser_msg, signing_key)
        bsig = raw_signed[:libnacl.crypto_sign_BYTES]
        return base58.b58encode(bsig)

    def start(self):
        print("\n\nNotes")
        print("  1. Press Enter for default values.")

    def get_zone_id(self):
        try:
            allowedTimeZoneIds = sorted(get_known_zone_Id_mapping().keys())
            print("\n\nAllowed time zone ids:\n     Fixed : {}\n     Offset: +02:30, -04:20, anything like that\n\n".format(", ".join(allowedTimeZoneIds)))
            last_config_tz = self.get_config("last_tz")
            if not last_config_tz:
                last_config_tz = "UTC"
            default_tz = ", default={}".format(last_config_tz)

            while True:
                last_tz = self.take_input("Enter your time zone [either Fixed or Offset style] (required=Y{}): ".format(default_tz), False)
                if last_tz == "":
                    last_tz = last_config_tz

                if not last_tz.startswith("+") and not last_tz.startswith("-") and last_tz != "UTC" and last_tz not in allowedTimeZoneIds:
                    print("    ERROR: invalid time zone id, please see above valid time zone ids and enter appropriate data")
                    continue
                self.store_config("last_tz", last_tz)
                break

        except Exception as e:
            print("\nError occurred: {}\n".format(repr(e)))

        except KeyboardInterrupt:
            print("\n\nExited\n")
            exit(1)

    def get_signing_info(self):
        signing_info = ""
        seed = ""
        did = ""
        print("\nProvide signing information...")
        while True:
            did = self.take_input(
                "  DID or Locally stored alias (required=Y): ", True)
            signing_info = self.get_config(did)
            did_length = len(did)
            if not signing_info and (did_length < 22 or did_length > 23):
                print(
                    "    ERROR: alias not found OR identifier length should be between 22 to 23 characters, please provide appropriate data")
                continue
            else:
                break

        if not signing_info:
            while True:
                seed = getpass.getpass(
                    "  Enter signing key seed here (required=Y, hidden=True)]: ")
                if seed == "":
                    print(
                        "    ERROR: it is required field, please provide appropriate data")
                    continue
                elif len(seed) != 32:
                    print(
                        "    ERROR: seed needs to be exact 32 character long, please provide appropriate data")
                    continue
                else:
                    break

            store = self.take_input(
                "\n\nDo you want to store signing information so that next time you have to only provide alias (optional=Y, default=N) [Y/N]: ",
                False, "N")

            if self.is_yes(store):
                while True:
                    alias = self.take_input(
                        "  Give an alias name (only alphabets): ",
                        True, "", True)
                    signing_info = self.get_config(alias)
                    if not signing_info:
                        self.store_config(alias, did + "," + seed)
                        break
                    else:
                        print(
                            "    ERROR: alias is already used")
                        update_it = self.take_input("Do you want to update it (default=N) [Y/N]: ", True, "N")
                        if self.is_yes(update_it):
                            self.store_config(alias, did + "," + seed)
                            break
                        else:
                            continue
            else:
                print("Ok, we'll not store signing information")
        else:
            did, seed = signing_info.split(",")
            print(
                "  signing information is fetched from config file=> did: {}".format(
                    did))
        self.did = did
        self.seed = seed

    @staticmethod
    def is_yes(ans):
        return ans.lower() == "y"

    def execute_request(self, input_dict, url_path_with_query_str, interactive, req_type):
        try:
            challenge = json.dumps(input_dict)
            sig = self.sign(challenge, self.seed)
            ready = "Y"

            if self.is_yes(interactive):
                print("\nVerify data:")
                print("  challenge: " + challenge)
                print("  signature: " + sig)

                ready = self.take_input(
                    "\nAre you ready to send the request (default=Y) [Target = {}] [Y/N] : ".format(
                        self.envUrlPrefix), False, "Y")

            if self.is_yes(ready):
                mapper = {
                    "did": self.did,
                    "challenge": urllib.parse.quote(challenge.encode('utf-8')),
                    "signature": sig
                }
                final_url = self.envUrlPrefix + "/" + url_path_with_query_str.format(**mapper)
                r = ""
                if req_type == "GET":
                    r = requests.get(final_url)
                else:
                    post_data = {
                        "challenge": challenge,
                        "signature": sig
                    }
                    if req_type == "POST":
                        r = requests.post(final_url, json=post_data)
                    elif req_type == "PUT":
                        r = requests.put(final_url, json=post_data)
                return r
        except Exception as e:
            print("\nError occurred: {}\n".format(repr(e)))

        except KeyboardInterrupt:
            print("\n\nExited\n")

    def process_response(self, r, is_download):
        try:
            print("\n=======================================================\n")
            print(r.content.decode())
            print("\n=======================================================\n")

            if self.is_yes(is_download):
                fn = r.headers['Content-Disposition']
                fname = re.findall("filename=(.+)", fn)[0]
                with open(fname, 'wb') as f:
                    f.write(r.content)
                print(
                    "\nFile downloaded, check current directory for this file: {}\n".format(
                        fname))
        except Exception as e:
            print("\nError occurred: {}\n".format(repr(e)))

        except KeyboardInterrupt:
            print("\n\nExited\n")
