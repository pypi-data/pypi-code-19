"""nb2py: dumps marked code cells from a Jupyter notebook into a text file."""

__author__ = "Hugo Guillen-Ramirez"
__copyright__ = "Copyright 2017"
__email__ = "hugoagr@gmail.com"

import json


def dump(input_notebook,output_py,marker='~'):
    """Writes the marked cells from the notebook into a python file.
    By default, this function writes all cells that start with the comment `#~`.
    
    Parameters
    ----------
    input_notebook : str
        Path to Jupyter Notebook.
    output_py : str
        Output file.
    marker : str
        String in the fist comment of the cell that indicates if the cell is written or not.
        default: ~             
    """    
    with open(input_notebook) as f:
        d = json.load(f)
    with open (output_py,'w') as f:
        for cell in [c for c in d['cells'] if c['cell_type']=='code']:
            source = cell['source']
            if len(source)>0 and source[0].strip() == '#'+marker:
                f.write(''.join(source[1:])+'\n\n')
                
                
def dump_indices(input_notebook,output_py,indices=None):
    """Writes the selected cells by index from the notebook into a python file.
    This is useful to export a markdown cell as a README.md file.
    
    Parameters
    ----------
    input_notebook : str
        Path to Jupyter Notebook.
    output_py : str
        Output file.
    indices : list
        list of cell indices.
    """    
    with open(input_notebook) as f:
        d = json.load(f)
    with open (output_py,'w') as f:        
        for cell in [d['cells'][idx] for idx in indices]:
            source = cell['source']
            f.write(''.join(source)+'\n\n')

