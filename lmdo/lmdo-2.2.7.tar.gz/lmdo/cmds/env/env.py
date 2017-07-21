from __future__ import print_function

import os
import json

from lmdo.oprint import Oprint
from lmdo.lmdo_config import lmdo_config
from lmdo.convertors.stack_var_convertor import StackVarConvertor

class Env(object):
    """Environment export handler"""
   
    def __init__(self):
        self._config = lmdo_config
        self.convert_config()

    def export(self):
        export_map = self._config.get('EnvExportMap')
        if not export_map:
            Oprint.warn('You have not defined "EnvExportMap" in your lmdo config file, no action taken')
            return True
        cmd = ''
        for key, value in export_map.iteritems():
            if len(cmd) == 0:
                cmd += 'export {}="{}"'.format(key, value)
            else:
                cmd += ' && export {}="{}"'.format(key, value)
        
        print(cmd)

    def convert_config(self):
        """converting stack var"""
        convertor = StackVarConvertor()

        # Convert stack output key value if there is any
        _, json_data = convertor.process((json.dumps(self._config.config), self._config.config))
        
        self._config.config = json_data

        return True


        
