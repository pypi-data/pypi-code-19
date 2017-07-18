from _arbit import ffi, lib

def solve(seed, r, checks):
    def clear(ptr):
        lib.clear(ptr, checks)

    buff = ffi.new("unsigned char[32]", seed)
    res = lib.solve(buff, r, checks)
    checkpoints = ffi.cast("char**", res)
    ret = [ffi.unpack(checkpoints[i], 32) for i in range(checks+1)]
    return ret

def verify(checks, r):
    check_array = [ffi.new("unsigned char[32]", check) for check in checks]
    checkpoints = ffi.new("unsigned char*[]", len(checks))
    for i in range(len(checks)):
        checkpoints[i] = check_array[i]
    return lib.verify(check_array, r, len(checks)-1)
