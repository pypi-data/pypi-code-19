#! /usr/bin/env python

import git, logtool, shutil, tempfile
from path import Path

# https://stackoverflow.com/questions/28291909/gitpython-and-ssh-keys
# https://stackoverflow.com/questions/28803626/get-all-revisions-for-a-specific-file-in-gitpython

class GitFiles_Ctx (object):

  @logtool.log_call
  def __init__ (self, url, ssh_keyfile, prefix = "gitfiles_ctx__",
                branch = "master"):
    self.fpath = tempfile.mkdtemp (prefix = prefix)
    ssh_cmd = "ssh -i {keyfile}".format (keyfile = ssh_keyfile)
    with git.Git ().custom_environment (GIT_SSH_COMMAND = ssh_cmd):
      self.repo = git.Repo.clone_from (url, self.fpath, branch = branch)

  @logtool.log_call
  def __enter__ (self):
    return self

  @logtool.log_call (log_exc = True)
  def __exit__ (self, exc_type, exc_val, exc_tb):
    shutil.rmtree (self.fpath)

  @logtool.log_call
  def read (self, fname):
    return file (Path (self.fpath) / fname).read ()
