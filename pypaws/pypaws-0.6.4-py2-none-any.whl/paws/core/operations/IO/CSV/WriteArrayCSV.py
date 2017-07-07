from os.path import splitext
from os import linesep
import numpy as np

from ...Operation import Operation
from ... import optools

class WriteArrayCSV(Operation):
    """Write a 2d array to a csv file"""

    def __init__(self):
        input_names = ['array','headers','dir_path','filename','filetag']
        output_names = ['csv_path']
        super(WriteArrayCSV, self).__init__(input_names, output_names)
        self.input_doc['array'] = 'any 2d array'
        self.input_doc['headers'] = 'list of headers (optional)- one header for each column of array'
        self.input_doc['dir_path'] = 'the path to the destination directory'
        self.input_doc['filename'] = 'the name of the file to be saved- no extension is expected'
        self.input_doc['filetag'] = 'tag appended to filename- no extension is expected'
        self.output_doc['csv_path'] = 'the path to the finished csv file: dir_path+filename+filetag+.csv'
        self.input_src['array'] = optools.wf_input
        self.input_src['headers'] = optools.text_input
        self.input_src['dir_path'] = optools.fs_input
        self.input_src['filename'] = optools.wf_input
        self.input_src['filetag'] = optools.text_input
        self.input_type['array'] = optools.ref_type
        self.input_type['headers'] = optools.str_type
        self.input_type['dir_path'] = optools.path_type
        self.input_type['filename'] = optools.ref_type
        self.input_type['filetag'] = optools.str_type
        self.inputs['filetag'] = ''

    def run(self):
        #import pdb; pdb.set_trace()
        h = self.inputs['headers']
        a = self.inputs['array']
        tag = ''
        if self.inputs['filetag']:
            tag = self.inputs['filetag']
        csv_path = self.inputs['dir_path']+'/'+self.inputs['filename']+tag+'.csv'
        self.outputs['csv_path'] = csv_path
        if h is not None:
            h_str = ''
            for i in range(len(h)-1):
                h_str += h[i] + ', '
            h_str = h_str+h[-1]
            np.savetxt(csv_path, a, delimiter=',', newline=linesep, header=h_str)
        else:
            np.savetxt(csv_path, a, delimiter=',', newline=linesep)

