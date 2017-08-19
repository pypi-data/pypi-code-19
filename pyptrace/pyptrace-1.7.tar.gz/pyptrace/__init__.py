# coding: utf-8

'''
Python wrapper for ptrace.
'''

import json
import ctypes
import platform
from collections import Sequence
import functools

from const import *
import _pyptrace

class X64UserRegs(ctypes.Structure):
    '''
    x64 UserRegs structure, see /usr/include/sys/user.h.
    '''
    _fields_ = [
        ('r15',     ctypes.c_uint64),
        ('r14',     ctypes.c_uint64),
        ('r13',     ctypes.c_uint64),
        ('r12',     ctypes.c_uint64),
        ('rbp',     ctypes.c_uint64),
        ('rbx',     ctypes.c_uint64),
        ('r11',     ctypes.c_uint64),
        ('r10',     ctypes.c_uint64),
        ('r9',      ctypes.c_uint64),
        ('r8',      ctypes.c_uint64),
        ('rax',     ctypes.c_uint64),
        ('rcx',     ctypes.c_uint64),
        ('rdx',     ctypes.c_uint64),
        ('rsi',     ctypes.c_uint64),
        ('rdi',     ctypes.c_uint64),
        ('orig_rax',ctypes.c_uint64),
        ('rip',     ctypes.c_uint64),
        ('cs',      ctypes.c_uint64),
        ('eflags',  ctypes.c_uint64),
        ('rsp',     ctypes.c_uint64),
        ('ss',      ctypes.c_uint64),
        ('fs_base', ctypes.c_uint64),
        ('gs_base', ctypes.c_uint64),
        ('ds',      ctypes.c_uint64),
        ('es',      ctypes.c_uint64),
        ('fs',      ctypes.c_uint64),
        ('gs',      ctypes.c_uint64),
    ]

class X32UserRegs(ctypes.Structure):
    '''
    x32 UserRegs structure, see /usr/include/sys/user.h.
    '''

    _fields_ = [
        ("ebx",			ctypes.c_uint32),
        ("ecx",			ctypes.c_uint32),
        ("edx",			ctypes.c_uint32),
        ("esi",			ctypes.c_uint32),
        ("edi",			ctypes.c_uint32),
        ("ebp",			ctypes.c_uint32),
        ("eax",			ctypes.c_uint32),
        ("xds",			ctypes.c_uint32),
        ("xes",			ctypes.c_uint32),
        ("xfs",			ctypes.c_uint32),
        ("xgs",			ctypes.c_uint32),
        ("orig_eax",	ctypes.c_uint32),
        ("eip",			ctypes.c_uint32),
        ("xcs",			ctypes.c_uint32),
        ("eflags",		ctypes.c_uint32),
        ("esp",			ctypes.c_uint32),
        ("xss",			ctypes.c_uint32),
    ]

class UnsupportArchException(Exception):
    pass

class PtraceException(Exception):
    pass

'''
UserRegs structure, PyPtrace will choose bwtween X32UserRegs/X64UserRegs
according to the machine arch that it is running on.
'''
UserRegs = None

arch = platform.machine()
if arch == 'x86_64':
    UserRegs = X64UserRegs
elif arch == 'i686':
    UserRegs = X32UserRegs
else:
    raise UnsupportArchException(arch)

class RegsWrapper(object):
    '''
    Wrapper for UserRegs, for pretty printing of UserRegs.
    '''

    def __init__(self, regs):
        self.regs = regs

    def __str__(self):
        if not self.regs:
            return None

        def reg_val(reg_name):
            reg = getattr(self.regs, reg_name)
            val = reg.real if hasattr(reg, 'real') else None
            if val: val = '0x{:016x}'.format(val)

            return val

        # register does not starts with '_'
        reg_names = [attr for attr in dir(self.regs) if not attr.startswith('_')]
        reg_dict = {reg_name: reg_val(reg_name) for reg_name in reg_names}
        return json.dumps(reg_dict, indent=4)

def check_ret(fn):
    '''
    Decorator for ptrace requests.
    This decorator will check the resutl for ptrace request and
    throw exception if throw_exception == True.
    '''

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        throw_exception = kwargs.get('throw_exception', True)
        if 'throw_exception' in kwargs:
            del kwargs['throw_exception']

        ret = fn(*args, **kwargs)
        errno = ret[0] if isinstance(ret, Sequence) else  ret 
        if errno != 0 and throw_exception is True:
            raise PtraceException('Failed executing %s' % fn.func_name)

        return ret 

    return wrapper

