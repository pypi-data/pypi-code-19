import os
import configparser
import sys

class Settings(object):
    def __init__(self):
        self.profiles = {}
        
        self._load_defaults()
        self._load_global()
        self._load_profiles()

        try:
            self.use_profile(self.config['global']['default_profile'])
        except:
            self.use_profile('global')

        self._load_eVars()
        
    def _load_defaults(self):
        # GET/MAKE REQUIRED DIRECTORIES
        #=============================================
        self.blackfynn_dir = os.environ.get('BLACKFYNN_LOCAL_DIR', '{}/.blackfynn'.format(os.path.expanduser('~')))
        if not os.path.exists(self.blackfynn_dir):
            os.makedirs(self.blackfynn_dir)
            
        self.cache_dir = os.environ.get('BLACKFYNN_CACHE_LOC', os.path.join(self.blackfynn_dir,'cache'))
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        # GET CONFIG OBJECT
        #============================================
        self.config_file = os.path.join(self.blackfynn_dir,'config.ini')
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

            
        # DEFAULT SETTINGS
        #=============================================
        self.defaults = {    
            # blackfynn api locations
            'api_host'                    : 'https://api.blackfynn.io',
            'streaming_api_host'          : 'https://streaming.blackfynn.io',
            
            # blackfynn API token/secret
            'api_token'                   : None,
            'api_secret'                  : None,
            
            # streaming
            'stream_name'                 : 'prod-stream-blackfynn',
            'stream_aws_region'           : 'us-east-1',
            'stream_max_segment_size'     : 5000,
            
            # all requests
            'max_request_time'            : 120, # two minutes
            'max_request_timeout_retries' : 2,
            
            #io
            'max_upload_workers'          : 10,
            
            # timeseries
            'max_points_per_chunk'        : 10000,
            
            # s3 (amazon/local)
            's3_host'                     : '',
            's3_port'                     : '',
            
            # logging
            'log_level'                   : 'INFO',
            
            # cache
            'cache_index'                 : os.path.join(self.cache_dir, 'index.db'),
            'cache_max_size'              : 2048, #os.environ.get('BLACKFYNN_CACHE_MAX_SIZE', 2048) # in MBs
            'cache_inspect_interval'      : 1000, #os.environ.get('BLACKFYNN_CACHE_INSPECT_EVERY', 1000) # num page writes
            'ts_page_size'                : 3600, #int(os.environ.get('BLACKFYNN_TS_PAGE_SIZE', 3600)) # num points / page
            'use_cache'                   : True, #bool(int(os.environ.get('BLACKFYNN_USE_CACHE', True)))
        }

    def _load_global(self):
        self.default_profile = None
        self.profiles['global'] = self.defaults.copy()
        if 'global' in self.config:
            for key, value in self.config['global'].items():
                if value == 'none'            : self.profiles['global'][key] = None
                elif value.lower() == 'true'  : self.profiles['global'][key] = True
                elif value.lower() == 'false' : self.profiles['global'][key] = False
                elif value.isdigit()          : self.profiles['global'][key] = int(value)
                else                          : self.profiles['global'][key] = str(value)

    def _load_eVars(self):
        eVars_dict = {
            'api_host'               : 'BLACKFYNN_API_LOC',
            'streaming_api_host'     : 'BLACKFYNN_STREAMING_API_LOC',
            'api_token'              : 'BLACKFYNN_API_TOKEN',
            'api_secret'             : 'BLACKFYNN_API_SECRET',
            'stream_name'            : 'BLACKFYNN_STREAM_NAME',
            
            'cache_max_size'         : 'BLACKFYNN_CACHE_MAX_SIZE',
            'cache_inspect_interval' : 'BLACKFYNN_CACHE_INSPECT_EVERY',
            'ts_page_size'           : 'BLACKFYNN_TS_PAGE_SIZE',
            'use_cache'              : 'BLACKFYNN_USE_CACHE',
            'log_level'              : 'BLACKFYNN_LOG_LEVEL',
            'default_profile'        : 'BLACKFYNN_PROFILE'
        }

        self.eVars = {}
        for key, eVar in eVars_dict.items():
            value = os.environ.get(eVar,None)
            if value is not None:
                self.eVars[key] = [value,eVar]
        
        self.__dict__.update((key, os.environ.get(value,self.__dict__[key])) for key,value in eVars_dict.items())

        if 'default_profile' in self.eVars:
            try:
                self.use_profile(self.eVars['default_profile'][0])
            except:
                sys.exit("Invalid value '{}' for environment variable {}".format(self.eVars['default_profile'][0],self.eVars['default_profile'][1]))
                
    def _load_profiles(self):
        for name in self.config.sections():
            if name is not 'global':
                self.profiles[name] = self.profiles['global'].copy()
                for key, value in self.config[name].items():
                    if value == 'none'            : self.profiles[name][key] = None
                    elif value.lower() == 'true'  : self.profiles[name][key] = True
                    elif value.lower() == 'false' : self.profiles[name][key] = False
                    elif value.isdigit()          : self.profiles[name][key] = int(value)
                    else                          : self.profiles[name][key] = str(value)

    def use_profile(self,name):
        if name is not None:
            if name not in self.profiles:
                raise Exception('Invaid profile name')
            else:
                self.__dict__.update(self.profiles[name])
                self.active_profile = name
                if name is 'global': self.active_profile = 'none'

settings = Settings()
