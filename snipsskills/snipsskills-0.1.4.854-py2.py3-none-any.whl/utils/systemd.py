# -*-: coding utf-8 -*-
""" Systemd utilities. """

import getpass
import os
import subprocess

from .os_helpers import execute_command

SERVICE_NAME = "snipsskills"


class Systemd:
    """ Systemd utilities. """

    @staticmethod
    def setup():
        (username, snips_home_path, snipsskills_path) = Systemd.get_params()
        Systemd.write_file(username, snips_home_path, snipsskills_path)
        Systemd.enable_service(username)

    @staticmethod
    def get_params():
        run_on_boot = raw_input(
            "Would you like Snips to start on boot (using systemd)? [Y/n] ")
        if run_on_boot is not None and run_on_boot.strip() != "" and run_on_boot.lower() != "y":
            return

        current_username = getpass.getuser()
        username = raw_input(
            "Run as user [default: {}]: ".format(current_username))
        if username is None or username.strip() == "":
            username = current_username

        current_dir = os.getcwd()
        snips_home_path = raw_input(
            "Snips project home [default: {}]: ".format(current_dir))
        if snips_home_path is None or snips_home_path.strip() == "":
            snips_home_path = current_dir

        try:
            snipsskills_path = subprocess.check_output(
                ['which', 'snipsskills']).strip()
        except subprocess.CalledProcessError:
            snipsskills_path = None

        if snipsskills_path is None or len(snipsskills_path.strip()) == 0:
            snipsskills_path = raw_input("Path to the snipsskills binary: ")

        return (username, snips_home_path, snipsskills_path)

    @staticmethod
    def write_file(username, snips_home_path, snipsskills_path):
        this_dir, this_filename = os.path.split(__file__)
        template_filename = os.path.join(
            this_dir, "../config/systemd/snipsskills@USER.service")
        with open(template_filename, 'r') as template_file:
            contents = template_file.read() \
                .replace("{{SNIPS_HOME_PATH}}", snips_home_path) \
                .replace("{{SNIPSSKILLS_PATH}}", snipsskills_path)
            output_filename = "/etc/systemd/system/{}@{}.service".format(
                SERVICE_NAME, username)
            os.system("sudo touch {}".format(output_filename))
            os.system("sudo echo \"{}\" > {}".format(
                contents, output_filename))
            os.system("sudo chmod a+rwx {}".format(output_filename))

    @staticmethod
    def enable_service(username):
        os.system("sudo systemctl --system daemon-reload")
        os.system("sudo systemctl enable {}@{}".format(
            SERVICE_NAME, username))
        os.system("sudo systemctl start {}@{}".format(
            SERVICE_NAME, username))
