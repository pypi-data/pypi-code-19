import os
from pathlib import Path
import tempfile
import shutil
import logging


from ..run import archived_run
from ..base import BaseCalculationJob


logger = logging.getLogger(__name__)


class VaspJob(BaseCalculationJob):
    def __init__(self, calculation, mode='full', temporary=True):
        """ Modes: ['validate', 'initialize', 'run', 'full']

        """
        super().__init__(calculation, mode=mode, temporary=temporary)
        self.check_program_dependencies({'mpi', 'VASP'})
        self.check_environment_variables({'PMG_VASP_PSP_DIR'})

    def run(self, cores=-1):
        vasp_command = self.mpi_prefix(cores=cores) + ['vasp']
        logger.info(f'Vasp command: {vasp_command}')

        backup_file = archived_run(vasp_command,
                                   temporary=self.temporary,
                                   scratch_directory=self.scratch_directory,
                                   preexec_fn=self.vasp_initialize_directory,
                                   initialize_only=(self.mode == 'initialize'))
        if self.mode in ['initialize', 'run']:
            return backup_file
        self.calculation.upload_results(backup_file)
        return backup_file


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
                logger.info(f'files needed from previous Vasp Calculation {files_needed}')
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
        self.calculation.notify_running(run_directory)


def analyze_vasp_job(filename, format='zip'):
    if Path(filename).expanduser().is_dir():
        logger.debug(f'vasp job is directory {filename}')
        return _analyze_vasp_job(Path(filename).expanduser())
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            shutil.unpack_archive(str(filename), tempdir, format=format)
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
    from pymatgen.io.vasp import Vasprun, Outcar, Potcar, Kpoints
    from ...api.calculation import to_kpoints_schema, to_potcar_schema

    # Find files in directory
    vasprun_directory = list(Path(run_directory).glob('**/vasprun.xml'))
    outcar_directory = list(Path(run_directory).glob('**/OUTCAR'))
    potcar_directory = list(Path(run_directory).glob('**/POTCAR'))
    kpoints_directory = list(Path(run_directory).glob('**/KPOINTS'))

    # Cannot trust vasprun.xml for kpoints and potcar
    if len(vasprun_directory) == 0:
        raise ValueError('Could not find vasprun.xml in archive')
    elif len(vasprun_directory) > 2:
        raise ValueError('Multiple vasprun.xml files found can only have one per archive: {vasp_directory}')
    logger.info(f'vasprun.xml found in {vasprun_directory[0]}')

    if len(outcar_directory) == 0:
        raise ValueError('Could not find OUTCAR in archive')
    elif len(outcar_directory) > 2:
        raise ValueError('Multiple OUTCAR files found can only have one per archive: {vasp_directory}')
    logger.info(f'OUTCAR found in {outcar_directory[0]}')

    if len(potcar_directory) == 0:
        raise ValueError('Could not find POTCAR in archive')
    elif len(potcar_directory) > 2:
        raise ValueError('Multiple POTCAR files found can only have one per archive: {vasp_directory}')
    logger.info(f'POTCAR found in {potcar_directory[0]}')

    if len(kpoints_directory) == 0:
        raise ValueError('Could not find KPOINTS in archive')
    elif len(kpoints_directory) > 2:
        raise ValueError('Multiple KPOINTS files found can only have one per archive: {vasp_directory}')
    logger.info(f'KPOINTS found in {vasprun_directory[0]}')

    vasprun = Vasprun(vasprun_directory[0])
    vasprun_dict = vasprun.as_dict()
    completed = is_vasp_calculation_completed(vasprun)
    outcar = Outcar(outcar_directory[0])
    potcar = Potcar.from_file(potcar_directory[0])
    kpoints = Kpoints.from_file(kpoints_directory[0])

    inputs = {
        'template': 'none',
        'incar': vasprun_dict['input']['incar'],
        'potcar': to_potcar_schema(potcar),
        'kpoints': to_kpoints_schema(kpoints)
    }

    return {
        'completed': completed,
        'initial_structure': vasprun.initial_structure,
        'final_structure': vasprun.final_structure,
        'outcar': outcar,
        'inputs': inputs,
        'vasprun': vasprun
    }
