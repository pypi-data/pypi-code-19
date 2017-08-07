#
# function that return the backup commands
# only with prefix backup_ in name        
#

import os
import sys
import re
import argparse
import time
import datetime
from subprocess import Popen, PIPE, call
import shutil
import tempfile
import logging

logging.basicConfig(format='%(levelname)s:%(name)s:line %(lineno)s: %(message)s')
log = logging.getLogger(__name__)

try:
    from rsbactools import rsbac, RSBAC_PROC_INFO_DIR
except ImportError as error:
    sys.exit(error)


# timestamp
TIMESTAMP = str("%0.f" % datetime.datetime.now().timestamp())

# default backup directory
BACKUP_DIRECTORY = os.path.join(os.getcwd(), "backup")
BACKUP_DIRECTORY_TODAY = os.path.join(
     str(datetime.datetime.now().year),
     str(datetime.datetime.now().month),
     str(datetime.datetime.now().day)
)
BACKUP_SHM = "/dev/shm/backup"

# BACKUP_MODULES contains module names which have no entry in 
# /proc/rsbac-info/active or similar
BACKUP_MODULES = ["general", "net", "log"]

# BACKUP_MODULES_EXCLUDE contains module names which are not backup.
#   e.g. JAIL is only process based
BACKUP_MODULES_EXCLUDE = ["JAIL"]

# directories which exclude
DIRECTORIES_EXCLUDE = ["/rsbac.dat", "/proc", "/sys"]

# buffer size for Popen and or open
BUFFER_SIZE = 4096


# command function must return a list 
def command_log():
    cmd = [
        ["switch_adf_log", "-b"]
    ]
    return cmd

def command_net():
    return [
        ["net_temp", "-a", "-b"],
        ["attr_back_net", "-a", "NETDEV"],
        ["attr_back_net", "-a", "NETTEMP"]
    ]

def command_mac():
    return [
        ["mac_back_trusted", "-r", "/"],
        ["attr_back_user", "-a", "-M", "MAC"]
    ]

def command_auth():
    return [
        ["auth_back_cap", "-r", "/"],
        ["attr_back_user", "-a", "-M", "AUTH"]
    ]

def command_cap():
    cmd = [
        ["attr_back_user", "-a", "-M", "CAP"]
    ]
    return cmd

def command_rc():
    return [
        ["rc_get_item", "backup"],
        ["attr", "-a", "-M", "RC"]
    ]

def command_acl():
    acl_tlist_all = call(["acl_tlist", "-n"])
    all_temp = call(["net_temp", "list_temp_nr"])
    cmd = [
        ["acl_tlist", "-br", "FD", ":DEFAULT:", "/"],
        ["acl_tlist", "-b", "DEV", ":DEFAULT:"],
        ["acl_tlist", "-Db"],
        ["acl_tlist", "-br", "IPC", ":DEFAULT:"],
        ["acl_tlist", "-br", "SCD", ":DEFAULT:", acl_tlist_all],
        ["acl_tlist", "-ab"],
        ["acl_tlist", "-br", "PROCESS", ":DEFAULT:"],
        ["acl_tlist", "-br", "NETDEV", ":DEFAULT:"],
        ["acl_tlist", "-br", "NETTEMP_NT", ":DEFAULT:", all_temp],
        ["acl_tlist", "-br", "NETTEMP", all_temp],
        ["acl_tlist", "-br", "NETOBJ", ":DEFAULT:"],
        ["acl_mask", "-br", "FD", "/"],
        ["acl_mask", "-Db"],
        ["acl_mask", "-ab"],
        ["acl_mask", "-b", "SCD", acl_tlist_all]
        ["acl_group", "-gb", "list_groups"]
    ]
    process1 = Popen(["acl_group", "-gs", "list_groups"], stdout=PIPE, 
            stderr=PIPE)
    process2 = Popen(["cut", "-f", "1", "-d", " "], stdin=process1.stdout, 
            stdout=PIPE, stderr=PIPE)
    groups, error = process2.communictate()
    if groups != "":
        for group in groups:
            cmd.append(["acl_group", "-b", "get_group_members", group])
    return cmd

