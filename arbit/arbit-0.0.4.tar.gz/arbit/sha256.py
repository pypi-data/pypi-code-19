from _arbit import ffi, lib

def sha256(seed, r, checks):
    buff = ffi.new("unsigned char[32]", seed)
    checkpoints = []
    for _ in range(checks):
        lib.sha256(buff, r//checks)
        checkpoints.append(ffi.string(buff))
    return checkpoints


def main():
    import sys
    import time

    if len(sys.argv) == 3:
        seed = sys.argv[1]
        if seed[:2] == "0x":
            seed = seed[2:]
        r = int(sys.argv[2])
        print(sha256(bytes.fromhex(seed), r, 1)[0].hex())
    else:
        t = time.clock()
        sha256(b'test', 50000000, 16)
        print("MH/s: " + str(50./(time.clock()-t)))
