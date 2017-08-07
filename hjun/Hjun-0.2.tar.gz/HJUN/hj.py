import os.path as path
import test_pack as tp
import sys

def hjun_call():
    print("Called!")
    print(path.abspath)
    tp.print_hi()


if __name__ == "__main__":
    sys.exit(hjun_call())



