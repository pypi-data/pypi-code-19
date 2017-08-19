# -*- coding: utf-8 -*-
# Copyright © 2017 Carl Chenet <carl.chenet@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/

# Get values of the configuration file
'''Get values of the configuration file'''

# standard library imports
from configparser import SafeConfigParser, NoOptionError, NoSectionError
import logging
import os
import os.path
import socket
import sys

# 3rd party library imports
import feedparser

def cfgparse(clioptions):
    '''Parse the configurations'''
    for pathtoconfig in clioptions.configs:
        options = {}
        # read the configuration file
        config = SafeConfigParser()
        if not config.read(os.path.expanduser(pathtoconfig)):
            sys.exit('Could not read the configuration file')
        ###########################
        # 
        # the mastodon section
        # 
        ###########################
        section = 'mastodon'
        if config.has_section(section):
            ############################
            # instance_url option
            ############################
            confoption = 'instance_url'
            if config.has_option(section, confoption):
                confkey = 'mastodon_{optionname}'.format(optionname=confoption)
                options[confkey] = config.get(section, confoption)
            else:
                sys.exit('You should define Mastodon instance url with the "{confoption}" in the [{section}] section'.format(confoption=confoption, section=section))
            ############################
            # user_credentials option
            ############################
            confoption = 'user_credentials'
            if config.has_option(section, confoption):
                confkey = 'mastodon_{optionname}'.format(optionname=confoption)
                options[confkey] = config.get(section, confoption)
            else:
                sys.exit('You should define Mastodon user credentials for with "{confoption}" in the [{section}] section'.format(confoption=confoption, section=section))
        if config.has_section(section):
            ############################
            # client_credentials option
            ############################
            confoption = 'client_credentials'
            if config.has_option(section, confoption):
                confkey = 'mastodon_{optionname}'.format(optionname=confoption)
                options[confkey] = config.get(section, confoption)
            else:
                sys.exit('You should define Mastodon client credentials with the "{confoption}" in the [{section}] section'.format(confoption=confoption, section=section))
            ############################
            # toot_visibility option
            ############################
            confoption = 'toot_visibility'
            if config.has_option(section, confoption):
                confkey = 'mastodon_{optionname}'.format(optionname=confoption)
                options[confkey] = config.get(section, confoption, fallback='public')
            ############################
            # image_path option
            ############################
            confoption = 'image_path'
            if config.has_option(section, confoption):
                confkey = 'mastodon_{optionname}'.format(optionname=confoption)
                options[confkey] = config.get(section, confoption)
            ############################
            # {lang}_image_path option
            ############################
            for langoption in config[section]:
                if langoption.endswith('_image_path'):
                    langkey = 'mastodon_{keywithlang}'.format(keywithlang=langoption)
                    options[langkey] = config.get(section, langoption)
        ###########################
        # 
        # the twitter section
        # 
        ###########################
        section = 'twitter'
        if config.has_section(section):
            ############################
            # consumer_key option
            ############################
            confoption = 'consumer_key'
            if config.has_option(section, confoption):
                confkey = 'twitter_{optionname}'.format(optionname=confoption)
                options[confkey] = config.get(section, confoption)
            else:
                sys.exit('You should define Mastodon instance url with the "{confoption}" in the [{section}] section'.format(confoption=confoption, section=section))
            ############################
            # consumer_secret option
            ############################
            confoption = 'consumer_secret'
            if config.has_option(section, confoption):
                confkey = 'twitter_{optionname}'.format(optionname=confoption)
                options[confkey] = config.get(section, confoption)
            else:
                sys.exit('You should define Mastodon instance url with the "{confoption}" in the [{section}] section'.format(confoption=confoption, section=section))
            ############################
            # access_token option
            ############################
            confoption = 'access_token'
            if config.has_option(section, confoption):
                confkey = 'twitter_{optionname}'.format(optionname=confoption)
                options[confkey] = config.get(section, confoption)
            else:
                sys.exit('You should define Mastodon instance url with the "{confoption}" in the [{section}] section'.format(confoption=confoption, section=section))
            ############################
            # access_token_secret option
            ############################
            confoption = 'access_token_secret'
            if config.has_option(section, confoption):
                confkey = 'twitter_{optionname}'.format(optionname=confoption)
                options[confkey] = config.get(section, confoption)
            else:
                sys.exit('You should define Mastodon instance url with the "{confoption}" in the [{section}] section'.format(confoption=confoption, section=section))
            ############################
            # image_path option
            ############################
            confoption = 'image_path'
            if config.has_option(section, confoption):
                confkey = 'twitter_{optionname}'.format(optionname=confoption)
                options[confkey] = config.get(section, confoption)
            ############################
            # {lang}_image_path option
            ############################
            for langoption in config[section]:
                if langoption.endswith('_image_path'):
                    langkey = 'twitter_{keywithlang}'.format(keywithlang=langoption)
                    options[langkey] = config.get(section, langoption)
        ###########################
        # 
        # the image section
        # 
        ###########################
        section = 'image'
        confoption = 'path_to_image'
        if config.has_section(section):
            if config.has_option(section, confoption):
                options['path_to_image'] = config.get(section, confoption)
            ############################
            # {lang}_image_path option
            ############################
            for langoption in config[section]:
                if langoption.endswith('_image_path'):
                    options[langoption] = config.get(section, langoption)
        ###########################
        # 
        # the entrylist section
        # 
        ###########################
        section = 'entrylist'
        if config.has_section(section):
            confoption = 'path_to_list'
            options['path_to_list'] = config.get(section, confoption)
        else:
            sys.exit('You should provide a {confoption} parameter in the [{section}] section'.format(section=section, confoption=confoption))
        ###########################
        # 
        # the prefix section
        # 
        ###########################
        section = 'prefix'
        if config.has_section(section):
            for prefixoption in config[section]:
                if prefixoption.endswith('_prefix'):
                    options[prefixoption] = config.get(section, prefixoption)
    return options
