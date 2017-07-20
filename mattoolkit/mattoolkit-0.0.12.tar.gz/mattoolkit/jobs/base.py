import os
from pathlib import Path
import tempfile
import shutil


class BaseCalculationJob:
    KNOWN_PROGRAMS = {'mpi', 'VASP'}

    def __init__(self, calculation):
        self.calculation = calculation

        self.cluster_job = calculation.cluster_job
        self.cluster_job.get()

        self.cluster = self.cluster_job.cluster
        self.cluster.get()

        self._programs = {}
        for program in self.cluster.data['programs']:
            self._programs[program['program']] = {
                'module': program['module'],
                'command': program['command']
            }

        self.scratch_directory = self.get_scratch_directory()

    def check_program_dependencies(self, required_programs):
        for required_program in required_programs:
            if required_program not in self.KNOWN_PROGRAMS:
                raise ValueError('Program %s not known to be executable. Available (%s)' % (required_program, self.KNOWN_PROGRAMS))
            elif required_program not in self._programs:
                raise ValueError('Program %s not specified in cluster programs' % required_program)
            elif shutil.which(self._programs[required_program]['command']) is None:
                program = self._programs[required_program]
                raise ValueError('Could not find program command %s needed for calculation named %s' % (program['command'], required_program))
        print(f'Program Dependencies Satisfied: {required_programs}')

    def get_scratch_directory(self):
        scratch_directory = Path(self.cluster.data['scratch_directory']).expanduser()
        if scratch_directory.is_dir():
            return scratch_directory.absolute()
        return Path(tempfile.gettempdir()).absolute()

    @property
    def mpi_prefix(self):
        cores = self.cluster_job.cores
        if cores == 1:
            return []
        return [self._programs["mpi"]["command"], '-n', str(cores)]

    def check_environment_variables(self, env_vars):
        for env_var in env_vars:
            if not os.environ.get(env_var):
                raise ValueError(f'Environment Variable {env_var} required for execution')

    @property
    def environment(self):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()
