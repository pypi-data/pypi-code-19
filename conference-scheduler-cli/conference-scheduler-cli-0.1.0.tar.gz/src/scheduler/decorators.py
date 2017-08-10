import functools
import shutil

from scheduler import session


def uses_output_folders(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if not session.output_folders_are_clean:
            for folder in ['solution', 'build']:
                shutil.rmtree(session.folders[folder], ignore_errors=True)
                session.folders[folder].mkdir(exist_ok=True)
            session.output_folders_are_clean = True
        return func(*args, **kwargs)
    return wrapped
