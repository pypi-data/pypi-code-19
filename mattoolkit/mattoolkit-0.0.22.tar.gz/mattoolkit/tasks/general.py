""" General Celery Tasks

"""

from mattoolkit.utils.celery import app
from mattoolkit.utils.mongodb import MTKStructure
from mattoolkit.io.icsd import ICSD


@app.task()
def icsd_structure_task(icsd_id):
    """ Task takes ICSD id for structure and adds to Mongo Database

    Idempotent Task

    Args:
        icsd_id (int): id provided by ICSD
    """
    crystal = ICSD.find_one(icsd_id=icsd_id)

    if crystal is None:
        raise ValueError('ICSD ID: {} does not exist'.format(icsd_id))

    structure_id = MTKStructure.add(crystal.structure, metadata={
        'icsd_id': crystal.icsd_id,
        'publication': crystal.publication,
        'cif': crystal.cif
    })

    return {
        'structure': structure_id
    }
