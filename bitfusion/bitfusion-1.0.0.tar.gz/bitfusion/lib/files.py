import os
import tarfile

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import requests

def create_tar(source_path):
  if not os.path.exists(source_path):
    raise Exception('{} does not exist'.format(source_path))

  abs_path = os.path.abspath(source_path)
  base_name = os.path.basename(os.path.normpath(abs_path))
  tar_name = base_name + '.tar.gz'

  if os.path.isdir(abs_path):
    # If it's a dir, put all the files in that dir at the top level of the tar
    tar_path = os.path.sep
  else:
    # If it's a file, make sure the file gets put in the top level by its name
    tar_path = os.path.basename(os.path.normpath(abs_path))

  with tarfile.open(tar_name, "w:gz") as tar:
    tar.add(abs_path, arcname=tar_path)

  return tar_name


def upload_to_s3(url, tar_name, callback):
  req = requests.put(url, data=open(tar_name, 'rb'))
  req.raise_for_status()
