import os
import shutil
from .config import PACKAGE_PATH


def install(suffix="uncle"):
    # home
    home = os.environ["HOME"]

    # 1. copy file to specified location ~/.bashrc_uncle
    fp_uncle = PACKAGE_PATH + "/data/bashrc_uncle.sh"
    fp_dest = home + "/.bashrc_uncle"
    shutil.copy(fp_uncle, fp_dest)
    print("@uncle: copy uncle to {} \n".format(fp_dest))

    # 2. connection line?
    s = "[ -f {}/.bashrc_{} ] && . {}/.bashrc_{}".format(
        home, suffix, home, suffix)

    # check existence for connection line in current ~/.bashrc file
    f = open("{}/.bashrc".format(home))
    lines = f.readlines()
    f.close()
    print("These are the last 10 lines in your {}/.bashrc file".format(home))
    print("==================================================================")
    for i, line in enumerate(lines[-10:]):
        print("{:02d} | ".format(i), line[:-1])
    print("==================================================================")

    # verbose
    print("")
    print("@uncle: run *uncle.add_line()* to add the following line to your ~/.bashrc file ...")
    print("==================================================================")
    print(s)
    print("==================================================================")


def add_line(suffix="uncle"):
    # home
    home = os.environ["HOME"]

    # 1. add connection line?
    s = "[ -f {}/.bashrc_{} ] && . {}/.bashrc_{}".format(home, suffix, home, suffix)
    f = open("{}/.bashrc".format(home), "a")
    f.write(s + "\n")
    f.close()

    # 2. check
    f = open("{}/.bashrc".format(home))
    lines = f.readlines()
    f.close()
    print("These are the NEW last 10 lines in your {}/.bashrc file".format(home))
    print("==================================================================")
    for i, line in enumerate(lines[-10:]):
        print("{:02d} | ".format(i), line[:-1])
    print("==================================================================")


def del_line():
    # home
    home = os.environ["HOME"]

    # 1. add connection line?
    f = open("{}/.bashrc".format(home), "r")
    lines = f.readlines()
    f.close()

    # 2. check
    f = open("{}/.bashrc".format(home), "w+")
    f.writelines(lines[:-1])
    f.close()
    print("These are the NEW last 10 lines in your {}/.bashrc file".format(home))
    print("==================================================================")
    for i, line in enumerate(lines[-11:-1]):
        print("{:02d} | ".format(i), line[:-1])
    print("==================================================================")


def test():
    import unclebash as u
    u.install()
    u.add_line()
    u.del_line()


if __name__ == "__main__":
    install()