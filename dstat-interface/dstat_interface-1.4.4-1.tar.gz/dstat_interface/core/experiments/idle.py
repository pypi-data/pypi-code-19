import time
import struct

from .experiment_template import Experiment

class OCPExp(Experiment):
    """Open circuit potential measumement in statusbar."""
    id = 'ocp'
    def __init__(self):
        self.databytes = 8
        
        self.commands = ["EA", "EP0 0 "]
    
        self.commands[0] += "2 " # input buffer
        self.commands[0] += "3 " # 2.5 Hz sample rate
        self.commands[0] += "1 " # 2x PGA
        
        
    def data_handler(self, data_input):
        """Overrides Experiment method to only send ADC values."""
        scan, data = data_input
        # 2*uint16 + int32
        seconds, milliseconds, voltage = struct.unpack('<HHl', data)
        return (voltage/5.592405e6)
        
class PMTIdle(Experiment):
    """Open circuit potential measumement in statusbar."""
    id = "pmt_idle"
    def __init__(self):
        self.databytes = 8
    
        self.commands = ["EA", "EM"]
    
        self.commands[0] += "2 " # input buffer
        self.commands[0] += "3 " # 2.5 Hz sample rate
        self.commands[0] += "1 " # 2x PGA