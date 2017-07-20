import os
from pathlib import Path
import tempfile
import shutil
import logging


from ..run import archived_run
from ..base import BaseCalculationJob

logger = logging.getLogger(__name__)


class VaspJob(BaseCalculationJob):
    def __init__(self, calculation):
        super().__init__(calculation)
        self.check_program_dependencies({'mpi', 'VASP'})
        self.check_environment_variables({'PMG_VASP_PSP_DIR'})

    def run(self):
        vasp_command = self.mpi_prefix + ['vasp']
        backup_file = archived_run(vasp_command,
                                   scratch_directory=self.scratch_directory,
                                   preexec_fn=self.vasp_initialize_directory)
        # self.calculation.upload_results(backup_file)


    def vasp_initialize_directory(self, run_directory):
        # Write input files
        vasp_input = self.calculation.input
        vasp_input.write_input(output_dir=run_directory, make_dir_if_not_present=False)

        # VASP Calculations can depend on other VASP Calculations
        previous_calculation = self.calculation.previous_calculation
        if self.calculation.format == 'VASP' and previous_calculation:
            icharg = vasp_input['INCAR'].get('ICHARG')
            istart = vasp_input['INCAR'].get('ISTART')
            files_needed = []
            if icharg in [1, 11]: files_needed.append('CHGCAR')
            if (istart in [1, 2, 3]) or icharg == 0: files_needed.append('WAVECAR')
            # if istart == 3: files_needed.append('TEMPCAR')
            if files_needed:
                with tempfile.TemporaryDirectory() as tempdir:
                    filename = previous_calculation.download_results(tempdir)
                    shutil.unpack_archive(filename, tempdir)
                    for filename in files_needed:
                        candidates = list(Path(tempdir).glob('**/' + filename))
                        if len(candidates) == 0:
                            raise ValueError(f'cannot find file {filename} in downloaded previous calculation {previous_calculation.id}')
                        elif len(candidates) != 1:
                            raise ValueError(f'multiple files with filename {filename} in downloaded previous calculation {previous_calculation.id}')
                        shutil.copyfile(candidates[0], run_directory / filename)


def analyze_vasp_job(filename):
    if Path(filename).expanduser().is_dir():
        logger.debug(f'vasp job is directory {filename}')
        return _analyze_vasp_job(Path(filename).expanduser())
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            shutil.unpack_archive(filename, tempdir)
            logger.debug(f'vasp job is archive analyzing in temporary folder {tempdir}')
            return _analyze_vasp_job(tempdir)

def is_vasp_calculation_completed(vasprun):
    if vasprun.parameters['IBRION'] == 0 and vasprun.converged_electronic:
        # For MD calculations the ionic configuration does not converge
        return True
    elif vasprun.converged:
        return True
    return False

def _analyze_vasp_job(run_directory):
    from pymatgen.io.vasp.outputs import Vasprun, Outcar

    # Find files in directory
    vasprun_directory = list(Path(run_directory).glob('**/vasprun.xml'))
    outcar_directory = list(Path(run_directory).glob('**/OUTCAR'))

    if len(vasprun_directory) == 0:
        raise ValueError('Could not find vasprun.xml in archive')
    elif len(vasprun_directory) > 2:
        raise ValueError('Multiple vasprun.xml files found can only have one per archive: {vasp_directory}')
    logger.info(f'vasprun.xml found in {vasprun_directory[0]}')

    if len(outcar_directory) == 0:
        raise ValueError('Could not find OUTCAR in archive')
    elif len(outcar_directory) > 2:
        raise ValueError('Multiple OUTCAR files found can only have one per archive: {vasp_directory}')
    logger.info(f'outcar found in {outcar_directory[0]}')

    vasprun = Vasprun(vasprun_directory[0])
    vasprun_dict = vasprun.as_dict()
    completed = is_vasp_calculation_completed(vasprun)
    outcar = Outcar(vasprun_directory[0])
    initial_structure = vasprun_dict['input']['crystal']
    final_structure = vasprun_dict['output']['crystal']

    return {
        'completed': completed,
        'initial_structure': initial_structure,
        'final_structure': final_structure,
        'outcar': outcar.as_dict(),
        'vasprun': vasprun_dict
    }