def command_general():
    cmd = []
    for module, status in rsbac.Rsbac().get_modules()["Module"].items():
        if module in BACKUP_MODULES_EXCLUDE:
            continue
        if status == "on":
            cmd.append(["attr_back_dev", "-b"])
    return cmd

def command_um():
    return [
        ["rsbac_groupshow", "-S", "all", "-b", "-p", "-a"],
        ["rsbac_usershow", "-S", "all", "-b", "-p", "-a"]
    ]
    
def command_res():
    #cmd = [attr_get_user RES 4294967292 res_min]
    cmd = [
        ["attr_back_fd", "-r", "-M", "RES", "/"],
        ["attr_back_user", "-a", "-M", "RES"]
    ]
    return cmd

def command_pax():
    cmd = [
        ["attr_back_fd", "-r", "-M", "PAX", "/"],
        ["attr_back_user", "-a", "-M", "PAX"]
    ]
    return cmd

def command_gen():
    cmd = [
        ["attr_back_fd", "-r", "-M", "GEN", "/"],
        ["attr_back_user", "-a", "-M", ""]
    ]
    return cmd

def get_directories(directory="/"):
    directories = os.listdir(directory)
    #for i i

def command(module, directory=["/"]):
    cmd = [
        ["attr_back_fd", "-r", "-M", module, directory],
        ["attr_back_user", "-a", "-M", module]
    ]
    return cmd


class Backup(object):
    """Backup RSABAC attribute modules based."""

    def __init__(self):
        self.args = {}
        self.shm_dir = None

    def set_args(self, args):
        self.args = args

    def set_log_level(self, log_level):
        log.setLevel(log_level)

    def get_log_level(self):
        return log.getEffectiveLevel()

    def modules_to_backup(self):
        """Get available modules and extend the module list."""
        modules = BACKUP_MODULES
        try:
            for module, status in rsbac.Rsbac().get_modules()["Module"].items():
                if status == "on" and module not in BACKUP_MODULES_EXCLUDE:
                    modules.append(module.lower())
            if os.path.exists(os.path.join(RSBAC_PROC_INFO_DIR, "stats_um")):
                modules.append("um")
        except Exception as error:
             log.error(error)
        return modules

    def execute(self, backup_dir, module):
        """Execute the module command and write to different files the result.
            The name are build: 
                backup_timestamp.sh
                command_timestamp.sh
                error_timestamp.txt
        """
        # build function name and call the function to get the shell commands
        cmd = globals()["_".join(["command", module])]()

        # build names for writing outupt 
        backup = os.path.join(backup_dir, 
                "backup_" + TIMESTAMP + ".sh")
        error = os.path.join(backup_dir, 
                "error_" + TIMESTAMP + ".txt")
        command = os.path.join(backup_dir, 
                "command_" + TIMESTAMP + ".sh")
       
        try:
            with open(backup, "w", buffering=BUFFER_SIZE) as backup_fd, \
                    open(error, "w", buffering=BUFFER_SIZE) as error_fd, \
                    open(command, "w", buffering=BUFFER_SIZE) as command_fd:
                for i in cmd:
                    command_fd.write(" ".join([str(x) for x in i]) + "\n")
                    process = Popen(i, bufsize=BUFFER_SIZE, stdin=PIPE, 
                            stdout=backup_fd, stderr=error_fd)
                    process.wait()
        except IOError as error:
            log.error(error)
   
    def check_shm(self):
        if not os.path.isdir("/dev/shm"):
            log.error("/dev/shm is not mounted")
            return False
        user = os.environ.get("USER")
        if len(user) == 0:
            log.error("could not found a valid user")
            return False
        try:
            path = os.path.join("/dev/shm", user)
            if not os.path.isdir(path):
                log.info("create %s" % path)
                os.mkdir(path)
            self.shm_dir = path
            return True
        except OSError as error:
            log.error(error)
            return False

    def get_backup_dir(self):
        backup_dir = os.path.join(self.args.get("backup_directory", 
                BACKUP_DIRECTORY), BACKUP_DIRECTORY_TODAY)
        try:
            if not os.path.isdir(backup_dir):
                os.makedirs(backup_dir)
            log.info("backup_dir is %s" % backup_dir)
            return backup_dir
        except OSError as error:
            log.error(error)
            return False

    def copy_files(self, src_dir, dst_dir):
        files = os.listdir(src_dir)
        if len(files) == 0:
            log.error("no files found to copy")
            return False
        for file in files:
            try:
                src_file = os.path.join(src_dir, file)
                dst_file = os.path.join(dst_dir, file)
                log.info("copy %s to backup_dir" % src_file)
                shutil.copy(src_file, dst_file)
            except OSError as error:
                log.error(error)
                return False
        return True

    def run(self):
        backup_dir = self.get_backup_dir()
        if not self.check_shm():
            log.error("do: mount -t tmpfs none /dev/shm")
            return False
        with tempfile.TemporaryDirectory(dir=self.shm_dir) as tmp_dir:
            log.info("create %s" % tmp_dir)
            os.chmod(tmp_dir, 0o700)
            for module in self.modules_to_backup():
                if self.args.get("full", False) is False:
                    if module in self.args:
                        continue
                try:
                    log.info("starting backup: %s" % module)
                    module_dir = os.path.join(tmp_dir, module)
                    if not os.path.isdir(module_dir):
                        log.info("create %s" % module_dir)
                        os.mkdir(module_dir)
                    backup_module_dir = os.path.join(backup_dir, module)
                    if not os.path.isdir(backup_module_dir):
                        log.info("create %s" % backup_module_dir)
                        os.mkdir(backup_module_dir)
                    self.execute(module_dir, module)
                    self.copy_files(module_dir, backup_module_dir)
                except KeyError as error:
                    log.error(error)
                    log.info("Not implemented: %s()" % module)
                except OSError as error:
                    log.info(error)
        return True


