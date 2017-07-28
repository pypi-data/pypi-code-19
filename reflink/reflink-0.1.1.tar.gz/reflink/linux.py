from cffi import FFI

REFLINK_ATTR_PRESERVE = 0x1
REFLINK_ATTR_NONE = 0x0

ffibuilder = FFI()
with open("reflink/linux.c") as source_file:
    ffibuilder.set_source("reflink._backend", source_file.read())

ffibuilder.cdef("""
int reflink_clone_file(char *oldpath, char *newpath);
int errno;
""")

if __file__ == '__main__':
    ffibuilder.compile(verbose=True)
