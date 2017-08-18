import json
import ctypes
import platform

from const import *
import _pyptrace

class X64UserRegs(ctypes.Structure):
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
    generate reg fields from /usr/include/sys/user.h
    cat rs | awk '{print $3}' | tr -d ';' | awk '{print "(\""$1"\",\t\tctypes.c_uint32),"}'
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

arch = platform.machine()
if arch == 'x86_64':
    UserRegs = X64UserRegs
elif arch == 'i686':
    UserRegs = X32UserRegs
else:
    raise UnsupportArchException(arch)

class RegsWrapper(object):
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

def attach(pid):
    return _pyptrace._pyptrace(PTRACE_ATTACH, pid, 0, 0)

def cont(pid, signo=0):
    return _pyptrace._pyptrace(PTRACE_CONT, pid, 0, signo)

def traceme():
    return _pyptrace._pyptrace(PTRACE_TRACEME, 0, 0, 0)

def detach(pid, signo):
    return _pyptrace._pyptrace(PTRACE_DETACH, pid, 0, signo)

def peektext(pid, addr):
    return _pyptrace._pyptrace_peek(PTRACE_PEEKTEXT, pid, addr)

def peekdata(pid, addr):
    return _pyptrace._pyptrace_peek(PTRACE_PEEKDATA, pid, addr)

def peekuser(pid, addr):
    return _pyptrace._pyptrace_peek(PTRACE_PEEKUSER, pid, addr)

def poketext(pid, addr, data):
    return _pyptrace._pyptrace(PTRACE_POKETEXT, pid, addr, data)

def pokedata(pid, addr, data):
    return _pyptrace._pyptrace(PTRACE_POKEDATA, pid, addr, data)

def pokeuser(pid, addr, data):
    return _pyptrace._pyptrace(PTRACE_POKEUSER, pid, addr, data)

def singlestep(pid, signo=0):
    return _pyptrace._pyptrace(PTRACE_SINGLESTEP, pid, 0, signo)

def syscall(pid, signo=0):
    return _pyptrace._pyptrace(PTRACE_SYSCALL, pid, 0, signo)

def setoptions(pid, options):
    return _pyptrace._pyptrace(PTRACE_SETOPTIONS, pid, 0, options)

_libc = ctypes.cdll.LoadLibrary('libc.so.6')

def getregs(pid):
    regs = UserRegs()
    _libc_ptrace = _libc.ptrace
    _libc_ptrace.restype = ctypes.c_long
    _libc_ptrace.argtypes = (ctypes.c_long, ctypes.c_int,
                             ctypes.c_void_p, ctypes.POINTER(UserRegs))

    ret = _libc_ptrace(PTRACE_GETREGS, pid, None, ctypes.byref(regs))
    return ret, regs

def setregs(pid, regs):
    _libc_ptrace = _libc.ptrace
    _libc_ptrace.restype = ctypes.c_long
    _libc_ptrace.argtypes = (ctypes.c_long, ctypes.c_int,
                             ctypes.c_void_p, ctypes.POINTER(UserRegs))

    ret = _libc_ptrace(PTRACE_SETREGS, pid, None, ctypes.byref(regs))