class BackupNg(object):

    def __init__(self):
        self.args = {}
        self.shm_dir = None
        self.files_dirs = []
        self.dirs = ["/bin", "/etc/", "/lib", "/lib64", "/sbin", "/usr", "/opt"]

    def set_args(self, args):
        self.args = args

    def set_log_level(self, log_level):
        log.setLevel(log_level)

    def get_log_level(self):
        return log.getEffectiveLevel()

    def modules_to_backup(self):
        """Get available modules and extend the module list."""
        modules = BACKUP_MODULES
        try:
            for module, status in rsbac.Rsbac().get_modules()["Module"].items():
                if status == "on" and module not in BACKUP_MODULES_EXCLUDE:
                    modules.append(module.lower())
            if os.path.exists(os.path.join(RSBAC_PROC_INFO_DIR, "stats_um")):
                modules.append("um")
        except Exception as error:
             log.error(error)
        return modules

    def run(self):
        from queue import Queue
        from threading import Thread

        def do_it():
            pass

        def worker():
            item = q.get()
            do_work(item)
            q.task_done()

        q = Queue()
        num_worker_threads = 3
        for i in range(num_worker_threads):
                t = Thread(target=worker)
                t.daemon = True
                t.start()

        for item in source():
                q.put(item)

        q.join()       # block until all tasks are done

        if not self.get_files_dirs():
            return False
        for module in self.modules_to_backup():
            print(module)

        print(len(self.files_dirs))
        

    def get_files_dirs(self):
        try:
            for i in self.dirs:
                for j in os.listdir(i):
                    self.files_dirs.append(os.path.join(i, j))
            return True
        except OSError as error:
            log.error(error)



if __name__ == "__main__":
    # 0.009 sec to collect all give files_dirs 
    start_time = datetime.datetime.now().timestamp()
    b = BackupNg()
    b.set_log_level(logging.DEBUG)
    b.run()
    end_time = datetime.datetime.now().timestamp()
    result_time = end_time - start_time
    print(result_time)
    #print(str("%0.10f" % result_time))
