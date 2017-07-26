from .software import VaspJob


def run_calculation(uuid, mode='full', temporary=True, cores=-1):
    from ..api import CalculationResourceItem

    calculation = CalculationResourceItem(uuid)
    calculation.get()

    calculation_map = {
        'VASP': VaspJob
    }

    if calculation_map.get(calculation.format):
        job = calculation_map[calculation.format](calculation, mode=mode, temporary=temporary)
        if mode == 'validate':
            return
        job.run(cores=cores)
    else:
        raise ValueError('No job runner for format', calculation.format)
