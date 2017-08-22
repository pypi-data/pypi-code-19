
import os, logging, tempfile
from os.path import basename, exists, join
from collections import namedtuple

from .clientcnxn import ClientConnection
from .protocol import hash_file

__all__ = ['Client', 'File', 'Template']

logger = logging.getLogger('pepperssh')

Stat = namedtuple('Stat', 'exists isdir isfile size hash')


class Client:
    """
    Creates an SSH connection to a remote host and allows Python scripts to be
    sent and executed.

    To run a script remotely, call `script(filename)`.  This will execute the
    module and return a proxy to it.  The proxy allows you to call functions in
    the script remotely:

        script = client.script('setupdb.py')
        result = script.createdb(name='test')

    Parameters sent to the proxied function and its return value are pickled,
    so many Python objects can be used.  Since all exception classes may not be
    available on the local machine, exceptions are returned as string
    tracebacks and a RuntimeError is raised.

    Anything printed to the screen by the remote function is printed on the
    screen locally.

    Bi-directional input is not supported, so remote functions must not call
    functions like getpass().

    By default, the client stops waiting for remote function calls after 2
    minutes and disconnects.  The current command will stay running (it is not
    forcefully terminated) but will exit when the command is complete.  To
    override this default, use the function proxy's `settimeout` method:

        script.createdb.timeout = 5 * 60
        script.createdb('test')
    """
    def __init__(self, host):
        """
        Begins the connection to the remote host and starts up a server on it
        to accept commands from this client.
        """
        self.host = host
        self.cnxn = ClientConnection(host)
        self.cnxn.connect()

    def script(self, filename, timeout=10.0):
        """
        Sends the file to the remote host and returns a proxy to it.

        The file is loaded and executed on the remote host from a temporary
        working directory.  Any output printed to the screen is printed on the
        screen locally.
        """
        proxy = FileProxy(self, filename)

        sftp = self.cnxn.sshclient.open_sftp()
        rname = join(self.cnxn.rpath, basename(filename))
        logger.debug('copying %s --> %s', filename, rname)
        sftp.put(filename, rname)

        self.cnxn.send_command({
            'msgtype': 'script',
            'modulename': proxy._modulename,
            'filename': rname
        }, timeout=timeout)

        return proxy

    def _call(self, modulename, funcname, args, kwargs, *, timeout):
        # This isn't terribly efficient, but I'm trying to get something
        # working right now.  Convert args from a tuple to a list so we can
        # replace entries.
        assert isinstance(args, tuple)
        args = list(args)

        self._copy_call_files(args, kwargs)

        return self.cnxn.send_command({
            'msgtype': 'call',
            'mname': modulename,
            'fname': funcname,
            'args': args,
            'kwargs': kwargs
        }, timeout=timeout)

    def _get_cache_dir(self, sftp):
        DIR = '.peppercache'

        stat = self._stat(DIR)
        if not stat:
            sftp.mkdir(DIR)

        return DIR

    def _stat(self, filename):
        """
        Returns statistics about a remote file or directory, siliar to os.stat.
        """
        msg = self.cnxn.send_command({
            'msgtype': 'stat',
            'filename': filename
        }, timeout=5)
        return Stat(*(msg.get(field) for field in Stat._fields))

    def _copy_call_files(self, args, kwargs):
        """
        If there are any File instances in the arguments, transfer the file to
        the working directory and replace the argument with the remote
        filename.
        """
        sftp = None

        remotedir = None

        def _copyfile(rf):
            nonlocal sftp, remotedir

            # TODO: Eliminate get_cache_dir and move to bootstrap.
            if not sftp:
                sftp = self.cnxn.sshclient.open_sftp()
                remotedir = self._get_cache_dir(sftp)

            lname = rf.filename
            rname = join(remotedir, basename(lname))

            stat = self._stat(rname)

            if stat and stat.isfile:
                hash = hash_file(lname)
                if hash == stat.hash:
                    logger.debug('Using cached file %s', rname)
                    return rname

            logger.debug('copying %s --> %s', lname, rname)
            sftp.put(lname, rname)

            return rname

        for i, arg in enumerate(args[:]):
            if isinstance(arg, File):
                args[i] = _copyfile(arg)

        for key, val in kwargs.copy().items():
            if isinstance(val, File):
                kwargs[key] = _copyfile(val)


class File:
    """
    Used to pass a local file to a remote function.

    If you pass a instance of File to a remote function, the file will be
    transferred to a temporary work directory on the remote host and the
    argument will be replaced with the remote filename.  The remote function
    receives only a string that is the fully qualified path to the file on the
    remote host.
    """
    def __init__(self, filename):
        """
        filename
          The local file to the path to send.
        """
        if not exists(filename):
            raise FileNotFoundError(filename)
        self.filename = filename

    def __repr__(self):
        return self.filename


class Template(File):
    """
    A subclass of File that first performs substitution using `str.format`.

    A local, temporary copy of the file is made after substitution and the copy
    is sent to the remote host.
    """
    def __init__(self, filename, vars):
        """
        filename
          The local file to the path to send.

        vars
          Values to substitute in the template.  This value is passed to
          `str.format` and is usually a dictionary.

          For convenience, namedtuples are passed as dictionaries in addition
          to be being passed as a tuple.  This allows fields in the tuple to be
          accessed by position ("{0}") but also by name ("{user}") which is
          considerably easier to maintain.
        """
        # I can't read from a NamedTemporaryFile after writing to it on macOS, so I'm leaving
        # it open for now.
        args = ()
        if hasattr(vars, '_asdict'):
            args = vars
            vars = vars._asdict()
        if not isinstance(vars, dict):
            raise TypeError('vars must be a dict or namedtuple')

        self.tempfile = tempfile.NamedTemporaryFile(delete=False)
        text = open(filename).read()
        text = text.format(*args, **vars)
        self.tempfile.write(text.encode('utf-8'))
        self.tempfile.close()

        File.__init__(self, self.tempfile.name)

    def __del__(self):
        os.unlink(self.tempfile.name)

    def __repr__(self):
        return 'Template(%s)' % self.filename


class FileProxy:
    """
    Represents a Python script sent to the remote server.

    Functions in the script are accessible by name: `proxy.func()`

    Only functions are supported.  Do not try to access remote variables -
    pepperssh will try to call the value as a function on the remote host.
    """
    def __init__(self, client, filename):
        mn = basename(filename)
        if mn.endswith('.py'):
            mn = mn[:-3]

        self._client = client
        self._filename = filename
        self._modulename = mn

    def __getattr__(self, name):
        proxy = FunctionProxy(self, name)
        setattr(self, name, proxy)
        return proxy


class FunctionProxy:
    """
    Represents a function in a remote script.

    Instances of these are returned for any unknown attribute accessed on the
    remote script: `x = remote.xyz()`.  Calling this object as a function sends
    an RPC request to the server and returns its response.
    """
    def __init__(self, fproxy, name):
        self.fproxy = fproxy
        self.name   = name
        self.timeout = 60.0 * 2  # two minutes (in seconds)

    def __call__(self, *args, **kwargs):
        msg = self.fproxy._client._call(
            self.fproxy._modulename,
            self.name, args, kwargs,
            timeout=self.timeout)
        return msg.get('result')
