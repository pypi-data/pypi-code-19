# -*-: coding utf-8 -*-
""" Systemd utilities. """

import getpass
import os
import subprocess

from .os_helpers import execute_sudo_command

SERVICE_NAME = "snipsskills"

class Systemd:
    """ Systemd utilities. """

    @staticmethod
    def setup():
        run_on_boot = raw_input("Would you like Snips to start on boot (using systemd)? [Y/n] ")
        if run_on_boot is not None and run_on_boot.strip() != "" and run_on_boot.lower() != "y":
            return

        current_username = getpass.getuser()
        username = raw_input("Run as user [default: {}]: ".format(current_username))
        if username is None or username.strip() == "":
            username = current_username

        current_dir = os.getcwd()
        snips_home_path = raw_input("Snips project home [default: {}]: ".format(current_dir))
        if snips_home_path is None or snips_home_path.strip() == "":
            snips_home_path = current_dir

        try:
            snipsskills_path = subprocess.check_output(['which', 'snipsskills']).strip()
        except subprocess.CalledProcessError:
            snipsskills_path = None

        if snipsskills_path is None or len(snipsskills_path.strip()) == 0:
            snipsskills_path = raw_input("Path to the snipsskills binary: ")

        Systemd.write_file(username, snips_home_path, snipsskills_path)
        # Systemd.enable_service(username)

    @staticmethod
    def write_file(username, snips_home_path, snipsskills_path):
        this_dir, this_filename = os.path.split(__file__)
        systemd_snipsskills_path = os.path.join(this_dir, "../config/systemd/snipsskills@USER.service")

        with open(systemd_snipsskills_path, 'r') as systemd_snipsskills:
            contents = systemd_snipsskills.read()
            contents = contents.replace("{{SNIPS_HOME_PATH}}", snips_home_path)
            contents = contents.replace("{{SNIPSSKILLS_PATH}}", snipsskills_path)
            local_output_filename = "{}/{}@{}.service".format(snips_home_path, SERVICE_NAME, username)
            with open(local_output_filename, "w") as output_file:
                output_file.write(contents)
                system_output_filename = "/etc/systemd/system/{}@{}.service".format(SERVICE_NAME, username)
                # copy_command = "sudo cat \"\" {}".format(local_output_filename, system_output_filename)
                copy_command = "sudo echo \"{}\" > {}".format(contents, system_output_filename)
                # copy_command = "sudo cp {} {}".format(local_output_filename, system_output_filename)
                print(copy_command)
                os.system(copy_command)
                chmod_command = "sudo chmod a+rwx {}".format(system_output_filename)
                print(chmod_command)
                os.system(chmod_command)
            # try:
            #     os.remove(local_output_filename)
            # except OSError:
            #     pass

    @staticmethod
    def enable_service(username):
        execute_sudo_command("sudo systemctl --system daemon-reload")
        execute_sudo_command("sudo systemctl enable {}@{}".format(SERVICE_NAME, username))
        execute_sudo_command("sudo systemctl start {}@{}".format(SERVICE_NAME, username))
