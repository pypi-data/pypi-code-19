""" VASP Celery Tasks

"""
import os
from datetime import datetime

from pymatgen.alchemy.materials import TransformedStructure

from mattoolkit.utils.celery import app
from mattoolkit.config import get_cluster_config
from mattoolkit.material.calculation import vasp_calculation
from mattoolkit.utils.mongodb import MTKStructure, MTKVaspCalculation
from mattoolkit.distributed.backends import get_backend_environment


@app.task()
def vasp_calculation_task(task, mode='static', user_incar_settings=None):
    """ Runs a vasp calculation on given structure and mode

    Args:
        task (dict): dictionary containing key 'structure'
        mode (str): static, relax, or line (currently not supported)
        user_incar_settings (dict): User INCAR settings. This allows a user
            to override INCAR settings
    """
    user_incar_settings = user_incar_settings or {}

    structure_id = task['structure']

    # Check if calculation has been completed before
    past_calculation_id = MTKVaspCalculation.is_unique(structure_id, mode, user_incar_settings)
    if past_calculation_id:
        past_calculation = MTKVaspCalculation.get(past_calculation_id)
        return {
            'structure': past_calculation['metadata']['to_structure'],
            'calculation': past_calculation_id
        }

    structure = MTKStructure.get(structure_id)
    if isinstance(structure, TransformedStructure):
        structure = structure.final_structure

    # Gather CHGCAR from database for Non-SCF calculations
    chgcar = None
    if mode in ['line', 'uniform']:
        prev_calculation = MTKVaspCalculation.get(task['calculation'])
        if prev_calculation['metadata']['calculation'] != 'static':
            raise ValueError('Previous calculation must be static for Non-SCF calculations')
        chgcar = prev_calculation['chgcar']

    # Run VASP calculation
    cluster_config = get_cluster_config()
    backend_config = get_backend_environment()

    # very-small but extremely unlikely folder name collision
    jobdir_name = '{}-{}-{}-{}'.format(
        str(structure_id),
        backend_config['job_id'],
        mode,
        datetime.now().strftime("%Y%m%d-%H%M%S")
    )
    directory = os.path.join(cluster_config['tmp'], jobdir_name)

    vasp_cmd = ['mpirun', '-np', str(backend_config['num_cores']), cluster_config['vasp_cmd']]

    outputs = vasp_calculation(structure, directory, vasp_cmd, mode, chgcar, user_incar_settings)

    # Store VASP Calculation
    to_structure_id = structure_id
    if mode == 'relax':
        to_structure_id = MTKStructure.add(outputs['vasprun'].final_structure, metadata={
            'calculation': mode,
            'from_structure': structure_id
        })

    calculation_id = MTKVaspCalculation.add(outputs, metadata={
        'from_structure': structure_id,
        'to_structure': to_structure_id,
        'calculation': mode,
        'user_incar_settings': user_incar_settings
    })

    return {
        'structure': to_structure_id,
        'calculation': calculation_id
    }
