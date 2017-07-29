import os
import errno
import cffi

SFD_NONBLOCK = 0o00004000
SFD_CLOEXEC = 0o02000000

SIG_BLOCK = 0
SIG_UNBLOCK = 1
SIG_SETMASK = 2

ffi = None
crt = None


def init():
    global ffi, crt
    ffi = cffi.FFI()
    crt = ffi.dlopen(None)
    ffi.cdef('''
        typedef unsigned int uint32_t;
        typedef int int32_t;
        typedef unsigned long int uint64_t;
        typedef unsigned char uint8_t;
        typedef struct {
            unsigned long int __val[%d];
            } sigset_t;
        int sigemptyset(sigset_t *set);
        int sigfillset(sigset_t *set);
        int sigaddset(sigset_t *set, int signum);
        int sigdelset(sigset_t *set, int signum);
        int sigismember(const sigset_t *set, int signum);
        int sigprocmask(int how, const sigset_t *set, sigset_t *oldset);
        struct signalfd_siginfo {
            uint32_t ssi_signo; /* Signal number */
            int32_t ssi_errno; /* Error number (unused) */
            int32_t ssi_code; /* Signal code */
            uint32_t ssi_pid; /* PID of sender */
            uint32_t ssi_uid; /* Real UID of sender */
            int32_t ssi_fd; /* File descriptor (SIGIO) */
            uint32_t ssi_tid; /* Kernel timer ID (POSIX timers)
            uint32_t ssi_band; /* Band event (SIGIO) */
            uint32_t ssi_overrun; /* POSIX timer overrun count */
            uint32_t ssi_trapno; /* Trap number that caused signal */
            int32_t ssi_status; /* Exit status or signal (SIGCHLD) */
            int32_t ssi_int; /* Integer sent by sigqueue(3) */
            uint64_t ssi_ptr; /* Pointer sent by sigqueue(3) */
            uint64_t ssi_utime; /* User CPU time consumed (SIGCHLD) */
            uint64_t ssi_stime; /* System CPU time consumed (SIGCHLD) */
            uint64_t ssi_addr; /* Address that generated signal (for hardware-generated signals) */
            uint8_t pad[48]; /* Pad size to 128 bytes (allow for additional fields in the future) */
        };
        int signalfd(int fd, const sigset_t *mask, int flags);
    ''' % (1024 / (8 * ffi.sizeof('unsigned long int'))))


init()


class SigSet(object):
    """
        This is a thin wrapper over sigsetops(3)
    """

    def __init__(self, signals=None):
        self.sigset = ffi.new('sigset_t *')
        self.empty()
        if signals is not None:
            self.sigset = signals

    '''Initialize the signal set to empty'''

    def empty(self):
        crt.sigemptyset(self.sigset)

    '''Initialize the signal set to full, including all signals'''

    def fill(self):
        crt.sigfillset(self.sigset)

    '''Add the specified signal to the signal set'''

    def add(self, sig):
        crt.sigaddset(self.sigset, sig)

    '''Remove the specified signal from the signal set'''

    def remove(self, sig):
        crt.sigdelset(self.sigset, sig)

    '''Test if the specified signal is a member of the signal set'''

    def ismember(self, sig):
        return crt.sigismember(self.sigset, sig) == 1

    def get_sigs(self):
        for i in range(0, 32):
            if self.ismember(i):
                yield i

    def get_set(self):
        s = set()
        for i in range(0, 32):
            if self.ismember(i):
                s.add(i)
        return s


'''
    Examine and change blocked signals
    - `signals` is a sigset object.
    - `mode` controls how sigprocmask() interprets the signal mask (see
    below)
'''


def sigprocmask(signals, mode=SIG_SETMASK):
    if mode not in [SIG_BLOCK, SIG_UNBLOCK, SIG_SETMASK]:
        raise ValueError('invalid mode')
    old_signals = ffi.new('sigset_t *')
    res = crt.sigprocmask(mode, signals.sigset, old_signals)
    if res == -1:
        tmp_errno = ffi.errno
        std_errno = errno.errorcode[tmp_errno]
        raise OSError(std_errno, os.strerror(tmp_errno))
    return SigSet(old_signals)


class sigfd(object):
    """
        signalfd(signal_set, [flags]) -> signalfd object
        Create a signalfd object for receiving the set of signals specified as
        a sigset object.
    """

    def __init__(self, signals, flags=None):
        if flags is None:
            self.flags = SFD_NONBLOCK
        else:
            self.flags = flags

        self.signals = signals
        self.fd = crt.signalfd(-1, self.signals.sigset, self.flags)
        if self.fd == -1:
            myerrno = ffi.errno
            stderrno = errno.errorcode[myerrno]
            raise OSError(stderrno, os.strerror(myerrno))

    def __enter__(self):
        self.oldsignals = sigprocmask(self.signals, SIG_BLOCK)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sigprocmask(self.oldsignals)
        self.close()
        return False

    '''
        Return the integer file descriptor returned by signalfd(2).
    '''

    def fileno(self):
        return self.fd

    '''
        Close the signalfd object. It cannot be used after this call.
    '''

    def close(self):
        os.close(self.fd)

    '''
        Return the next signalfd_siginfo structure available from the
        signalfd file descriptor. The signalfd_siginfo structure has the
        following attributes:
    
        For example::

            info = sigfd.info()
            print 'Received signal: %d' % info.ssi_signo
    '''

    def info(self):
        info = ffi.new('struct signalfd_siginfo *')
        buffer = ffi.buffer(info)
        buffer[:] = os.read(self.fd, ffi.sizeof('struct signalfd_siginfo'))
        return info
