#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""
import argparse
import ast
import datetime
import collections
import gzip
import os
import json

import requests
import signal
import subprocess
import traceback
import usb
import usbtmc
from math import log10

from requests_toolbelt.multipart.encoder import MultipartEncoder
from raven import Client
import ivi
try:
    from urllib.parse import urljoin
except:
    from urlparse import urljoin

import re
import logging
from configparser import RawConfigParser
import schema_forms

cfg = RawConfigParser()
cfg.optionxform = str
try:
    cfg.read('/etc/gradient_one.cfg')
    COMMON_SETTINGS = cfg['common']
    CLIENT_SETTINGS = cfg['client']
except KeyError:
    raise ValueError("Please create a config file in /etc/gradient_one.cfg")
DIRPATH = os.path.dirname(os.path.realpath(__file__))
PID_JSON_FILE = os.path.join(DIRPATH, 'pids.json')

if COMMON_SETTINGS['DOMAIN'].find("localhost") == 0 or COMMON_SETTINGS['DOMAIN'].find("127.0.0.1") == 0:  # noqa
    BASE_URL = "http://"+COMMON_SETTINGS['DOMAIN']
else:
    BASE_URL = "https://" + COMMON_SETTINGS['DOMAIN']


def print_debug(debug_statement, post=False, trace=False):
    if cfg.getboolean('client', 'DEBUG_ON'):
        print(debug_statement)
    if post:
        post_log(debug_statement)
    if trace:
        print(traceback.format_exc())
    if trace and post:
        post_log(traceback.format_exc())


def rotate_logfiles(original_file):
    for i in range(int(CLIENT_SETTINGS['MAX_NUM_LOGFILES'])):
        file_num = i + 1
        nextlogfile = original_file + "." + str(file_num)
        if not os.path.isfile(nextlogfile):
            break
        if os.stat(nextlogfile).st_size < int(ELIGIBLE_LOGFILE_SIZE):  # nopep8
            # purge the oldest file so that it's ready next rotate
            if file_num < int(CLIENT_SETTINGS['MAX_NUM_LOGFILES']):
                file_num += 1
                purge_logfile(original_file + "." + str(file_num))
            # break to return nextlogfile
            break
        # if all allowed files are full, purge and original
        if file_num == int(CLIENT_SETTINGS['MAX_NUM_LOGFILES']):
            purge_logfile(original_file)
            nextlogfile = original_file
    return nextlogfile


def purge_logfile(file):
    if not os.path.isfile(file):
        return
    try:
        os.remove(file)
    except Exception:
        print_debug("Remove logfile exception")

try:
    DEFAULT_LOGFILE = CLIENT_SETTINGS['DEFAULT_LOGFILE']
except KeyError:
    DEFAULT_LOGFILE = "info.log"

try:
    ELIGIBLE_LOGFILE_SIZE = CLIENT_SETTINGS["ELIGIBLE_LOGFILE_SIZE"]
except KeyError:
    ELIGIBLE_LOGFILE_SIZE = 2000000


parser = argparse.ArgumentParser(description='Update to given version')
parser.add_argument('-v', '--verbosity', type=str, default="info",
                    help='Verbosity for logs to console')
parser.add_argument('-l', '--logfile', type=str, help='logfile',
                    default=DEFAULT_LOGFILE)
parser.add_argument('-c', '--client', type=str,
                    help='Specific client to run', default="all")
ARGS = parser.parse_args()


