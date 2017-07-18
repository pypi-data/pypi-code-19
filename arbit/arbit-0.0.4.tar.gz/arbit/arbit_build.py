from cffi import FFI

ffibuilder = FFI()

ffibuilder.cdef(
    r"""
    void sha256(unsigned char*, int);
    """
)

ffibuilder.set_source("_arbit",
    r"""
    #include <openssl/sha.h>
    void sha256(unsigned char* buffer, int r){
        int i;
        for(i = 0; i < r; i++){
            SHA256_CTX context;
            SHA256_Init(&context);
            SHA256_Update(&context, buffer, SHA256_DIGEST_LENGTH);
            SHA256_Final(buffer, &context);
        }
    }
    """, libraries = ["crypto"]
)



if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
