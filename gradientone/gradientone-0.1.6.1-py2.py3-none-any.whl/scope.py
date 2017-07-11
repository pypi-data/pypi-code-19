"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import collections
import datetime
import json
import numpy as np
import os.path
import traceback
import time
import usb

import gateway_helpers as helpers
import tek_grl_configs
import test_runners
from configparser import ConfigParser
from device_drivers import usb_controller
from base import BaseClient


# Read in config file info
cfg = ConfigParser()
PATH_TO_CFG_FILE = '/etc/gradient_one.cfg'
cfg.read(PATH_TO_CFG_FILE)
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']
DEFAULT_TEK_TYPE = 'TektronixMDO3012'
BASE_URL = helpers.BASE_URL
MAX_VALID_MEAS_VAL = 1000000000
try:
    TMPDIR = CLIENT_SETTINGS["TMPDIR"]
except:
    TMPDIR = "/tmp"

# Get Sentry client for Sentry logging
SENTRY_CLIENT = helpers.get_sentry()

# For Non-Sentry logging
logger = helpers.logger


class ScopeClient(BaseClient):
    """Manages scope config related client workflow"""
    def __init__(self, *args, **kwargs):
        super(ScopeClient, self).__init__(*args, **kwargs)
        self.post_config_form([{
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
            }])
        url = BASE_URL + "/gateway"
        payload = {
            "name": COMMON_SETTINGS['HARDWARENAME'],
            "company": COMMON_SETTINGS['COMPANYNAME'],
        }
        data = json.dumps(payload)
        response = self.put(url, data=data)
        if response.status_code != 200:
            logger.warning("PUT to %s failed" % url)
        self.dec_factor = 1
        self.tags = ['Scope']  # to just get scope commands

    def process_response(self, response):
        """Processes response from server to config get requests

        This gets called when check_for_commands() and
        check_command_url() get a response from the server.

        if command == Config or Capture executing w/ TestRunner()
        elif it's 'check_scope'
        elif it's some other Special command
        else it considers the response a non-command

        """
        if not response.text:
            logger.debug("No response text")
            return
        try:
            commands = json.loads(response.text)['commands']
            if commands:
                command = collections.defaultdict(str, commands[0])
            else:
                command = None
        except Exception as e:
            logger.warning("Exception loading setup data, e:%s reponse is:%s"
                           % (e, response.text))
            return
        if not command:
            logger.debug("No command; Time:" + str(datetime.datetime.now()) +
                         "; Gateway:" + COMMON_SETTINGS['HARDWARENAME'] +
                         "; Company:" + COMMON_SETTINGS['COMPANYNAME'] +
                         "; Domain:" + COMMON_SETTINGS['DOMAIN'])
            return
        logger.debug("Setup received: %s" % command)
        kind = command['category']
        if kind == 'Config' or kind == 'Capture':
            logger.info("%s Command received: %s" % (kind, command))
            test_runner = test_runners.TestRunner(self.session)
            test_runner.run_command(command)
        # most commands will be test runs like above
        # special commands and continue commands below
        elif command['arg'] == 'check_scope':
            scope_info = None
            try:
                instrument_type = command['instrument_type']
                scope_info = self.check_scope(instrument_type)
            except Exception:
                logger.error(traceback.format_exc())
                SENTRY_CLIENT.captureException()
            finally:
                self.update_gateway_state(scope_info)
        elif command['category'] == 'Special':
            self.process_special_command(command)
        else:
            logger.info("Unexpected command in response: %s" % command)

    def process_special_command(self, command):
        """Runs special commands not associated with an instrument run"""
        setup = command
        spc = setup['special_command']
        logger.info("Special command found: %s" % spc)
        if spc == 'reset' or spc == 'check':
            self.check_or_reset(self.session, spc, setup[
                'instrument_type'])
        elif spc == 'reset_usb':
            helpers.reset_device_with_tag()
        elif spc == 'UsbRawInputCommand':
            usb_contr = usb_controller.UsbController()
            instr = usb_contr.get_instrument(setup['mnf_id'], setup['dev_id'])
            logger.info("issuing command %s" % setup['usb_command'])
            resp = usb_contr.ask(instr, setup['usb_command'])
            logger.info(resp)
        elif spc == 'grl-test':
            logger.info("starting grl-test")
            grl = tek_grl_configs.Grl_Test()
            resp = grl.run_grl_test()
            logger.info("grl test response: %s" % resp)
            self.update_gateway_state(self.session, {'grl_test': resp})
        else:
            logger.warning("unknown special command: %s" % command)
            self.update_gateway_state(self.session, {'unknown_command': spc})

    def reset_scope(self, instrument_type=DEFAULT_TEK_TYPE):
        """Calls utility.reset() to reset scope"""
        try:
            instr = helpers.get_instrument({
                'instrument_type': instrument_type})
        except Exception:
            logger.debug(traceback.format_exc())
        try:
            instr.utility.reset()
            logger.debug("instrument reset")
        except Exception:
            logger.debug(traceback.format_exc())
        finally:
            instr.close()

    def check_scope(self, instrument_type=DEFAULT_TEK_TYPE):
        """Checks acquisition type to check if scope working"""
        acq_type = None
        try:
            instr = helpers.get_instrument({
                'instrument_type': instrument_type})
        except Exception:
            logger.info(traceback.format_exc())
            return None
        try:
            acq_type = instr.acquisition.type
            acq_time_per_record = instr.acquisition.time_per_record
            trigger_type = instr.trigger.type
            trigger_coupling = instr.trigger.coupling
            logger.info("acq_type: " + acq_type)
            inst_info = {
                'acq_type': acq_type,
                'acq_time_per_record': acq_time_per_record,
                'trigger_type': trigger_type,
                'trigger_coupling': trigger_coupling,
            }
            logger.info("basic instrument info: %s" % inst_info)
            return acq_type
        except Exception:
            logger.info(traceback.format_exc())
        finally:
            instr.close()
            return acq_type

    def set_scope(self, scope_info=None):
        """Sets basic scope info to test scope"""
        scope_dict = collections.defaultdict(int)
        scope_dict.update(scope_info)
        if not scope_dict['instrument_type']:
            scope_dict['instrument_type'] = DEFAULT_TEK_TYPE
        try:
            instr = helpers.get_instrument(scope_dict)
        except Exception:
            logger.info(traceback.format_exc())
            return None
        try:
            instr.acquisition.type = scope_dict['acq_type']
            instr.acquisition.time_per_record = scope_dict['acq_time_per_record']  # noqa
            instr.trigger.type = scope_dict['trigger_type']
            instr.trigger.coupling = scope_dict['coupling']
            return True
        except Exception:
            logger.info(traceback.format_exc())
            return None

    def check_or_reset(self, session, command, instrument_type):
        """Runs ad hoc check or reset scope commands"""
        command_funcs = {
            'reset': self.reset_scope,
            'check': self.check_scope,
        }
        try:
            scope_info = command_funcs[command](instrument_type)
        except Exception:
            logger.error(traceback.format_exc())
            scope_info = None
        finally:
            self.update_gateway_state(session, scope_info)

    def _shrink(self, summary_channel, mode='normal',
                max_length=CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER']):
        """Shinks a voltage list to a decimated waveform

        Decimated waveform needed for faster data transfer and to save
        browser memory when drawing the summary view.
        """
        logger.debug("shrinking summary channel")
        y_values = summary_channel['y_values']
        len_y_values = len(y_values)
        dec_factor = len_y_values / int(max_length)
        summary_channel['dec_factor'] = dec_factor
        self.dec_factor = dec_factor  # migrate out
        og_time_step = summary_channel['time_step']
        summary_channel['og_time_step'] = og_time_step
        new_time_step = summary_channel['dec_factor'] * self.time_step
        summary_channel['time_step'] = new_time_step
        self.dec_time_step = new_time_step  # migrate out
        shrunk_list = [y_values[0]]
        offset = summary_channel['dec_factor']  # for sampling

        while offset < len_y_values:
            if mode == 'normal':
                shrunk_list.append(y_values[offset])
                offset += int(dec_factor)
            elif mode == 'average':
                offset += int(dec_factor)
                mean_value = np.mean(
                    y_values[offset - int(dec_factor): offset])
                shrunk_list.append(mean_value)
            elif mode == 'downsample':
                # use scipy.signal.downsample
                pass
            elif mode == 'voltage_peak_to_peak':
                dec_factor = dec_factor * 2
        logger.info("Shrunk list down to %s items" % len(shrunk_list))
        return shrunk_list

    def _post_summary_waveform(self):
        """Sends summary dataset for full waveform views

        If the length of y values is greater than the max for a
        browser, the list will be 'shrunk' or sampled to get a
        summary representation of the list of values. If the full
        list is under the max length then no shrinking or sampling
        is needed and the full list is posted.
        """
        test_run_id = self.test_run_id
        summary_channels = []
        for channel in self.channels:
            summary_channel = {}  # create new summary channel
            summary_channel.update(channel)  # copy the channel info
            max_length = int(CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER'])
            if len(summary_channel['y_values']) > max_length:
                summary_channel['y_values'] = self._shrink(summary_channel)
            summary_channels.append(summary_channel)
        summary_data = {}
        summary_data.update(self.metadata)
        summary_data['channels'] = summary_channels
        payload = {
            'data': summary_data,
        }
        json_data = json.dumps(payload)
        logger.info("posting end to end (decimated) waveform")
        url_d = BASE_URL + "/results/" + str(test_run_id) + "/summary"
        self.post(url_d, data=json_data)
        filename = 'summary-waveform-%s.json' % self.test_run_id
        summary_file = os.path.join(TMPDIR, filename)
        logger.info("Writing waveform to %s" % summary_file)
        with open(summary_file, 'w') as f:
            f.write(json_data)

    def _metadata_from_channel(self, channel):
        """Strips y_values from channel, leaving only metadata"""
        channel_copy = {}
        channel_copy.update(channel)
        if 'y_values' in channel_copy:
            del channel_copy['y_values']
        return channel_copy

    def _get_metadata_only(self, results_dict={}, channels={}):
        """Gets metadata from the args

        Removes the trace data from the channels leaving just metadata
        """
        metadata = {}
        metadata.update(results_dict)
        metadata['channels'] = []
        if results_dict != {} and 'channels' in results_dict:
            channels = results_dict['channels']
        for channel in channels:
            metadata['channels'].append(self._metadata_from_channel(channel))
        filename = 'full-trace-%s.json' % self.test_run_id
        trace_file = os.path.join(TMPDIR, filename)
        if not os.path.exists(trace_file):
            logger.error("No full trace file!")
            metadata['error'] = "No trace data"
        return metadata

    def get_instrument_settings(self):
        """Instrument settings that are channel independent

        Separate from the config excerpt
        """
        settings = {}
        settings['h_divs'] = self.get_horizontal_divisions()
        settings['v_divs'] = self.get_vertical_divisions()
        settings['timebase_range'] = self.instr.timebase.range
        settings['timebase_position'] = self.instr.timebase.position
        settings['timebase_scale'] = self.instr.timebase.scale
        return settings


class IviScopeClient(ScopeClient):
    """Manages ivi scope related client workflow"""

    def fetch_raw_setup(self, last_try=False):
        if cfg.getboolean('client', 'SIMULATED'):
            return "simulated config info"
        logger.debug("fetching raw_setup")
        try:
            raw_setup = self.instr.system.fetch_setup()
        except Exception:
            self.logger.warning("fetch setup failed", exc_info=True)
            if last_try:
                return None
            else:
                raw_setup = self.fetch_raw_setup(last_try=True)
        return raw_setup

    def load_raw_setup(self, try_count=0):
        logger.debug("loading raw setup")
        ascii_config = self.config['info']['raw_setup'].encode('ascii')
        try:
            self.instr.system.load_setup(ascii_config)
        except Exception:
            self.logger.warning("failed loading raw setup", exc_info=True)
            if try_count > 10:
                logger.debug("not retrying")
            else:
                self.instr.close()
                time.sleep(1)
                logger.debug("retrying...")
                try_count = try_count + 1
                self.instr = helpers.get_instrument(self.test_run)
                self.load_raw_setup(try_count)

    def _setinstr(self, ivi_obj, key, value, label=''):
        try:
            setattr(ivi_obj, key, value)
            self.config_scorecard['success'].append(label + key)
            return True
        except Exception:
            logger.debug("failed setting %s" % label + key)
            logger.debug(traceback.format_exc())
            self.exception_count += 1
            self.config_scorecard['failure'].append(label + key)
            return False

    def _setinstr_with_tries(self, ivi_obj, key, value, label='', tries=3):
        success = False
        for attempt in range(tries):
            try:
                setattr(ivi_obj, key, value)
                success = True
                break
            except usb.core.USBError as e:
                logger.debug("USB Error in setting instrument", trace=True)
                self.handle_usb_error(e)
            except Exception:
                logger.debug("failed to set timebase: %s %s" %
                             (key, value), trace=True)
                self.exception_count += 1
                time.sleep(0.1)
        if success:
            self.config_scorecard['success'].append(label + key)
        else:
            self.config_scorecard['failure'].append(label + key)
