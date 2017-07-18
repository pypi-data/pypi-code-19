from cffi import FFI

ffibuilder = FFI()

ffibuilder.cdef(
    r"""
    unsigned char** solve(unsigned char *seed, int r, int checks);
    int verify(unsigned char** checkpoints, int r, int checks);
    """
)
with open('arbit/arbit.c') as src:
    ffibuilder.set_source("_arbit", src.read(), libraries=["crypto", "pthread"])


if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
