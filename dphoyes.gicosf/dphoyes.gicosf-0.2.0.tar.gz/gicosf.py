#!/usr/bin/env python3

import os
import sys
import time
import subprocess
import libssh2
import socket
import json
import yaml
import io
import re
import functools
import shutil
import readline, getpass
import argparse, argcomplete
from paramiko import SSHConfig
import contextlib

COMMAND_NAME = 'gicosf'



class lazy_property(object):
    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value


def wait_any_key(message=None):
    if message is None:
        message = "Once done, press any key to continue..."
    subprocess.call(["bash", "-c", "read -rsp $'" +  message + "\n' -n1 key"])

def request_install(prog_name, instruction=None):
    if instruction is None:
        instruction = "Please install: " + prog_name

    print(instruction)
    wait_any_key()

def handle_not_installed(prog_name, instruction=None):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            while True:
                try:
                    return f(*args, **kwargs)
                except OSError as e:
                    if e.errno == os.errno.ENOENT:
                        # handle file not found error.
                        pass
                    else:
                        raise
                request_install(prog_name, instruction)

        return wrapper
    return decorator

def is_program_installed(prog_name):
    return True if shutil.which(prog_name) else False

def check_installed(prog_name, instruction=None):
    while not is_program_installed(prog_name):
        request_install(prog_name, instruction)

def handle_not_installed_gem(gem_name):
    return handle_not_installed(gem_name, "Please run: gem install " + gem_name)



