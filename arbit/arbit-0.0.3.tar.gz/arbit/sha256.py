from _arbit import ffi, lib

def sha256(seed, r):
    buff = ffi.new("unsigned char[32]", seed)
    lib.sha256(buff, r)
    return ffi.string(buff)


def main():
    import sys
    import time

    if len(sys.argv) == 3:
        seed = sys.argv[1]
        if seed[:2] == "0x":
            seed = seed[2:]
        r = int(sys.argv[2])
        print(sha256(bytes.fromhex(seed), r).hex())
    else:
        t = time.clock()
        sha256(b'test', 50000000)
        print("MH/s: " + str(50./(time.clock()-t)))
