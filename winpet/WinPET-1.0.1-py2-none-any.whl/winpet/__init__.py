# Copyright 2017 Alex Hadi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import click
import ctypes
import os
import pywintypes
import subprocess
import win32service
import _winreg


@click.command()
@click.option("-g", "-group", type=str, help="Display only a certain group's permissions.")
@click.option("-o", "-output", type=str, help="Set different output path for the file. Defaults to current directory.")
@click.option("-s", "-service", required=True, type=str, help="Specify Windows service to inspect.")
@click.option("-v", "-verbose", is_flag=True, help="Display results to terminal. Otherwise, written to txt file.")
def cli(group, output, service, verbose):
    """
    Author: Alex Hadi\n
    Created using Python 2.7.13 and Click.\n
    Windows Privilege Escalation Tester.
    Checks ImagePath in registry key, path permissions, and registry key permissions.
    """

    home_path = os.getcwd()
    # Used to open registry keys.
    service_path = "SYSTEM\\CurrentControlSet\\Services\\" + service

    if group is not None:
        # All groups are capitalized.
        group_name = group.upper()
    else:
        group_name = None

    if output is None:
        # Default path if user doesn't use -o.
        output_path = home_path + "\\" + service + "_report.txt"
    else:
        if not output.endswith(".txt"):
            output_path = None
            click.echo("The output path must end in .txt!")
            quit()
        else:
            output_path = output

    if verbose:
        verbose_output = True
    else:
        verbose_output = False

    # All called functions.
    check_admin()
    if verbose_output:
        # Placeholder so that program doesn't have errors.
        save_file = None
    else:
        check_existing_file(output_path)
        try:
            # Append mode.
            save_file = open(output_path, "a")
        except IOError:
            save_file = None
            click.echo("The save file could not be opened!")
            quit()
    reg_key = get_reg_key(service_path)
    image_path = get_image_path(reg_key)
    is_quoted = get_is_quoted(image_path, save_file, verbose_output)
    exe_path = get_exe_path(image_path)
    set_path(exe_path)
    check_path_permissions(group_name, is_quoted, save_file, verbose_output)
    check_reg_permissions(save_file, service_path, verbose_output)
    check_service_permissions(save_file, service, verbose_output)

    # Return to home path.
    os.chdir(home_path)
    if not verbose_output:
        save_file.close()

    click.echo("All operations were successfully completed.")


def check_admin():
    """Checks to see if script is being run as an admin."""
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    if is_admin:
        click.echo("The script is running as an administrator!")
    else:
        click.echo("The script is not running as an administrator.")


def check_existing_file(output_path):
    """
    Checks to see if existing file needs to be deleted.
    :param output_path: path to check to see if file already exists.
    :return: Return to same function if user provides invalid input.
    """

    if os.path.isfile(output_path):
        # Make input case insensitive.
        delete_file = raw_input("Would you like to delete the existing file? (Y/N)\n").upper()
        if delete_file == "Y":
            try:
                os.remove(output_path)
            except OSError:
                click.echo("The existing security file could not be deleted!")
                quit()
        elif delete_file == "N":
            click.echo("The program cannot save the output!")
            quit()
        else:
            check_existing_file(output_path)


def get_reg_key(service_path):
    """
    Retrieves the requested service key.
    :param service_path: Path to specified service.
    :return: Specified Windows registry key.
    """

    try:
        key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, service_path, 0, _winreg.KEY_READ)
        return key
    except WindowsError:
        click.echo("The service specified does not exist!")
        quit()


def get_image_path(key):
    """
    Gets image path.
    :param key: Windows registry key.
    :return: ImagePath registry value.
    """

    # While loop goes through tuples to find ImagePath value and record it.
    index = 0
    while True:
        try:
            temp_list = list(_winreg.EnumValue(key, index))
            if temp_list[0] == "ImagePath":
                image_path_key = temp_list
                break
            index += 1
        except WindowsError:
            click.echo("The image path cannot be found!")
            quit()

    # Second element of image_path_key contains the actual executable path.
    return image_path_key[1]