class WebmasterSSH:
    FILE_PERM = 0o664
    DIR_PERM = 0o775

    def __init__(self, remote_host, rpath_local, rpath_remote):
        self.server       = remote_host   # Remote host
        self.rpath_local  = rpath_local   # Local root path
        self.rpath_remote = rpath_remote # Remote root path
        self.is_session_started = False

    def setVendorPath(self, vpath_rel):
        vpath_rel = vpath_rel + '/'
        self.vpath_local = os.path.join(self.rpath_local, vpath_rel)
        self.vpath_remote = os.path.join(self.rpath_remote, vpath_rel)

    @contextlib.contextmanager
    def makeSshSocket(self, host, port):
        ssh_config = SSHConfig()
        try:
            with open(os.path.expanduser("~/.ssh/config")) as f:
                ssh_config.parse(f)
        except FileNotFoundError:
            pass

        conf = ssh_config.lookup(host)
        proxycommand = conf.get('proxycommand')
        close_pforward = None
        try:
            if proxycommand:
                proxycommand = ' '.join(proxycommand.split())
                match = re.match("ssh (\S+) nc (\S+) (\d+)", proxycommand)
                if match:
                    phost, dhost, dport = match.groups()
                    port = 2222
                    host = "localhost"
                    subprocess.check_call([
                        'ssh', phost, '-N', '-f',
                        '-L', '{}:{}:{}'.format(port, dhost, dport),
                        '-M', '-S', 'gicosf_port_forward',
                    ])
                    print("Port-forward opened")
                    close_pforward = [
                        'ssh',
                        '-S',
                        'gicosf_port_forward',
                        '-O',
                        'exit',
                        phost,
                    ]
                else:
                    print("Warning: proxycommand ignored")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((host, port))
                yield sock
            finally:
                sock.close()
        finally:
            if close_pforward:
                subprocess.check_call(
                    close_pforward,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )

    @contextlib.contextmanager
    def startSession(self, username, password):
        with self.makeSshSocket(self.server, 22) as sock:
            self.session = libssh2.Session()
            try:
                self.session.startup(sock)
                print("Session started")
                self.session.userauth_password(username, password)
                print("Auth success")
                self.sftp = self.session.sftp()
                self.is_session_started = True
                yield
            finally:
                self.is_session_started = False
                self.session.disconnect()
                print("Disconnected")

    def fixSymlinks(self):
        links = subprocess.check_output(['find', self.rpath_local, '-type', 'l']).decode('utf8').split('\n')
        links = [os.path.relpath(l, self.rpath_local) for l in links if l]

        print('Making', len(links), 'symlinks')

        for l in links:
            path = os.path.join(self.rpath_remote, l)
            target = os.readlink(os.path.join(self.rpath_local, l))
            # print(path, '->', target)

            # try:
            #     remote_file_contents = self.dumpRemoteFile(path).getvalue()
            #     assert remote_file_contents == target
            # except(libssh2.Error):
            #     pass
            self.sftp.unlink(path)
            self.sftp.symlink(target, path)

    def getPackageListFromInstalledData(self, json_data):
        return {i['name']:{k:i[k] for k in ['time']} for i in json_data}

    def getLocalPackageList(self):
        with open(os.path.join(self.vpath_local, 'composer', 'installed.json')) as f:
            return self.getPackageListFromInstalledData(json.load(f))

    def dumpRemoteFile(self, file_path):
        file_size = self.sftp.get_stat(file_path)[0]
        f = self.sftp.open(file_path)
        buf = io.StringIO()
        got = 0
        while got < file_size:
            data = self.sftp.read(f, min(file_size - got, 999999))
            got += len(data)
            buf.write(data.decode('utf-8'))

        buf.seek(0)
        return buf

    def getRemotePackageList(self):
        file_path = os.path.join(self.vpath_remote, 'composer', 'installed.json')
        try:
            buf = self.dumpRemoteFile(file_path)
        except(libssh2.Error):
            return dict()
        json_data = json.load(buf)
        package_list = self.getPackageListFromInstalledData(json_data)
        return package_list

    def remoteCommand(self, command):
        channel = self.session.channel()
        channel.execute(command)
        full_str = ''
        while True:
            data = channel.read(100)
            full_str += data.decode('utf-8')
            if len(data) == 0:
                break
        print(full_str, end='')
        stat = channel.get_exit_status()
        if stat != 0:
            print(stat)
        channel.close()

    def directoryContents(self, dir):
        d = self.sftp.open_dir(dir)
        files = set()
        while True:
            file_tuple = self.sftp.read_dir(d)
            if file_tuple == None:
                break
            files.add(file_tuple[0])
        return files

    def isDirEmpty(self, dir):
        return self.directoryContents(dir) == {'.', '..'}

    def deleteFullDirectory(self, dir):
        self.remoteCommand('rm -rf '+dir)

    def deleteRemotePackage(self, package):
        package_dir = os.path.join(self.vpath_remote, package)
        self.deleteFullDirectory(package_dir)
        package_vendor_dir = os.path.dirname(package_dir)
        try:
            if self.isDirEmpty(package_vendor_dir):
                self.sftp.rmdir(package_vendor_dir)
        except(libssh2.Error):
            pass

    def uploadFile(self, local_filename, remote_filename):
        with open(local_filename, 'rb') as i_file:

            o_file = self.sftp.open(remote_filename, 'wb', self.FILE_PERM)

            while True:
                data = i_file.read(300000)
                if len(data) == 0:
                    break
                bytes_written = 0
                while True:
                    write_ret = self.sftp.write(o_file, data[bytes_written:])
                    if write_ret < 0:
                        raise Exception('Write failed')
                    bytes_written += write_ret
                    if bytes_written == len(data):
                        break

    def uploadFullDirectory(self, local_path, remote_path, verbose=True, keep_existing=False, sync_with_deletion=False):
        # Make directory
        try:
            self.sftp.mkdir(remote_path, self.DIR_PERM)
        except (libssh2.Error):
            if not sync_with_deletion:
                raise Exception("Directory already exists, won't re-upload")

        for current_dir_local, subdirs, files in os.walk(local_path):
            try:
                subdirs.remove('.git')
            except(ValueError):
                pass

            rel_path = os.path.relpath(current_dir_local, local_path)
            current_dir_remote = os.path.join(remote_path, rel_path if rel_path != '.' else '')

            if keep_existing or sync_with_deletion:
                unprocessed_remote_files = self.directoryContents(current_dir_remote) - {'.', '..'}
            else:
                unprocessed_remote_files = set()

            for sd in subdirs:
                try:
                    self.sftp.mkdir(os.path.join(current_dir_remote, sd), self.DIR_PERM)
                except libssh2.Error:
                    if not sync_with_deletion:
                        raise
                unprocessed_remote_files.discard(sd)
            for f in files:
                if keep_existing and f in unprocessed_remote_files:
                    if verbose:
                        print('Skipping upload of', os.path.join(current_dir_remote, f))
                    unprocessed_remote_files.remove(f)
                else:
                    if verbose:
                        print('Uploading', os.path.join(current_dir_remote, f))
                    self.uploadFile(os.path.join(current_dir_local, f), os.path.join(current_dir_remote, f))
                    unprocessed_remote_files.discard(f)

            if sync_with_deletion:
                for f in unprocessed_remote_files:
                    if verbose:
                        print('Deleting', os.path.join(current_dir_remote, f))
                    self.deleteFullDirectory(os.path.join(current_dir_remote, f))

    def reuploadPackage(self, package):
        self.deleteRemotePackage(package)
        [vendorname, packagename] = package.split('/')

        try:
            self.sftp.mkdir(os.path.join(self.vpath_remote, vendorname), self.DIR_PERM)
        except (libssh2.Error):
            pass

        self.uploadFullDirectory(os.path.join(self.vpath_local, package), os.path.join(self.vpath_remote, package))

    def clearCache(self, rel_path):
        cache_dir = os.path.join(self.rpath_remote, rel_path)
        print('Clearing cache', '(rm -rf '+cache_dir+')')
        self.remoteCommand('rm -rf '+cache_dir)

    def syncVendors(self, new_vendor_path):
        self.setVendorPath(new_vendor_path)

        # Derive packages lists
        local_list = self.getLocalPackageList()
        remote_list = self.getRemotePackageList()

        local_packages = set(local_list.keys())
        remote_packages = set(remote_list.keys())

        new_packages = local_packages - remote_packages
        removal_packages = remote_packages - local_packages
        update_packages = local_packages & remote_packages
        update_packages = {p for p in update_packages if local_list[p]['time'] != remote_list[p]['time']}

        # Make vendor root directory if it doesn't exist
        try:
            self.sftp.mkdir(self.vpath_remote, self.DIR_PERM)
            print('Made directory', self.vpath_remote)
            print(self.directoryContents(self.vpath_remote))

        except (libssh2.Error):
            pass

        # Remove/update/install packages
        if removal_packages:
            for idx,p in enumerate(removal_packages):
                print('Removing Package (', idx+1, '/', len(removal_packages), '): ', p, sep='')
                self.deleteRemotePackage(p)
        else:
            print("No packages to remove")

        if update_packages:
            for idx,p in enumerate(update_packages):
                print('Updating Package (', idx+1, '/', len(update_packages), '): ', p, sep='')
                self.reuploadPackage(p)
        else:
            print("No packages to update")

        if new_packages:
            for idx,p in enumerate(new_packages):
                print('Installing New Package (', idx+1, '/', len(new_packages), '): ', p, sep='')
                self.reuploadPackage(p)
        else:
            print("No new packages to install")

        # Upload all files in top-level directory
        (_, _, top_files) = next(os.walk(self.vpath_local))
        for f in top_files:
            self.uploadFile(os.path.join(self.vpath_local, f), os.path.join(self.vpath_remote, f))

        bootstrap_rel_path = ['..', 'var', 'bootstrap.php.cache']
        local_bootstrap_file = os.path.join(self.vpath_local, *bootstrap_rel_path)
        if os.path.isfile(local_bootstrap_file):
            self.uploadFile(local_bootstrap_file, os.path.join(self.vpath_remote, *bootstrap_rel_path))

        # Upload composer state directory
        # if local_list != remote_list:
        print("Updating Composer State")
        self.deleteFullDirectory(os.path.join(self.vpath_remote, 'composer'))
        self.uploadFullDirectory(os.path.join(self.vpath_local, 'composer'), os.path.join(self.vpath_remote, 'composer'), verbose=False)

    def syncWebpackBuilds(self, build_path, verbose=False):
        local_build_path  = os.path.join(self.rpath_local,  build_path)
        remote_build_path = os.path.join(self.rpath_remote, build_path)
        manifest_filename = 'manifest.json'
        keep_existing = True

        with open(os.path.join(local_build_path, manifest_filename)) as f:
            manifest = json.load(f)
        for k, v in manifest.items():
            if os.path.basename(k) == os.path.basename(v):
                keep_existing = False
                break

        if keep_existing:
            print("Uploading any new JS/CSS assets to", remote_build_path)
            if verbose:
                print('Uploading', os.path.join(remote_build_path, manifest_filename))
            self.uploadFile(os.path.join(local_build_path, manifest_filename), os.path.join(remote_build_path, manifest_filename))
        else:
            print("Uploading all JS/CSS assets to", remote_build_path)
        self.uploadFullDirectory(local_build_path, remote_build_path, verbose=verbose, keep_existing=keep_existing, sync_with_deletion=True)