def get_logger(file_lvl=logging.DEBUG,
               log_filename='info.log',
               console_lvl=logging.INFO,
               verbose=False,):
    """Returns the logger for client logs

    If verbose is True, the console will print debug level
    """
    logger = logging.getLogger(__name__)

    # check if the logger already exists (avoids duplicate logs)
    if len(logger.handlers) > 0:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # DIRPATH = os.path.dirname(os.path.realpath(__file__))
    # LOGDIR = os.path.join(DIRPATH, 'logs')
    try:
        LOGDIR = CLIENT_SETTINGS["LOGDIR"]
    except:
        LOGDIR = '/var/log/gradientone'
    if not os.path.exists(LOGDIR):
        os.makedirs(LOGDIR)

    # check for command line arg filename
    arg_file = ARGS.logfile
    if arg_file:
        log_filename = arg_file
    if not log_filename:
        log_filename = 'info.log'
    logger_file = os.path.join(LOGDIR, log_filename)

    # check if file exists
    if not os.path.isfile(logger_file):
        with open(logger_file, 'w') as f:
            f.write("init\n")

    # check logfile size and rotate if needed
    if os.stat(logger_file).st_size > int(ELIGIBLE_LOGFILE_SIZE):  # nopep8
        logger_file = rotate_logfiles(logger_file)

    # create file handler
    console_handler = logging.StreamHandler()  # by default, sys.stderr
    file_handler = logging.FileHandler(logger_file)

    # check for command line verbosity level arg
    arg_lvl = ARGS.verbosity
    if not arg_lvl:
        pass
    elif arg_lvl == 'info':
        console_lvl = logging.INFO
    elif arg_lvl == 'debug':
        console_lvl = logging.DEBUG
    elif arg_lvl == 'warning':
        console_lvl = logging.WARNING
    elif arg_lvl == 'error':
        console_lvl = logging.ERROR
    else:
        print "Ignoring command line arg: %s" % arg_lvl
        print "Using function arg: %s" % console_lvl

    # set logging levels
    console_handler.setLevel(console_lvl)
    file_handler.setLevel(file_lvl)

    # create logging format
    formatter = logging.Formatter(
        '%(asctime)s :: [ %(levelname)s ] %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Note verbose flag will set the console_lvl to the debug
    if verbose:
        console_handler.setLevel(logging.DEBUG)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = get_logger()


def get_headers(refresh=False, content_type='application/json'):
    headers = {'Content-Type': content_type,
               'Gateway-Auth-Token': CLIENT_SETTINGS['GATEWAY_AUTH_TOKEN'],
               'Company-Name': COMMON_SETTINGS['COMPANYNAME']}
    tokenfile = os.path.join(DIRPATH, '__token__')
    if os.path.isfile(tokenfile):
        with open(tokenfile, 'r') as f:
            headers['Auth-Token'] = str(f.read().strip())
    else:
        headers['Auth-Token'] = CLIENT_SETTINGS['GATEWAY_AUTH_TOKEN']
        with open(tokenfile, 'w') as f:
            f.write(headers['Auth-Token'])
    url = BASE_URL + '/profile/auth_token/refresh'
    if refresh:
        try:
            headers['Refresh-Token'] = CLIENT_SETTINGS['REFRESH_TOKEN']
            response = requests.get(url, headers=headers)
            assert response.status_code == 200
            data = json.loads(response.text)
            headers['Auth-Token'] = data['new auth token']
            with open(tokenfile, 'w') as f:
                f.write(headers['Auth-Token'])
        except Exception:
            logger.warning("Unable to get refresh token", exc_info=True)
    return headers


def authorize_and_post(session, url, data):
    headers = get_headers()
    response = session.post(url, headers=headers, data=data)
    if response.status_code == 401:
        headers = get_headers(refresh=True)
        response = session.post(url, headers=headers, data=data)
    return response


class SimulatedInstrument(ivi.tektronix.tektronixBaseScope.tektronixBaseScope):
    def __init__(self, *args, **kwargs):
        self.name = 'simulated'
        self._add_method('measurement.initiate',
                         self._measurement_initiate)
        self._add_method('measurement.fetch_waveform',
                         self._measurement_fetch_waveform)
        self._add_method('measurement.fetch_waveform_measurements',
                         self._measurement_fetch_waveform_measurements)
        self._add_property('identity.instrument_serial_number',
                           self._get_instrument_serial)
        self._add_property('identity.instrument_firmware_revision',
                           self._get_simulated_firmware_revision)
        self._add_method('channels[].measurement.fetch_waveform',
                         self._measurement_fetch_waveform)
        self._add_method('channels[].measurement.fetch_waveform_measurements',
                         self._measurement_fetch_waveform_measurements)
        self._add_property('channels[].probe_id',
                           self._get_channel_probe_id)
        self._add_property('channels[].enabled',
                           self._get_simulated_enabled)
        self._channel_count = 2
        self._analog_channel_count = 1
        self._digital_channel_count = 1
        self._init_channels()

    def close(self):
        pass

    def _get_channel_probe_id(self):
        return 'simulated_probe_id'

    def _get_simulated_firmware_revision(self):
        return 'simulated_firmware_version'

    def _get_instrument_serial(self):
        return 'simulated_serial_number'

    def _get_simulated_enabled(self, index=0):
        return True

    def _measurement_initiate(self):
        pass

    def _measurement_fetch_waveform(self, index):
        waveform = CLIENT_SETTINGS['SAMPLE_WAVEFORM']
        return waveform

    def _measurement_fetch_waveform_measurements(self, index):
        return None


def dt2ms(dtime):
    """Converts date time to miliseconds
    >>> from u2000_client import dt2ms
    >>> import datetime
    >>> dtime = datetime.datetime(2015, 12, 8, 18, 11, 44, 320012)
    >>> dt2ms(dtime)
    1449627104320
    """
    delta = dtime - datetime.datetime(1970, 1, 1)
    return int(delta.total_seconds()) * 1000 + int(delta.microseconds / 1000)


def log_wrap(execution, address):
    try:
        # return ivi.tektronix.tektronixMDO4104("TCPIP::192.168.1.108::INSTR")
        return execution(str(address))
    except Exception as e:
        logger.critical(
            "instrument exception: " + str(e) + "|" + address + "|" + str(
                execution) + "|", exc_info=False)
        return None


def getAgilentU2000(addr=None):
    if addr is None:
        addr = CLIENT_SETTINGS['AGILENT_U2000_ADDRESS']
    return log_wrap(ivi.agilent.agilentU2001A, addr)


def getTektronixMDO4104(addr=None):
    if addr is None:
        addr = CLIENT_SETTINGS['TEK_MDO4104_ADDRESS']
    return log_wrap(ivi.tektronix.tektronixMDO4104, addr)


def getTektronixMDO3012(addr=None):
    if addr is None:
        addr = CLIENT_SETTINGS['TEK_MDO3012_ADDRESS']
    return log_wrap(ivi.tektronix.tektronixMDO3012, addr)


def getTektronixMSO2024(addr=None):
    if addr is None:
        addr = CLIENT_SETTINGS['TEK_MSO2024_ADDRESS']
    return log_wrap(ivi.tektronix.tektronixMSO2024, addr)


def getTektronixMSO5204B(addr=None):
    if addr is None:
        addr = CLIENT_SETTINGS['TEK_MSO5204B_ADDRESS']
    return log_wrap(ivi.tektronix.tektronixMSO5204B, addr)

# def getKeysightDSOS804A(addr=nuc_settings.KeysightDSOS804A_ADDR):
#     return log_wrap(ivi.agilent.agilentDSOS804A, addr)


def getRigolMSO2302A(addr=None):
    if addr is None:
        addr = CLIENT_SETTINGS['RIGOL_MSO2302A_ADDRESS']
    return log_wrap(ivi.rigol.rigolMSO2302A, addr)


def getGenericScope(addr=None):
    if addr is None:
        addr = CLIENT_SETTINGS['GENERIC_SCOPE_ADDRESS']
    return log_wrap(ivi.tektronix.tektronixMSO5204B,
                    addr)  # DPO7354C for the default scope


def get_instrument(command_info):
    info_dict = collections.defaultdict(str, command_info)
    logger.info("Getting instrument")
    ivi_instruments = {
        'AgilentU2000': getAgilentU2000,
        'TektronixMDO4104': getTektronixMDO4104,
        'TektronixMDO3012': getTektronixMDO3012,
        'TektronixMSO2024': getTektronixMSO2024,
        'TektronixMSO5204B': getTektronixMSO5204B,
        'RigolMSO2302A': getRigolMSO2302A,
        'simulated': SimulatedInstrument,
        # 'KeysightDSOS804A': getKeysightDSOS804A,
        'GenericTektronix': getGenericScope,
    }

    ip_addr = None
    try:
        ip_addr = str(info_dict['instrument_ip_address'])
    except Exception:
        logger.debug("Invalid instrument IP address")

    device_id = manf_id = None
    try:
        device_id = str(info_dict['usb_device_id'])
        manf_id = str(info_dict['usb_manufacturer_id'])
    except Exception:
        logger.debug("Invalid instrument USB address")

    instrument_type = None
    try:
        instrument_type = info_dict['instrument_type']
    except Exception:
        logger.debug("Invalid instrument type")

    addr = None
    if cfg.getboolean('client', 'SIMULATED'):
        instrument_type = 'simulated'
        logger.debug("Using simulated instrument type", exc_info=True)
    elif ip_addr:
        addr = "TCPIP0::" + ip_addr + "::INSTR"
    elif device_id and manf_id:
        addr = "USB::" + manf_id + "::" + device_id + "::INSTR"
    else:
        logger.debug("No address info, using defaults for instrument")
    logger.info("calling ivi contructor with instrument type: %s"
                % instrument_type)
    if instrument_type in ivi_instruments:
        return ivi_instruments[instrument_type](addr)


def post_log(message, session=None):
    "posts logs to the server for info and troubleshooting"
    logger.info("posting log message: %s" % message)
    if not session:
        session = requests.session()
    headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
    data = {
        'message': message,
        'time': datetime.datetime.now().isoformat(),
    }
    json_data = json.dumps(data, ensure_ascii=True)
    url_s = (BASE_URL + "/nuc_logs/" +
             COMMON_SETTINGS['COMPANYNAME'] + '/' +
             COMMON_SETTINGS['HARDWARENAME'])
    response = session.post(url_s, data=json_data, headers=headers)
    logger.info("post_log response: %s" % response)


def round_dec(val, decimal_place=3):
    """Rounds to a given decimal place and rounds up on 5
       >>> round_dec(0.0045)
       0.005
       >>> round_dec(4.5e-05)
       0.0
       >>> round_dec(4.5e-05, 5)
       5e-05
       """
    val += 0.01 * 10 ** -decimal_place
    rounded_val = round(val, decimal_place)
    if rounded_val > 1e+36:
        rounded_val = float(str(rounded_val))
    return rounded_val


def round_sig(val, digits=3):
    """Rounds value to specified significant digits by determining
       decimal place needed to round number value and calling round_dec
       >>> round_sig(6.3193e-9)
       6.32e-09
       >>> round_sig(6.3193e-9, 4)
       6.319e-09
       >>> round_sig(0.55550)
       0.556
       """
    if val == 0:
        return 0.0
    decimal_place = int(-log10(abs(val))) + digits
    return round_dec(val, decimal_place)


def safe_json_loads(eval_str, default=collections.defaultdict(int)):
    try:
        retval = json.loads(eval_str)
    except Exception:
        retval = legacy_ast(eval_str, default)
    return retval


def legacy_ast(eval_str, default=collections.defaultdict(int)):
    try:
        retval = ast.literal_eval(eval_str)
    except Exception:
        retval = default
    return retval


class Timer(object):
    def signal_handler(self, signum, frame):
        raise Exception("Timeouts: Timed out!")

    def set_timeout(self, seconds=10):
        signal.signal(signal.SIGALRM, self.signal_handler)
        signal.alarm(seconds)

    def clear_timeout(self):
        signal.alarm(0)


def reset_device_with_tag(tag='Tektronix'):
    if not tag:
        tag = 'Tektronix'
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+)." +
                           "+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")
    devices = []
    for i in df.split('\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'),
                                                          dinfo.pop('device'))
                devices.append(dinfo)

    for d in devices:
        if tag in d['tag']:
            device_path = d['device']
        else:
            device_path = '/dev/bus/usb/002/003'

    print_debug("resetting %s" % device_path, post=True)
    e = '../../HelperScripts/usbreset ' + device_path
    subprocess.call(e, shell=True)


