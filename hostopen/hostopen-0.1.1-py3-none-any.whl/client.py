from hostopen.arg_handler import parse_client
import json
import logging
import os
import socket
import sys

from hostopen import utils

def get_synced_folders():
    """ Reads the appropriate file to get the synced_folder
    information so filepaths can be converted.

    Will look for the file 'synced_folder' in '/.vagrant_info'.

    Vagrantfile setup example:
        config.vm.synced_folder \
            ".vagrant/machines/default/virtualbox", \
            "/.vagrant_info"

    Returns:
        [<tuple>]: Uses the format (guestpath, hostpath)
    """
    folder = '/.vagrant_info'
    data_file = os.path.join(folder, 'synced_folders')

    with open(data_file, 'r') as file:
        data = json.load(file)

    folders = []
    for key_a in data.keys():
        for key_b in data[key_a].keys():
            guestpath = data[key_a][key_b]['guestpath']
            hostpath = data[key_a][key_b]['hostpath']
            folders.append(
                (guestpath,hostpath)
            )

    return folders

def transmit_data(data, port):
    """
    Args:
        data <binary>: the data to send
        port <int>: the port to connect through

    Returns:
        <bool>: success flag
    """
    try:
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect(('localhost', port))
        clientsocket.send(data)
        clientsocket.close()
        return True
    except ConnectionRefusedError:
        pass

def convert_filepaths(filepaths, folders):
    """ Convert files from the VM filepath to the host filepath

    Args:
        filepaths[<str>]: files to send
        folders<(guestpath, hostpath)>: conversion 'table'

    Returns:
        [<str>]: converted files - to send
        [<str>]: invalid files - to print
    """
    def s_length(item):
        return len(item[0])

    # Reverse sort by length of guestpath (first arg)
    folders = sorted(folders, key=s_length, reverse = True)

    # Convert Files
    converted_files = []
    invalid_files = []
    for path in filepaths:
        path = os.path.abspath(path)

        success = False
        for guestpath, hostpath in folders:
            if guestpath in path:
                new_path = path.replace(guestpath, hostpath, 1)
                converted_files.append(new_path)
                success = True
                break
        if not success:
            invalid_files.append(path)

    converted_files = list(set(converted_files))
    invalid_files = list(set(invalid_files))
    return converted_files, invalid_files

def main():
    # Parse Args
    level, port, filepaths = parse_client(sys.argv[1:])

    # Setup Logger
    utils.init_logger(level)
    logger = logging.getLogger(__name__)

    logger.debug('Port: %d' % port)
    logger.debug('Files: %s' % ', '.join(filepaths))

    # Get files and convert
    folders = get_synced_folders()
    converted_files, invalid_files = convert_filepaths(filepaths, folders)

    # Send data
    if converted_files:
        data = utils.pack_data(converted_files)
        success = transmit_data(data, port)

        if success:
            if invalid_files:
                logging.info('Not sent (not synced):')
                for file in invalid_files:
                    logging.info('  %s' % file)
        else:
            logging.warning('Unable to connect.')
            logging.warning('Connect with the command:')
            logging.warning('  vagrant ssh -- -R <port>:localhost:<port>')
    else:
        logger.warning('No valid files selected.')


if __name__ == '__main__':
    main()