class ObjectWrapperWithMethodPreHook:
    def __init__(self, inner, pre):
        self.inner = inner
        self.pre   = pre

    def __getattr__(self, attr):
        attr = getattr(self.inner, attr)
        if not callable(attr):
            raise AttributeError
        return self.MethodWrapper(method=attr, pre=self.pre)

    class MethodWrapper:
        def __init__(self, method, pre):
            self.method = method
            self.pre    = pre

        def __call__(self, *args, **kwargs):
            self.pre()
            return self.method(*args, **kwargs)


class NotUsingGitException(Exception): pass
class NotUsingComposerException(Exception): pass
class NotUsingWebpackException(Exception): pass
class CantParseWebpackOutputException(Exception): pass
class VendorDirManagedByGitException(Exception): pass
class NotUsingSymfonyException(Exception): pass


class GitComposerSftp:

    def __init__(self):
        pass

    @lazy_property
    def local_project_root_path(self):
        try:
            return subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode('utf8').splitlines()[0]
        except subprocess.CalledProcessError:
            pass
        raise NotUsingGitException()

    @lazy_property
    def local_composer_base_dir_path(self):
        return os.path.join(self.local_project_root_path, self.composer_base_dir_prefix)

    @lazy_property
    def composer_base_dir_prefix(self):
        for prefix in ['', 'Symfony/']:
            if os.path.isfile(os.path.join(self.local_project_root_path, prefix, 'composer.lock')):
                return prefix
        raise NotUsingComposerException()

    @lazy_property
    def syncable_vendor_dir(self):
        prefix = self.composer_base_dir_prefix
        autoload_file = os.path.join(self.local_project_root_path, prefix, 'vendor', 'autoload.php')

        if not os.path.isfile(autoload_file):
            raise NotUsingComposerException()

        if 0 == subprocess.run(
            ['git', 'ls-files', '--error-unmatch', autoload_file],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ).returncode:
            raise VendorDirManagedByGitException()

        return os.path.join(prefix, 'vendor')

    def get_sf_cache_path(self, environment):
        prefix = self.composer_base_dir_prefix

        try:
            abspath = subprocess.run(
                ['php', '-r', """
                    require_once __DIR__.'/vendor/autoload.php';
                    require_once __DIR__.'/app/AppKernel.php';
                    $kernel = new AppKernel('{0}', true);
                    echo $kernel->getCacheDir();
                """.format(environment)],
                cwd=prefix if prefix else None,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                check=True, encoding='utf8'
            ).stdout
        except subprocess.CalledProcessError:
            raise NotUsingSymfonyException()

        relpath = os.path.relpath(abspath, self.local_project_root_path)
        return relpath

    @lazy_property
    def dandelion_conf(self):
        fname = "dandelion.yml"
        try:
            with open(os.path.join(self.local_project_root_path, fname), 'r') as f:
                return yaml.load(f)
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                print("The project at {} has no {} file".format(self.local_project_root_path, fname))
                raise SystemExit(1)
            else:
                raise

    @lazy_property
    def remote_domain(self):
       return self.dandelion_conf['host']

    @lazy_property
    def remote_project_root_path(self):
       return self.dandelion_conf['path']

    def is_pass_initialised(self):
        return os.path.isfile(os.path.expanduser('~/.password-store/.gpg-id'))

    def is_pass_inserted(self):
        return any(self.does_pass_entry_exist(entry_name) for entry_name in self.get_candidate_pass_entry_names__length_ascending())

    def does_pass_entry_exist(self, entry_name):
        p = os.path
        return p.isfile(p.join(p.expanduser('~/.password-store'), entry_name + '.gpg'))

    def get_candidate_pass_entry_names__length_ascending(self, try_with_username=True):
        conf = self.dandelion_conf
        yield "{}/{}".format(conf["scheme"], conf["host"])
        if try_with_username:
            yield "{}/{}/{}".format(conf["scheme"], conf["host"], self.username)

    def get_candidate_pass_entry_names__length_descending(self, try_with_username=True):
        return reversed(list(self.get_candidate_pass_entry_names__length_ascending(try_with_username)))

    def get_candidate_pass_entry_names(self, try_with_username=True):
        return self.get_candidate_pass_entry_names__length_descending(try_with_username)

    @handle_not_installed('pass')
    def get_pass_creds(self, try_entry_with_username):
        try:
            return self.__get_pass_creds
        except AttributeError:
            pass

        if not self.is_pass_initialised():
            print("No stored credentials found (try running '{} pass-setup')".format(COMMAND_NAME))
            self.__get_pass_creds = None
            return self.__get_pass_creds

        for entry_name in self.get_candidate_pass_entry_names(try_with_username=try_entry_with_username):
            if self.does_pass_entry_exist(entry_name):
                lines = subprocess.check_output(['pass', entry_name]).decode('utf-8').splitlines()
                creds = {'Password': lines[0].strip()}
                for l in lines[1:]:
                    key, _, val = l.partition(':')
                    creds[key] = val.strip()
                self.__get_pass_creds = creds
                print("Found credentials in pass: {}".format(entry_name))
                return creds
        return None

    def get_dandelion_conf_field_info(self, field_name):
        conf = self.dandelion_conf

        try:
            field_val = conf[field_name]
        except KeyError:
            return None, None

        is_placeholder = re.match(r'<%=\s*ENV\[[\'\"](\w+)[\'\"]\]\s*%>', field_val)

        if is_placeholder:
            env_name = is_placeholder.group(1)
            if env_name in os.environ:
                env_val = os.environ[env_name]
                return env_val, env_name
            else:
                return None, env_name
        else:
            return field_val, None

    @lazy_property
    def dandelion_conf_username_info(self):
        return self.get_dandelion_conf_field_info('username')

    @lazy_property
    def dandelion_conf_password_info(self):
        return self.get_dandelion_conf_field_info('password')

    @lazy_property
    def username(self):
        user_val, user_env = self.dandelion_conf_username_info
        if user_val is not None:
            print("Using username from {} ({})".format('env' if user_env else 'yml', user_val))
            return user_val

        creds = self.get_pass_creds(try_entry_with_username=False)
        if creds:
            u = creds['Username']
            print("Using username from pass ({})".format(u))
            return u

        return input('Username: ')

    @lazy_property
    def password(self):
        pass_val, pass_env = self.dandelion_conf_password_info
        if pass_val is not None:
            print("Using password from {}".format('env' if pass_env else 'yml'))
            return pass_val

        creds = self.get_pass_creds(try_entry_with_username=True)
        if creds:
            print("Using password from pass")
            return creds['Password']

        return getpass.getpass('Password: ')

    @handle_not_installed_gem("dandelion")
    def dandelion(self, options):
        if any(x in options for x in ["deploy", "status", "init"]):

            user_val, user_env = self.dandelion_conf_username_info
            pass_val, pass_env = self.dandelion_conf_password_info

            if user_env and not user_val:
                os.environ[user_env] = self.username
            if pass_env and not pass_val:
                os.environ[pass_env] = self.password

        try:
            cwd = cwd=self.local_project_root_path
        except:
            cwd = None

        tried_adjusting_path = False

        while True:
            try:
                subprocess.check_call(["dandelion"] + options, cwd=cwd)
                return
            except subprocess.CalledProcessError as e:
                raise SystemExit(e.returncode)
            except OSError as e:
                if e.errno == os.errno.ENOENT and not tried_adjusting_path:
                    tried_adjusting_path = True
                    try:
                        gem_path = subprocess.check_output(['ruby', '-rubygems', '-e', 'puts Gem.user_dir'], encoding='utf8').strip()
                        gem_bin_path = os.path.join(gem_path, 'bin')
                        os.environ['PATH'] = "{}:{}".format(os.environ['PATH'], gem_bin_path)
                    except:
                        pass
                else:
                    raise

    def set_up_pass(self):
        check_installed('gpg')
        check_installed('gpg-agent')
        check_installed('pass')

        if not self.is_pass_initialised():
            print('Initialising pass')

            print('Please run: gpg --gen-key')
            while True:
                email = input('Once done, enter the email address used: ')
                try:
                    lines = subprocess.check_output(
                        ['gpg', '--list-keys', '--with-colons', email],
                        stderr=subprocess.DEVNULL
                    ).decode('utf8').split('\n')
                except subprocess.CalledProcessError:
                    continue

                uid_lines = [l for l in lines if l.startswith('uid')]
                if len(uid_lines) == 0:
                    print("No uid field found")
                    continue
                if len(uid_lines) > 1:
                    print("Multiple matches found, try being more specific")
                    continue
                break

            uid_line = uid_lines[0]
            gpg_id = uid_line.split(':')[9]
            print('Found: {}'.format(gpg_id))
            subprocess.check_call(['pass', 'init', gpg_id])
            assert self.is_pass_initialised()

        if not self.is_pass_inserted():
            u = self.username
            p = self.password
            content = "{}".format(p) + "\nUsername: {}".format(u)

            print("Choose a pass-name:")
            candidate_entry_names = list(self.get_candidate_pass_entry_names__length_ascending())
            user_val, user_env = self.dandelion_conf_username_info
            for i, entry_name in enumerate(candidate_entry_names):
                if user_val and not user_env:
                    recommended = i == len(candidate_entry_names)-1
                else:
                    recommended = i == 0

                print("{}: {}".format(i, entry_name + ('  (recommended)' if recommended else '')))
            while True:
                i = input('Your choice: ')
                try:
                    entry_name = candidate_entry_names[int(i)]
                    break
                except (IndexError, ValueError):
                    pass

            subprocess.run(
                ['pass', 'insert', '-m', entry_name],
                input=content,
                encoding='utf8',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            assert self.is_pass_inserted()
            print("To check/change the entered details, run: pass edit {}".format(entry_name))

        print('Done!')

    def do_webpack_build(self):
        print("Compiling JS/CSS assets")
        try:
            lines = subprocess.check_output(
                ['./node_modules/.bin/encore', 'production'],
                cwd=self.local_composer_base_dir_path,
                encoding='utf8'
            ).split('\n')
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                # handle file not found error.
                raise NotUsingWebpackException()
            else:
                raise

        for l in reversed(lines):
            match = re.search(r'written to (\S+)', l)
            if match:
                build_dir = match.group(1)
                return build_dir
        else:
            raise CantParseWebpackOutputException()

    @contextlib.contextmanager
    def setup_ssh_session(self):
        if hasattr(self, '_ssh_exit_stack'):
            yield
        else:
            try:
                with contextlib.ExitStack() as self._ssh_exit_stack:
                    yield
            finally:
                del self._ssh_exit_stack
                with contextlib.suppress(AttributeError):
                    del self.ssh_session

    def with_ssh_session(f):
        @functools.wraps(f)
        def f_with_setup(self, *args, **kwargs):
            with self.setup_ssh_session():
                return f(self, *args, **kwargs)
        return f_with_setup

    def start_ssh_session(self):
        if not self._ssh_session_to_start.is_session_started:
            exit_stack = self._ssh_exit_stack
            exit_stack.enter_context(self._ssh_session_to_start.startSession(self.username, self.password))

    @lazy_property
    def ssh_session(self):
        ws = WebmasterSSH(
            remote_host=self.remote_domain,
            rpath_local=self.local_project_root_path,
            rpath_remote=self.remote_project_root_path
        )
        self._ssh_session_to_start = ws
        return ObjectWrapperWithMethodPreHook(ws, self.start_ssh_session)

    @with_ssh_session
    def deploy(self):
        self.dandelion(['deploy'])
        with contextlib.suppress(NotUsingComposerException, VendorDirManagedByGitException):
            self.sf_vendor_sync()
        with contextlib.suppress(NotUsingWebpackException):
            self.sf_webpack_deploy()
        with contextlib.suppress(NotUsingComposerException, NotUsingSymfonyException):
            self.sf_cache_clear()

    @with_ssh_session
    def sf_vendor_sync(self):
        self.ssh_session.syncVendors(self.syncable_vendor_dir)

    @with_ssh_session
    def sf_webpack_deploy(self, verbose=False):
        build_dir = self.do_webpack_build()
        build_dir = os.path.join(self.composer_base_dir_prefix, build_dir)
        self.ssh_session.syncWebpackBuilds(build_dir, verbose=verbose)

    @with_ssh_session
    def sf_cache_clear(self, environments=[]):
        if not environments:
            environments = ['prod']
        for e in environments:
            path = self.get_sf_cache_path(e)
            self.ssh_session.clearCache(path)

    def main(self):

        parser = argparse.ArgumentParser(prog=COMMAND_NAME)

        subparsers = parser.add_subparsers()

        subparsers.add_parser('deploy').set_defaults(func=self.deploy)
        subparsers.add_parser('pass-setup').set_defaults(func=self.set_up_pass)

        subparsers.add_parser('sf-vendor-sync').set_defaults(func=self.sf_vendor_sync)

        p = subparsers.add_parser('sf-webpack-deploy')
        p.set_defaults(func=self.sf_webpack_deploy)
        p.add_argument('-v', '--verbose', action='store_true')

        p = subparsers.add_parser('sf-cache-clear')
        p.set_defaults(func=self.sf_cache_clear)
        p.add_argument('environments', nargs='*')

        p = subparsers.add_parser('dandelion')
        p.set_defaults(func=self.dandelion)
        p.add_argument('options', nargs='*')

        argcomplete.autocomplete(parser)
        args = parser.parse_args().__dict__
        try:
            func = args.pop('func')
        except KeyError:
            parser.print_help()
            raise SystemExit(1)

        try:
            func(**args)
        except KeyboardInterrupt:
            raise SystemExit(0)


def main():
    w = GitComposerSftp()
    w.main()


if __name__ == "__main__":
    main()
