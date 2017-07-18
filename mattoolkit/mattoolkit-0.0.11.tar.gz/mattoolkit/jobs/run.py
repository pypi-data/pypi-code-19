import subprocess
import shutil
from tempfile import mkdtemp, mkstemp
from pathlib import Path
import time
import logging

logger = logging.getLogger(__name__)


def archived_run(command, temporary=True, format='zip', scratch_directory=None, timeout=None, shell=False, preexec_fn=None, postexec_fn=None):
    """ Runs command in a temporary directory

    process.stdout
    process.stderr
    process.returncode # return code from running command
    process/ # directory that command is run under
    """
    Path(scratch_directory).mkdir(parents=True, exist_ok=True) # Ensure that scratch_directory exists

    backup_file, backup_filename = mkstemp(suffix=f".{format}", dir=scratch_directory)
    logger.info(f'Creating backup file {backup_filename}')

    try:
        temp_directory = Path(mkdtemp(dir=scratch_directory)).absolute()
        logger.info(f'Temporary Directory ({temporary}): {temp_directory}')
        run_directory = temp_directory / 'process'
        run_directory.mkdir(parents=True, exist_ok=True)
        if preexec_fn:
            try:
                preexec_fn(run_directory)
            except Exception as e:
                logger.exception('preexec function threw error')

        logger.info(f'Running process {command} in {run_directory}')

        with (temp_directory / 'process.stdout').open('w', buffering=1) as stdout, \
             (temp_directory / 'process.stderr').open('w', buffering=1) as stderr:
            return_code = run_with_timeout(run_directory, command,
                                           timeout=timeout, shell=shell,
                                           stdout=stdout, stderr=stderr)
        with (temp_directory / 'process.returncode').open('w') as f:
            f.write(f'{return_code}')

        if postexec_fn:
            try:
                postexec_fn(run_directory)
            except Exception as e:
                logger.exception('postexec function threw error')
    finally:

        base_filename = backup_filename[:backup_filename.rfind('.')]
        archive_filename = shutil.make_archive(base_filename, 'zip', root_dir=temp_directory)
        logger.info(f'Archive of process: {archive_filename}')
        if temporary:
            shutil.rmtree(temp_directory)
        return backup_file


def run_with_timeout(run_directory, command, timeout=None, shell=False, stdout=None, stderr=None):
    """ Blocking call to run command. If given a timeout command will be sent signal SIGTERM.

    """
    try:
        process = subprocess.Popen(command, cwd=run_directory, shell=shell, stdout=stdout, stderr=stderr)
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired as error:
        logger.warning(f'Running process timeout after {timeout} seconds')
        process.terminate()
    finally:
        return_code = process.wait()
    return return_code
