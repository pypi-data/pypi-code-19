"""
Copyright 2013-2017 PhishMe, Inc.  All rights reserved.

This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
"""

try:
    from configparser import ConfigParser
    from io import StringIO
except ImportError:
    from ConfigParser import RawConfigParser as ConfigParser
    from StringIO import StringIO

import json
import logging
import os
import re
import sys
import time

from phishme_intelligence import PmValidationError


# Determine the major version of python running this script.
PYTHON_MAJOR_VERSION = sys.version_info[0]

# Get the current logger object.
# LOGGER = logging.getLogger('phishme')

IS_VALID_CONFIG = True


class ConfigCheck(object):
    """
    
    """
    
    def __init__(self, config):
        """

        :param config:
        :return:
        """

        self.config_copy = self._config_make_copy(config_old=config)
        self.logger = logging.getLogger(__name__)
        
    def validate_config(self):
        """
    
        :return:
        """

        # Remove any deactivated sections since they don't need to be scanned.
        self._remove_unused_sections()
    
        # Validate any options that are standard across multiple sections.
        self._validate_standard_options()
    
        # Loop through all sections in config file and call a method to validate it.
        for section in self.config_copy.sections():
    
            try:
                # Dynamically determine the correct method name depending on which section is being validated
                validate_config_section = getattr(self, '_validate_config_section_'+section)
    
                # Execute the correct validation method.
                validate_config_section(section=section)
    
            except PmValidationError as e:
                self._log_warn(message='%s, non-validated section' % e, section=section)
    
        # Return the result if this config is acceptable.
        return IS_VALID_CONFIG

    def _validate_standard_options(self):
        """

        :return:
        """
    
        # Loop through all the sections.
        for section in self.config_copy.sections():
    
            # Look for a 'host_with_protocol' option.
            option = 'host_with_protocol'
            if self.config_copy.has_option(section, option):
    
                # Ensure that it has a protocol.
                if not (self.config_copy.get(section, option).startswith('https://') or self.config_copy.get(section, option).startswith('http://')):
                    self._log_warn(message='protocol is missing', section=section, option=option, value=self.config_copy.get(section, option))
    
                # Remove option so it won't be rechecked.
                self.config_copy.remove_option(section=section, option=option)
    
            # Look for a 'host_without_protocol' option.
            option = 'host_without_protocol'
            if self.config_copy.has_option(section, option):
    
                # Ensure that it has a protocol.
                if self.config_copy.get(section, option).startswith('https://') or self.config_copy.get(section, option).startswith('http://'):
                    self._log_warn(message='Should not contain protocol.', section=section, option=option, value=self.config_copy.get(section, option))
    
                # Remove option so it won't be rechecked.
                self.config_copy.remove_option(section=section, option=option)
    
            # Look for a 'ssl_verify' option.
            option = 'ssl_verify'
            if self.config_copy.has_option(section, option):
    
                # Validate boolean.
                self._validate_option_boolean(section=section, option=option)
    
                # Remove option so it won't be rechecked.
                self.config_copy.remove_option(section=section, option=option)
    
    def _remove_unused_sections(self):
        """

        :return:
        """
    
        # Loop through all the sections.
        for section in self.config_copy.sections():
    
            # If a section has a 'use' option.
            if self.config_copy.has_option(section, 'use'):
    
                # If the 'use' option is set to False.
                if not self.config_copy.getboolean(section, 'use'):
    
                    # Remove the entire section.
                    self.config_copy.remove_section(section)
    
                else:
                    # Remove the 'use' option only.
                    self.config_copy.remove_option(section=section, option='use')

    @staticmethod
    def _config_make_copy(config_old):
        """
    
        :param config_old:
        :return:
        """
    
        # Make string from current ConfigParser object.
        config_string = StringIO()
        config_old.write(config_string)
    
        # We must reset the buffer ready for reading.
        config_string.seek(0)
    
        if PYTHON_MAJOR_VERSION == 3:
            config_new = ConfigParser(interpolation=None)
            config_new.read_file(config_string)
        else:
            config_new = ConfigParser()
            config_new.readfp(config_string)
    
        return config_new
    
    def _validate_config_section_pm_api(self, section):
        """
    
        :param section:
        :return:
        """
    
        for option in self.config_copy.options(section):
            value = self.config_copy.get(section, option)
    
            if option == 'base_url':
                self._validate_option_length(section, option, 10)
    
            elif option == 'user':
                self._validate_option_length(section, option, 32)
    
            elif option == 'pass':
                self._validate_option_length(section, option, 32)
    
            elif option == 'init_date':
                try:
                    time.strptime(self.config_copy.get(section, option), '%Y-%m-%d')
                except PmValidationError:
                    self._log_error(message='%s failed format check' % e, section=section, option=option)
    
            elif option == 'position':
                if len(value) == 0:
                    self._log_warn(message='is blank. This is normal during the initial execution of this script', section=section, option=option)
                else:
                    self._validate_option_length(section, option, 36)
    
            elif option == 'results_per_page':
                self._validate_option_number(section, option, minimum=1, maximum=100)
    
            elif option == 'max_retries':
                self._validate_option_number(section, option, minimum=1, maximum=10)

            elif option == 'expired_threat_days':
                self._validate_option_number(section, option, minimum=1, maximum=3650)
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_pm_jitter(self, section):
        """

        :param section:
        :return:
        """

        # Loop through all the options.
        for option in self.config_copy.options(section):

            # Get the value for the option.
            value = self.config_copy.get(section, option)

            if option == 'use':
                pass

            elif option == 'execution_frequency':
                self._validate_option_number(section=section, option=option, minimum=5, maximum=1440)

            elif option == 'scheduler_offset':
                execution_frequency = self.config_copy.getint('pm_jitter', 'execution_frequency')
                self._validate_option_number(section=section, option=option, minimum=0, maximum=execution_frequency)

            else:
                self._non_valid_option_found(section, option)
    
    def _validate_config_section_pm_product(self, section):
        """
    
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            if option == 'intelligence':
                self._validate_option_boolean(section, option)
    
            elif option == 'brand_intelligence':
                self._validate_option_boolean(section, option)
    
            else:
                self._non_valid_option_found(section, option)
    
    def _validate_config_section_pm_format(self, section):
        """
    
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            if option == 'cef':
                self._validate_option_boolean(section, option)
    
            elif option == 'json':
                self._validate_option_boolean(section, option)
    
            elif option == 'stix':
                self._validate_option_boolean(section, option)
    
            else:
                self._non_valid_option_found(section, option)
    
    def _validate_config_section_pm_impact(self, section):
        """
    
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'use':
                pass
    
            elif option == 'major':
                self._validate_option_boolean(section, option)
    
            elif option == 'moderate':
                self._validate_option_boolean(section, option)
    
            elif option == 'minor':
                self._validate_option_boolean(section, option)
    
            elif option == 'none':
                self._validate_option_boolean(section, option)
    
            else:
                self._non_valid_option_found(section, option)
    
    def _validate_config_section_local_proxy(self, section):
        """

        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'use':
                pass
    
            elif option == 'http':
                self._validate_option_length(section, option, 10)
    
            elif option == 'https':
                self._validate_option_length(section, option, 10)
    
            # Test BASIC auth settings.
            elif option == 'auth_basic_use':
                self._validate_option_boolean(section, option)
                if self.config_copy.getboolean(section, option):
                    auth_basic_user = self.config_copy.get(section, 'auth_basic_user')
                    auth_basic_pass = self.config_copy.get(section, 'auth_basic_pass')
                    self._validate_option_length(section, 'auth_basic_user', 1)
                    self._validate_option_length(section, 'auth_basic_pass', 1)
    
            # Ignore these, they will be screened if their respective sections are activated.
            elif option == 'auth_basic_user':
                pass
            elif option == 'auth_basic_pass':
                pass
    
            else:
                self._non_valid_option_found(section, option)
    
    def _validate_config_section_local_file_lock(self, section):
        """
    
        
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'use':
                pass
    
            elif option == 'lock_file':
                # Just test whether parent dir is present. Lock file will not exist when this test is being run.
                self._validate_option_folder_exists(section, option, verify_file=False)
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_local_log(self, section):
        """
    
        
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'log_file':
                self._validate_option_length(section, option, 6)
                self._validate_option_folder_exists(section, option, verify_file=True)

            elif option == 'log_level':
                # This is already validated when the logger is created, prior to executing the code in this class.
                pass

            elif option == 'log_name':
                # This is just a string to know what logger object to write or attach to.
                pass
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_local_sqlite(self, section):
        """
    
        
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'use':
                pass
    
            elif option == 'db_location':
                self._validate_option_folder_exists(section, option, verify_file=False)
    
            elif option == 'data_retention_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
            elif option == 'data_retention_days':
                self._validate_option_number(section, option, minimum=1, maximum=365)
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_raw_cef(self, section):
        """
        
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'use':
                pass
    
            elif option == 'max_eps':
                self._validate_option_number(section, option, minimum=100, maximum=1000)
    
            elif option == 'syslog_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
                    self._validate_option_length(section, 'syslog_host', 1)
                    self._validate_option_number(section, 'syslog_port', 1, 65536)
    
            elif option == 'append_file_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
                    self._validate_option_folder_exists(section, 'append_file_location', verify_file=False)
    
            elif option == 'multiple_file_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
                    self._validate_option_boolean(section, 'multiple_file_split_by_date')
    
                    self._validate_option_folder_exists(section, 'multiple_file_location', verify_file=False)
    
            # Ignore these, they will be screened if their respective sections are activated.
            elif option == 'append_file_location':
                pass
            elif option == 'multiple_file_location':
                pass
            elif option == 'multiple_file_split_by_date':
                pass
    
            else:
                self._non_valid_option_found(section, option)
    
    def _validate_config_section_integration_raw_json(self, section):
        """
    
        
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'use':
                pass
    
            elif option == 'append_file_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
                    self._validate_option_folder_exists(section, 'append_file_location', verify_file=False)
    
            elif option == 'multiple_file_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
                    self._validate_option_boolean(section, 'multiple_file_split_by_date')
    
                    self._validate_option_folder_exists(section, 'multiple_file_location', verify_file=False)
    
            # Ignore these, they will be screened if their respective sections are activated.
            elif option == 'append_file_location':
                pass
            elif option == 'multiple_file_location':
                pass
            elif option == 'multiple_file_split_by_date':
                pass
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_raw_stix(self, section):
        """

        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'use':
                pass
    
            elif option == 'append_file_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
                    self._validate_option_folder_exists(section, 'append_file_location', verify_file=False)
    
            elif option == 'multiple_file_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
                    self._validate_option_boolean(section, 'multiple_file_split_by_date')
    
                    self._validate_option_folder_exists(section, 'multiple_file_location', verify_file=False)
    
            # Ignore these, they will be screened if their respective sections are activated.
            elif option == 'append_file_location':
                pass
            elif option == 'multiple_file_location':
                pass
            elif option == 'multiple_file_split_by_date':
                pass
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_arcsight(self, section):
        """

        
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'port':
                self._validate_option_number(section=section, option=option, minimum=1, maximum=65536)
    
            elif option == 'max_eps':
                self._validate_option_number(section=section, option=option, minimum=1, maximum=1000)
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_carbon_black(self, section):
        """
    
        
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'api_token':
                self._validate_option_length(section=section, option=option, min_length=40)
    
            elif option == 'feed_name':
                if not self._validate_option_alphanumeric(value):
                    self._log_warn(message='', section=section, option=option, value=value)
    
            elif option == 'feed_id':
                if len(value) == 0:
                    self._log_warn(message='is blank. This is normal during the initial execution of this script.', section=section, option=option)
                else:
                    self._validate_option_number(section=section, option=option, minimum=0, maximum=1000)
    
            elif option == 'sqlite_location':
                self._validate_option_folder_exists(section=section, option=option, verify_file=True)
    
            elif option == 'sqlite_data_retention_days':
                self._validate_option_number(section=section, option=option, minimum=1, maximum=365)
    
            elif option == 'cb_feed':
                self._validate_option_folder_exists(section=section, option=option, verify_file=True)
    
            elif option == 'impact_major':
                self._validate_option_number(section=section, option=option, minimum=0, maximum=100)
    
            elif option == 'impact_moderate':
                self._validate_option_number(section=section, option=option, minimum=0, maximum=100)
    
            elif option == 'impact_minor':
                self._validate_option_number(section=section, option=option, minimum=0, maximum=100)
    
            elif option == 'impact_none':
                self._validate_option_number(section=section, option=option, minimum=0, maximum=100)
    
            elif option == 'excluded_md5_use':
                self._validate_option_boolean(section=section, option=option)
    
                # Handle the excluded MD5s only if this section is turned on.
                if self.config_copy.getboolean(section, option):
                    try:
                        json.loads(self.config_copy.get(section, 'excluded_md5'))
                    except PmValidationError as e:
                        self._log_warn(
                            message='%s: Excluded md5s are not formatted correctly. Ensure they are enclosed in [], double-quoted, and comma separated.' % e,
                            section=section,
                            option='excluded_md5'
                        )
    
            elif option == 'excluded_md5':
                # Handled conditionally above.
                pass
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_crits(self, section):
        """

        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'api_token':
                self._validate_option_length(section=section, option=option, min_length=40)
    
            elif option == 'source':
                self._validate_option_length(section=section, option=option, min_length=3)
    
            elif option == 'user':
                self._validate_option_length(section=section, option=option, min_length=3)
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_logrhythm(self, section):
        """
    
        
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'output_dir':
                self._validate_option_folder_exists(section=section, option=option, verify_file=False)
    
            else:
                self._non_valid_option_found(section, option)
    
    def _validate_config_section_integration_mcafee_siem(self, section):
        """
    
        
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'port':
                self._validate_option_number(section=section, option=option, minimum=1, maximum=65536)
    
            elif option == 'max_eps':
                self._validate_option_number(section=section, option=option, minimum=1, maximum=1000)
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_tipping_point_ips(self, section):
        """
    
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'user':
                self._validate_option_length(section=section, option=option, min_length=3)
    
            elif option == 'pass':
                self._validate_option_length(section=section, option=option, min_length=8)
    
            elif option == 'impact_major':
                self._validate_option_boolean(section=section, option=option)
    
            elif option == 'impact_moderate':
                self._validate_option_boolean(section=section, option=option)
    
            elif option == 'impact_minor':
                self._validate_option_boolean(section=section, option=option)
    
            elif option == 'impact_none':
                self._validate_option_boolean(section=section, option=option)
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_threatconnect(self, section):
        # The TC Exchange App has validation of inputs that is equivalent to what is done here
        pass

    def _validate_config_section_integration_qradar_siem(self, section):
        # QRadar ConfigForm already validates input
        pass

    @staticmethod
    def _validate_option_alphanumeric(reg_ex, search=re.compile(r'[^a-zA-Z0-9]').search):
        return not bool(search(reg_ex))
    
    def _validate_option_length(self, section, option, min_length):
        """
        :param section:
        :param option:
        :param min_length:
        :return:
        """
    
        value = self.config_copy.get(section, option)
        if len(value) < min_length:
            self._log_error(message='failed length check', section=section, option=option)

    def _validate_option_boolean(self, section, option):
        """
    
        :param section:
        :param option:
        
        :return:
        """
    
        try:
            self.config_copy.getboolean(section, option)
        except PmValidationError as e:
            self._log_error(message='%s: should be a boolean value' % e, section=section, option=option)

    def _validate_option_max_one_true(self, error_message, *args):
        """
    
        :param error_message:
        :param args:
        :return:
        """
    
        if sum(bool(a) for a in args) > 1:
            self._log_error(message=error_message)
    
    def _validate_option_number(self, section, option, minimum, maximum):
        """
    
        :param section:
        :param option:
        
        :param minimum:
        :param maximum:
        :return:
        """
    
        try:
            value = self.config_copy.getint(section, option)
    
            if minimum:
                if value < minimum:
                    self._log_error(message='should be greater than or equal to ' + str(minimum) + '.', section=section, option=option)
    
            if maximum:
                if value > maximum:
                    self._log_error(message='should be less than or equal to ' + str(maximum) + '.', section=section, option=option)
    
        except PmValidationError as e:
            self._log_error(message='%s: should be an integer value.' % e, section=section, option=option)
    
    def _validate_option_folder_exists(self, section, option, verify_file=False):
        """
    
        :param section:
        :param option:
        
        :param verify_file:
        :return:
        """
    
        value = self.config_copy.get(section, option)
    
        directory, file_name = os.path.split(value)
    
        if not os.path.isdir(directory):
            self._log_error(message='folder does not exist.', section=section, option=option)
    
        if verify_file:
            if not os.path.isfile(value):
                self._log_warn(message='file does not exist.', section=section, option=option)
        
    def _non_valid_option_found(self, section, option):
        """
    
        :param section:
        :param option:
        :return:
        """
    
        self._log_warn(message='non-validated option', section=section, option=option)

    def _log_warn(self, message, section=None, option=None, value=None):
        """
    
        :param message:
        :param section:
        :param option:
        :param value:
        :return:
        """
    
        if section and option and value:
            self.logger.warning('Within config.ini, section \'' + section + '\' contains option \'' + option + '\' contains value \'' + value + '\': ' + message)
    
        elif section and option:
            self.logger.warning('Within config.ini, section \'' + section + '\' contains option \'' + option + '\': ' + message)
    
        elif section:
            self.logger.warning('Within config.ini, section \'' + section + '\': ' + message)
    
        else:
            self.logger.warning('Within config.ini: ' + message)

    def _log_error(self, message, section=None, option=None, value=None):
        """
    
        :param message:
        :param section:
        :param option:
        :param value:
        :return:
        """
    
        global IS_VALID_CONFIG
        IS_VALID_CONFIG = False
    
        if section and option and value:
            self.logger.warning('Within config.ini, section \'' + section + '\' contains option \'' + option + '\' contains value \'' + value + '\': ' + message)
    
        elif section and option:
            self.logger.warning('Within config.ini, section \'' + section + '\' contains option \'' + option + '\': ' + message)
    
        elif section:
            self.logger.warning('Within config.ini, section \'' + section + '\': ' + message)
    
        else:
            self.logger.warning('Within config.ini: ' + message)
