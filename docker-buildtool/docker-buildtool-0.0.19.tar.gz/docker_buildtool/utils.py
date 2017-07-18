import logging
import os
import pipes
import six
import subprocess
import tempfile
import time

from docker_buildtool import error

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

def pretty_command(command):
    if isinstance(command, six.string_types):
        return command
    else:
        return ' '.join(pipes.quote(c) for c in command)

class FakeFile(object):
    def __init__(self, dir):
        self.name = os.path.join(dir, '<tmppath>')

    def close(self):
        pass

def named_temporary_file(dryrun, dir=None):
    if dryrun:
        return FakeFile(dir)
    else:
        return tempfile.NamedTemporaryFile(dir=dir)

def popen(dryrun, cmd, *args, **kwargs):
    if dryrun:
        logger.info('Would start subprocess: %s (args=%s kwargs=%s)', cmd, args, kwargs)
    else:
        logger.info('Starting subprocess: %s (args=%s kwargs=%s)', cmd, args, kwargs)
        return subprocess.Popen(cmd, *args, **kwargs)

def execute_command(dryrun, cmd, cleanup_timeout=None, **kwargs):
    if dryrun:
        logger.info('Would execute: %s (kwargs=%s)', cmd, kwargs)
    else:
        logger.info('Executing: %s (kwargs=%s)', ' '.join(cmd), kwargs)
        proc = subprocess.Popen(cmd, **kwargs)
        try:
            proc.wait()
        except:
            if cleanup_timeout is None:
                raise
            proc.terminate()
            # No wait(timeout) on Python 2.7
            start = time.time()

            while time.time() < start + cleanup_timeout:
                ret = proc.poll()
                if ret is not None:
                    return
                time.sleep(0.1)

            # Finally, just hammer it.
            proc.kill()
            proc.wait()
        else:
            if proc.returncode != 0:
                raise error.Error('Command {} exited with non-zero status {}'.format(pretty_command(cmd), proc.returncode))

def rename(dryrun, src, dst):
    if dryrun:
        logger.info('Would move: %s -> %s', src, dst)
    else:
        logger.info('Moving: %s -> %s', src, dst)
        os.rename(src, dst)

def unlink(dryrun, target):
    if dryrun:
        logger.info('Would remove: %s', target)
    else:
        logger.info('Removing: %s', target)
        os.unlink(target)

def write(dryrun, target, contents):
    if dryrun:
        logger.info('Would write to %s:\n  %s', target, contents.replace('\n', '\n  '))
    else:
        logger.info('Writing to: %s', target)
        with open(target, 'w') as f:
            f.write(contents)

def makedirs(dryrun, directory):
    if dryrun:
        logger.info('Would have created directory %s', directory)
    else:
        os.makedirs(directory)
