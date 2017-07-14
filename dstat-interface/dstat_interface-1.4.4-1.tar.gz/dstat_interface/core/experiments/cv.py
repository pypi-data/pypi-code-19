import time
import struct

from .experiment_template import PlotBox, Experiment

class CVExp(Experiment):
    id = 'cve'
    """Cyclic Voltammetry experiment"""
    def setup(self):
        super(CVExp, self).setup()
        self.datatype = "CVData"
        self.xlabel = "Voltage (mV)"
        self.ylabel = "Current (A)"
        self.datalength = 2 * self.parameters['scans']  # x and y for each scan
        self.databytes = 6  # uint16 + int32
        self.plot_format['current_voltage']['xlims'] = tuple(
                sorted((int(self.parameters['v1']), int(self.parameters['v2'])))
                )
        
        self.commands += "E"
        self.commands[2] += "C"
        self.commands[2] += str(self.parameters['clean_s'])
        self.commands[2] += " "
        self.commands[2] += str(self.parameters['dep_s'])
        self.commands[2] += " "
        self.commands[2] += str(int(int(self.parameters['clean_mV'])*
                                (65536./3000)+32768))
        self.commands[2] += " "
        self.commands[2] += str(int(int(self.parameters['dep_mV'])*
                                (65536./3000)+32768))
        self.commands[2] += " "
        self.commands[2] += str(self.parameters['v1'])
        self.commands[2] += " "
        self.commands[2] += str(self.parameters['v2'])
        self.commands[2] += " "
        self.commands[2] += str(self.parameters['start'])
        self.commands[2] += " "
        self.commands[2] += str(self.parameters['scans'])
        self.commands[2] += " "
        self.commands[2] += str(self.parameters['slope'])
        self.commands[2] += " "