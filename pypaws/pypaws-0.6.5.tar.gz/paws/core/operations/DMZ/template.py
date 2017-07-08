"""
Template for developing operations for paws.
"""
from operation import Operation
import optools

# Replace <OperationName> with a SHORT operation title 
class <OperationName>(Operation):
    # Replace <Description of Operation> with a detailed description 
    """<Description of Operation>"""

    def __init__(self):
        """<Description of anything notable performed during __init__()>"""
        # Name the inputs and outputs for your operation.
        input_names = ['<input_name_1>','<input_name_2>',<...>]
        output_names = ['<output_name_1>','<output_name_2>',<...>]
        # Replace <OperationName> with the same name chosen above
        super(<OperationName>,self).__init__(input_names,output_names)
        # Provide a basic description for each of the inputs and outputs 
        self.input_doc['<input_name_1>'] = '<expectations for input 1>'
        self.input_doc['<input_name_2>'] = '<etc>'
        self.output_doc['<output_name_1>'] = '<description of output 1>'
        self.output_doc['<output_name_2>'] = '<etc>'
        # OPTIONAL: set default sources, types, values for the inputs.
        # Valid sources:
        #   optools.no_input (default input to None), 
        #   optools.wf_input (take input from another operation in the workflow), 
        #   optools.text_input (manual text input)
        #   optools.plugin_input (take input from a PawsPlugin)
        #   optools.batch_input (input provided by a batch/realtime operation)
        self.input_src['<input_name_1>'] = <optools.some_source>
        self.input_src['<input_name_2>'] = <etc>
        # Valid types: optools.none_type (None), optools.str_type (string), 
        #   optools.int_type (integer), optools.float_type (float), 
        #   optools.bool_type (boolean), optools.ref_type (direct reference),
        #   optools.path_type (a path to something in the filesystem or workflow), 
        #   optools.auto_type (default for chosen source, or input set by batch)
        self.input_type['<input_name_1>'] = <optools.some_type>
        self.input_type['<input_name_2>'] = <etc>
        
    # Write a run() function for this Operation.
    def run(self):
        """<Description of processing performed by run()>"""
        # Optional- create references in the local namespace for cleaner code.
        <inp1> = self.inputs['<input_name_1>']
        <inp2> = self.inputs['<input_name_2>']
        <etc>
        # Perform the computation
        < ... >
        # Save the output
        self.outputs['<output_name_1>'] = <computed_value_1>
        self.outputs['<output_name_2>'] = <etc>

