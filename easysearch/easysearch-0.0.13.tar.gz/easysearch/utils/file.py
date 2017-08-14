import os
import tempfile


def get_file_name(job_id, folder_name, file_name):
    tempdir = tempfile.gettempdir()
    dir = os.path.join(tempdir, 'easysearch', folder_name)
    if not os.path.exists(dir):
        os.makedirs(dir)
    return os.path.join(dir, job_id + file_name)