def get_is_quoted(image_path, save_file, verbose_output):
    """
    Determines whether the path is quoted or not. Records result.
    :param image_path: Value of ImagePath key.
    :param save_file: File to send to record_string.
    :param verbose_output: Boolean to send to record_string.
    :return: True (path is quoted) or false (path is not quoted).
    """

    if image_path.startswith('"') and image_path.endswith('"'):
        record_string("The image path is quoted.", save_file, verbose_output)
        return True
    else:
        record_string("The image path is not quoted.", save_file, verbose_output)
        return False


def get_exe_path(image_path):
    """
    Gets just the exe folder path by expanding the ImagePath and stripping quotes.
    :param image_path: ImagePath value.
    :return: Just path to folder containing the executable.
    """

    exe_path = image_path.strip('"')

    # Necessary for keys that have "%SystemRoot%, etc
    exe_path = os.path.expandvars(exe_path)

    if not exe_path.endswith(".exe"):
        # Attempt to just remove args from end (ex: <exe path> -k <args>)
        exe_path = exe_path.split(" ", 1)[0]
        # Examples of ImagePath values that would fail are .sys
        if not exe_path.endswith(".exe"):
            click.echo("The image path is invalid because it doesn't end in .exe!")
            quit()

    # Remove last part of path to just folder that contains executable.
    exe_path = os.path.split(exe_path)[0]
    return exe_path


def set_path(exe_path):
    """
    Directory changed to path containing executable so that it can be checked.
    :param exe_path: Folder that contains executable.
    """
    try:
        os.chdir(exe_path)
    except WindowsError:
        click.echo("The path to the executable does not exist!")
        quit()


def check_path_permissions(group_name, is_quoted, save_file, verbose_output):
    """
    Recursive function checks each directory.
    :param group_name: group to print permissions for (None = print all permissions).
    :param is_quoted: True (ImagePath key is quoted) or False (ImagePath is not quoted).
    :param save_file: File to send to record_string function.
    :param verbose_output: Boolean to send to record_string function.
    :return: Recursively calls function if applicable.
    """

    path = os.curdir

    # Runs icacls cmd command.
    run_command = None
    try:
        command = ['icacls', path]
        run_command = subprocess.Popen(command, stdout=subprocess.PIPE)
    except WindowsError:
        click.echo("The icacls command could not be executed!")
        quit()

    # Adds output line by line to list and closes command process.
    permissions_list = []
    for line in iter(run_command.stdout.readline, ""):
        permissions_list.append(line)
    run_command.stdout.close()

    # Clean up list: remove path from first item, strip, remove \n & \r, remove empty item, remove success/failure item.
    if permissions_list[0].startswith(path):
        permissions_list[0] = permissions_list[0][len(path):]
    permissions_list = [i.strip(' ') for i in permissions_list]
    permissions_list = [i.strip('\n') for i in permissions_list]
    permissions_list = [i.strip('\r') for i in permissions_list]
    permissions_list = [i for i in permissions_list if not ("Successfully processed" or "Failed processing") in i]
    permissions_list = [i for i in permissions_list if not i == ""]

    # Current path is recorded to give report info about which path was checked.
    record_string(os.getcwd(), save_file, verbose_output)
    for i in permissions_list:
        # If no group_name, print all permissions. Otherwise, print just that group's.
        if group_name is None:
            record_string(i, save_file, verbose_output)
        else:
            if group_name in i:
                record_string(i, save_file, verbose_output)
    record_string("\n", save_file, verbose_output)

    # Command only runs for current directory if path is quoted. Otherwise, all parent directories besides Win & Sys32.
    if is_quoted:
        return
    else:
        # Old path is saved to prevent endless recursion.
        old_path = os.getcwd()

        new_path = os.getcwd()
        while True:
            temp_path = new_path
            # First, directory is attempted to be changed to everything before last space.
            new_path = new_path.rsplit(' ', 1)[0]
            # Then, if this doesn't change the path, dir is attempted to be changed to everything before the last slash.
            if new_path == temp_path:
                new_path = new_path.rsplit('\\', 1)[0] + "\\"
            # If this path doesn't exist, this will be recorded and the loop will continue.
            if os.path.exists(new_path):
                break
            else:
                record_string("The directory {0} does not exist!".format(new_path), save_file, verbose_output)
                continue

        try:
            os.chdir(new_path)
        except WindowsError:
            click.echo("The directory could not be changed!")
            quit()

        # Don't check 'Windows' or 'System32' directories.
        if new_path.lower() == ("c:\\windows\\" or "c:\\windows\\system32\\"):
            record_string("The permissions for {0} were not recorded.".format(new_path), save_file, verbose_output)
            return
        # To prevent endless recursion (changed to same directory and checked, etc...)
        elif os.getcwd() != old_path:
            check_path_permissions(group_name, is_quoted, save_file, verbose_output)
        else:
            return