@check_ret
def attach(pid):
    '''
    Attach  to  the process specified in pid, making it a tracee of the
    calling process.
    '''

    return _pyptrace._pyptrace(PTRACE_ATTACH, pid, 0, 0)

@check_ret
def cont(pid, signo=0):
    '''
    Restart  the  stopped  tracee  process. If signo is nonzero, it is
    interpreted as the number of a signal to be delivered to the tracee;
    otherwise, no signal is delivered.
    '''

    return _pyptrace._pyptrace(PTRACE_CONT, pid, 0, signo)

@check_ret
def traceme():
    '''
    Indicate that this process is to be traced by its parent.
    '''

    return _pyptrace._pyptrace(PTRACE_TRACEME, 0, 0, 0)

@check_ret
def detach(pid, signo):
    '''
    Restart  the stopped tracee as for cont(), but first detach from it.
    '''

    return _pyptrace._pyptrace(PTRACE_DETACH, pid, 0, signo)

@check_ret
def peektext(pid, addr):
    '''
    Read  a  word  at  the address addr in the tracee's text memory, returning
    the word as the result of the peektext() call.
    '''

    return _pyptrace._pyptrace_peek(PTRACE_PEEKTEXT, pid, addr)

@check_ret
def peekdata(pid, addr):
    '''
    Read  a  word  at  the address addr in the tracee's data memory, returning
    the word as the result of the peektext() call.
    '''

    return _pyptrace._pyptrace_peek(PTRACE_PEEKDATA, pid, addr)

@check_ret
def peekuser(pid, addr):
    '''
    Read a word at offset addr in the tracee's USER area,  which  holds  the
    registers  and  other  information  about  the  process (see <sys/user.h>).
    '''

    return _pyptrace._pyptrace_peek(PTRACE_PEEKUSER, pid, addr)

@check_ret
def poketext(pid, addr, data):
    '''
    Copy the word data to the address addr in the tracee's text memory.
    '''

    return _pyptrace._pyptrace(PTRACE_POKETEXT, pid, addr, data)

@check_ret
def pokedata(pid, addr, data):
    '''
    Copy the word data to the address addr in the tracee's data memory.
    '''

    return _pyptrace._pyptrace(PTRACE_POKEDATA, pid, addr, data)

@check_ret
def pokeuser(pid, addr, data):
    '''
    Copy  the  word  data to offset addr in the tracee's USER area.
    '''

    return _pyptrace._pyptrace(PTRACE_POKEUSER, pid, addr, data)

@check_ret
def singlestep(pid, signo=0):
    '''
    Restart  the  stopped  tracee  as  for cont(), but arrange for the tracee
    to be stopped at the next entry to or exit after a single instruction.
    '''

    return _pyptrace._pyptrace(PTRACE_SINGLESTEP, pid, 0, signo)

@check_ret
def syscall(pid, signo=0):
    '''
    Restart  the  stopped  tracee  as  for cont(), but arrange for the tracee
    to be stopped at the next entry to or exit from a system call.
    '''

    return _pyptrace._pyptrace(PTRACE_SYSCALL, pid, 0, signo)

@check_ret
def setoptions(pid, options):
    '''
    Set  ptrace  options from options.
    '''

    return _pyptrace._pyptrace(PTRACE_SETOPTIONS, pid, 0, options)

_libc = ctypes.cdll.LoadLibrary('libc.so.6')

@check_ret
def getregs(pid):
    '''
    Return the tracee's general-purpose registers.
    '''

    regs = UserRegs()
    _libc_ptrace = _libc.ptrace
    _libc_ptrace.restype = ctypes.c_long
    _libc_ptrace.argtypes = (ctypes.c_long, ctypes.c_int,
                             ctypes.c_void_p, ctypes.POINTER(UserRegs))

    ret = _libc_ptrace(PTRACE_GETREGS, pid, None, ctypes.byref(regs))
    return ret, regs

@check_ret
def setregs(pid, regs):
    '''
    Modify the tracee's general-purpose registers,  respectively,  from  the
    paramater  regs.
    '''

    _libc_ptrace = _libc.ptrace
    _libc_ptrace.restype = ctypes.c_long
    _libc_ptrace.argtypes = (ctypes.c_long, ctypes.c_int,
                             ctypes.c_void_p, ctypes.POINTER(UserRegs))

    ret = _libc_ptrace(PTRACE_SETREGS, pid, None, ctypes.byref(regs))
    return ret