def authorize_and_request(url):
    headers = get_headers()
    ses = requests.session()
    response = ses.get(url, headers=headers)
    return response, ses


def decimation_factor(record_length):
    """Returns decimation factor based on record length"""
    dec_factors = {100000: 10, 125000: 12, 1000000: 100,
                   1250000: 125, 5000000: 500, 10000000: 1000, 20000000: 2000}
    factor = dec_factors[record_length]
    return factor


def get_usb_devices():
    """Returns list of all usb devices, including peripherals"""
    device_re = re.compile(
        "Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)  # noqa
    df = subprocess.check_output("lsusb")
    devices = []
    for i in df.split('\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = ('/dev/bus/usb/%s/%s'
                                   % (dinfo.pop('bus'), dinfo.pop('device')))
                devices.append(dinfo)
    return devices


def get_usbtmc_devices():
    """Returns list of usbtmc devices with manf, prod, and serial"""
    device_list = usbtmc.list_devices()
    instruments = []
    for dev in device_list:
        if dev is None:
            logger.warning('Device is not connected')
        else:
            dev._langids = (1033,)
            if dev._manufacturer is None:
                try:
                    dev._manufacturer = usb.util.get_string(dev, dev.iManufacturer)  # noqa
                except Exception as e:
                    logger.warning("failed to get manufacturer, e: %s" % e)
            man = str(dev._manufacturer)
            # manufacturers.append(man)
            if dev._product is None:
                dev._product = usb.util.get_string(dev, dev.iProduct)
            prod = str(dev._product)
            # products.append(prod)
            serial = usb.util.get_string(dev, dev.iSerialNumber)
            inst_dict = {
                'manufacturer': man,
                'product': prod,
                'serial': serial,
            }
            instruments.append(inst_dict)
    return instruments


def get_copley_devices():
    """Returns a list of Copley devices"""
    dev_ports = os.listdir("/dev")
    instruments = []
    for dev_port in dev_ports:
        if dev_port.find("copleycan") == 0:
            # TODO: query the can device to find the full name
            inst_dict = {
                "manufacturer": "Copley",
                "product": "ADP05518",
                "fancy_name": "CopleyAccelNetADP-055-18",
                "port": os.path.join("/dev", dev_port)
            }
            instruments.append(inst_dict)
    return instruments


def authorize_and_get(url):
    """Authorizes request to url and makes GET"""
    headers = get_headers()
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        headers = get_headers(refresh=True)
        response = requests.get(url, headers=headers)
    return response


class MySentry(object):
    """A fake sentry for there's no real Sentry Client"""
    def captureException(self, msg=""):
        logger.warning(msg)


def get_sentry():
    if 'SENTRY' not in cfg['client']:
        return MySentry()
    try:
        return Client(cfg['client']['SENTRY'])
    except Exception:
        return MySentry()


def get_pid_list():
    pid_list = []
    try:
        if not os.path.isfile(PID_JSON_FILE):
            with open(PID_JSON_FILE, 'w') as f:
                f.write(json.dumps(pid_list))
        with open(PID_JSON_FILE, 'r') as f:
            data = f.read()
            if data:
                pid_list = json.loads(data)
    except Exception as e:
        logger.error(e)

    return pid_list


def save_pid(pid):
    pid_list = get_pid_list()
    pid_list.append(pid)
    try:
        with open(PID_JSON_FILE, 'w') as f:
            f.write(json.dumps(pid_list))
    except Exception as e:
        logger.error(e)


def clear_pid_list():
    pid_list = []
    try:
        with open(PID_JSON_FILE, 'w') as f:
            f.write(json.dumps(pid_list))
    except Exception as e:
        logger.error(e)


def post_config_form(instruments=None):
    if not instruments:
        instruments = [{
                "manufacturer": "Tektronix",
                "product": "TektronixMDO3012",
                "fancy_name": "TektronixMDO3012"
            },
            {
                "manufacturer": "Tektronix",
                "product": "TektronixMSO2024",
                "fancy_name": "TektronixMSO2024"
            },
            {
                "manufacturer": "Tektronix",
                "product": "TektronixMSO5204B",
                "fancy_name": "TektronixMSO5204B"
            },
            {
                "manufacturer": "Rigol",
                "product": "RigolMSO2302A",
                "fancy_name": "RigolMSO2302A"
            }]
        return
    # upload all config forms for available instruments
    for instrument in instruments:
        inst_name = instrument["product"]
        if inst_name in dir(schema_forms):
            FORM_DICT = getattr(schema_forms, inst_name).FORM_DICT
            SCHEMA_DICT = getattr(schema_forms, inst_name).SCHEMA_DICT
        else:
            FORM_DICT = "unavailable for instrument: "+inst_name
            SCHEMA_DICT = {}
        if "fancy_name" in instrument.keys():
            inst_fancy_name = instrument["fancy_name"]
        else:
            inst_fancy_name = inst_name
        _data = {"schema": SCHEMA_DICT, "form": FORM_DICT, "defaults": [],
                 "instrument_type": inst_fancy_name}
        schema_url = urljoin(BASE_URL, "schemaform")
        headers = get_headers()
        session = requests.session()
        response = session.post(schema_url, headers=headers,
                                data=json.dumps(_data))
        assert response.status_code == 200
