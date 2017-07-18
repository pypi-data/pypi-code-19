from .software import VaspJob


def run_calculation(uuid):
    from ..api import CalculationResourceItem

    calculation = CalculationResourceItem(uuid)
    calculation.get()

    calculation_map = {
        'VASP': VaspJob
    }

    if calculation_map.get(calculation.format):
        job = calculation_map[calculation.format](calculation)
        job.run()
    else:
        raise ValueError('No job runner for format', calculation.format)