def check_reg_permissions(save_file, service_path, verbose_output):
    """
    Checks specified registry key's permissions.
    :param save_file: File to send to record_string function.
    :param service_path: Path to the service in the Windows registry.
    :param verbose_output: Boolean to send to record_string function.
    """

    bad_reg_permissions = {_winreg.KEY_ALL_ACCESS: "KEY_ALL_ACCESS", _winreg.KEY_WRITE: "KEY_WRITE",
                           _winreg.KEY_SET_VALUE: "KEY_SET_VALUE", _winreg.KEY_CREATE_SUB_KEY: "KEY_CREATE_SUB_KEY"}

    # Attempts to open the registry key with access controls in bad_reg_permissions.
    for index in bad_reg_permissions:
        # If error is thrown, no access using specified access control. Otherwise, have access.
        try:
            key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, service_path, 0, index)
            record_string("Can access {0} registry permissions.".format(bad_reg_permissions[index]),
                          save_file, verbose_output)
            _winreg.CloseKey(key)
        except WindowsError:
            record_string("Cannot access {0} registry permissions.".format(bad_reg_permissions[index]),
                          save_file, verbose_output)


def check_service_permissions(save_file, service, verbose_output):
    """
    Attempts to open service with permissions that grant too much access. Result is recorded.
    Note: pywintypes.error may resolve as an error. Ignore it.
    :param save_file: File to send to record_string function.
    :param service: Name of specified service.
    :param verbose_output: Boolean to send to record_string function.
    """

    # Outer try-except block attempts to connect to SCM Manager. Result is recorded.
    try:
        sc_handle = win32service.OpenSCManager(None, None, win32service.SERVICE_ALL_ACCESS)
        record_string("Can open Service Control Manager (SCM) with SERVICE_ALL_ACCESS permissions.",
                      save_file, verbose_output)
        # Inner try-except block attempts to open service. Result is recorded.
        try:
            win32service.OpenService(sc_handle, service, win32service.SERVICE_ALL_ACCESS)
            record_string("Can open service with SERVICE_ALL_ACCESS permissions.", save_file, verbose_output)
        except pywintypes.error:
            record_string("Cannot open service with SERVICE_ALL_ACCESS permissions.", save_file, verbose_output)
        win32service.CloseServiceHandle(sc_handle)
    except pywintypes.error:
        record_string("Cannot open Service Control Manager (SCM) with SERVICE_ALL_ACCESS permissions.",
                      save_file, verbose_output)


def record_string(string, save_file, verbose_output):
    """
    Records input string to either the console (verbose_output is True) or save_file (verbose_output is not true).
    :param string: String to be recorded.
    :param save_file: File to write string to (if applicable).
    :param verbose_output: True (print to console) or False (write to file).
    """

    if verbose_output:
        click.echo(string)
    else:
        save_file.write(string + "\n")
