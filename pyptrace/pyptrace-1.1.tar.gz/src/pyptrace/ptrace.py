# coding: utf-8

'''
simple wrapper for ptrace sys call.
'''

import os
import json
import ctypes

ROOT = os.path.dirname(os.path.dirname(__file__))
PTRACE_SHARED_LIB = os.path.join(ROOT, 'ptrace_wrapper.so')

# __ptrace = ctypes.cdll.LoadLibrary("./libptrace/ptrace.so")
__ptrace = ctypes.cdll.LoadLibrary(PTRACE_SHARED_LIB)
PTRACE_O_EXITKILL = 1048576

class PtraceException(Exception):
    pass

def check_ret(fn):
    def wrapper(*args, **kwargs):
        ret = fn(*args, **kwargs)
        # print 'ret of %s: %d' % (fn.func_name, ret)

        if ret == -1:
            raise PtraceException('Failed executing %s' % fn.func_name)

        return ret

    return wrapper

@check_ret
def attach(pid):
    __attach = __ptrace.attach
    __attach.restype = ctypes.c_long
    __attach.argtypes = (ctypes.c_int, )

    ret = __attach(ctypes.c_int(pid))
    return ret

@check_ret
def cont(pid, signo=0):
    __cont = __ptrace.cont
    __cont.restype = ctypes.c_long
    __cont.argtypes = (ctypes.c_int, ctypes.c_int)

    ret = __cont(ctypes.c_int(pid), ctypes.c_int(signo))
    return ret

# TODO check error
def peektext(pid, addr):
    __peektext = __ptrace.peektext
    __peektext.restype = ctypes.c_long
    __peektext.argtypes = (ctypes.c_int, ctypes.c_long)

    ret = __peektext(ctypes.c_int(pid), ctypes.c_long(addr))
    return ret

# TODO check error
def peekdata(pid, addr):
    __peekdata = __ptrace.peekdata
    __peekdata.restype = ctypes.c_long
    __peekdata.argtypes = (ctypes.c_int, ctypes.c_long)

    ret = __peekdata(ctypes.c_int(pid), ctypes.c_long(addr))
    return ret

@check_ret
def poketext(pid, addr, data):
    __poketext = __ptrace.poketext
    __poketext.restype = ctypes.c_long
    __poketext.argtypes = (ctypes.c_int, ctypes.c_long, ctypes.c_long)

    ret = __poketext(ctypes.c_int(pid), ctypes.c_long(addr), ctypes.c_long(data))
    return ret


@check_ret
def pokedata(pid, addr, data):
    raise NotImplemented

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


class user_regs_x64(ctypes.Structure):
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


# TODO distinguish between 64-bit and 32-bit
user_regs = user_regs_x64

@check_ret
def getregs(pid, regs):
    __getregs = __ptrace.getregs
    __getregs.restype = ctypes.c_long
    __getregs.argtypes = ctypes.c_int, ctypes.POINTER(user_regs)

    ret = __getregs(ctypes.c_int(pid), ctypes.byref(regs))
    return ret

@check_ret
def setregs(pid, regs):
    __setregs = __ptrace.setregs
    __setregs.restype = ctypes.c_long
    __setregs.argtypes = ctypes.c_int, ctypes.POINTER(user_regs)

    ret = __setregs(ctypes.c_int(pid), ctypes.byref(regs))
    return ret

@check_ret
def singlestep(pid, signo=0):
    __singlestep = __ptrace.singlestep
    __singlestep.restype = ctypes.c_long
    __singlestep.argtypes = ctypes.c_int, ctypes.c_int

    ret = __singlestep(ctypes.c_int(pid), ctypes.c_int(signo))
    return ret

@check_ret
def traceme():
    __traceme = __ptrace.traceme
    __traceme.restype = ctypes.c_long

    ret = __traceme()
    return ret

'''
struct user_regs_struct
{
  __extension__ unsigned long long int r15;
  __extension__ unsigned long long int r14;
  __extension__ unsigned long long int r13;
  __extension__ unsigned long long int r12;
  __extension__ unsigned long long int rbp;
  __extension__ unsigned long long int rbx;
  __extension__ unsigned long long int r11;
  __extension__ unsigned long long int r10;
  __extension__ unsigned long long int r9; 
  __extension__ unsigned long long int r8; 
  __extension__ unsigned long long int rax;
  __extension__ unsigned long long int rcx;
  __extension__ unsigned long long int rdx;
  __extension__ unsigned long long int rsi;
  __extension__ unsigned long long int rdi;
  __extension__ unsigned long long int orig_rax;
  __extension__ unsigned long long int rip;
  __extension__ unsigned long long int cs; 
  __extension__ unsigned long long int eflags;
  __extension__ unsigned long long int rsp;
  __extension__ unsigned long long int ss; 
  __extension__ unsigned long long int fs_base;
  __extension__ unsigned long long int gs_base;
  __extension__ unsigned long long int ds; 
  __extension__ unsigned long long int es; 
  __extension__ unsigned long long int fs; 
  __extension__ unsigned long long int gs; 
};

struct user_regs_struct
{
  long int ebx;
  long int ecx;
  long int edx;
  long int esi;
  long int edi;
  long int ebp;
  long int eax;
  long int xds;
  long int xes;
  long int xfs;
  long int xgs;
  long int orig_eax;
  long int eip;
  long int xcs;
  long int eflags;
  long int esp;
  long int xss;
};

'''
# def getregs(pid, )
# pid = 26305
# # print(attach(17944))
# # import pdb; pdb.set_trace()
# attach(pid)
# print os.waitpid(pid, 0)

# addr = 0x8048310
# data = peektext(pid, addr)
# print 'data: 0x%08x' % (data)

# cont(pid)
# print 'hello'

# import pdb; pdb.set_trace()

from operator import or_
 
@check_ret
def set_options(pid, *options):
    option_val = reduce(or_, options, 0)

    __setoptions = __ptrace.setoptions
    __setoptions.argtypes = (ctypes.c_int, ctypes.c_int)
    __setoptions.restype = ctypes.c_long

    ret = __setoptions(pid, option_val)
    return ret

