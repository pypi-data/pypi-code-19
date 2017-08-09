"""
Written by: Ian Doarn

Main webdriver object
"""
import logging
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER
import os


class Page:
    """
    Base class from which to 
    inherit driver object
    """

    @staticmethod
    def create_driver(path_to_driver,
                      init_site=None,
                      additional_options=None,
                      additional_experimental_options=None,
                      desired_capabilities=None,
                      disable_logging=False):
        """
        Creates driver using the chromedriver
        
        After passing the path to the driver executable,
        the driver is created. By default save password notifications and 
        ignore certificate errors are on my default.
        
        the user can choose to add additional options, additional
        experimental options, and custom desired capabilities.
        
        additional options:
        
            must be a list of additional options
            
            example:
            
                ["--disable-extensions", "--user-data-dir=/Users..../Google/Chrome"]
                
            each will be added as:
            
                options.add_argument(option-from-list)
        
        additional experimental options:
        
            must be a list of dict objects. They must contain a key called
            'name' who's value is of what the option is called and a 
            key called 'value' who's value is the options value
            
            example:
            
                [{'name': 'perfs', 'value': {"download.default_directory" : "/some/path"}}]
            
            this will be interpreted as:
            
                options.add_experimental_option("perfs", perfs)
        
        desired capabilities:
        
            Must be a dict object
            example:
            
                desired_capabilities={
                                      'prefs': {
                                                'download': {
                                                             'default_directory': r'/Users/.../Desktop', 
                                                             "directory_upgrade": true, 
                                                             "extensions_to_open": ""
                                                             }
                                                }
                                      }
        
        :param path_to_driver: Path to the chromedriver.exe
        :param init_site: If not none, starts driver at a give url
        :param additional_options: Must be a list of additional options to add
        :param additional_experimental_options: Must be a dict of additional options to add
        :param desired_capabilities: a dict object of capabilities to crate the driver with
        :param disable_logging: Stop selenium from logging and creating is debug.log
        :return: driver object, driver url, driver session id
        """

        chromedriver = path_to_driver

        os.environ["webdriver.chrome.driver"] = chromedriver

        options = webdriver.ChromeOptions()
        options.add_argument("--enable-save-password-bubble=false")
        options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])

        if additional_options is not None:
            if type(additional_options) is list:
                for additional_optional_arg in additional_options:
                    options.add_argument(additional_optional_arg)
            elif type(additional_options) is not list:
                raise ValueError("additional_args kwarg value must "
                                 "be type list not {}".format(str(type(additional_options))))

        if additional_experimental_options is not None:
            if type(additional_experimental_options) is list:
                for option in additional_experimental_options:
                    if type(option) is dict:
                        options.add_experimental_option(option['name'], option['value'])
                    else:
                        raise ValueError("Can not add option: {} must be type dict not {}".format(str(option),
                                                                                                  str(type(option))))
            elif type(additional_experimental_options) is not list:
                raise ValueError("additional_experimental_options kwarg value "
                                 "must be type list not {}".format(str(type(additional_options))))

        if desired_capabilities is not None and type(desired_capabilities) is not dict:
            raise ValueError("desired_capabilities kwarg value "
                             "must be type dict not {}".format(str(type(additional_options))))

        if disable_logging:
            # Prevent selenium from logging if disable_logging is True
            LOGGER.setLevel(logging.WARNING)

        driver = webdriver.Chrome(executable_path=chromedriver,
                                  chrome_options=options,
                                  desired_capabilities=desired_capabilities)

        if init_site is None:
            return driver, driver.command_executor._url, driver.session_id
        else:
            driver.get(init_site)
            return driver, driver.command_executor._url, driver.session_id
