#!/usr/bin/python3
''' This script to export feedback file from submissions
'''

import os
import argparse
import shutil
from tqdm import tqdm

'''
def main():
    # The main function to run the script
    
    try:
        args = args_handle()

    except NotADirectoryError as err:
        print(err)
        return

    export(args.path, args.out, args.file)
'''

def export_result():
    
    try:
        args = args_handle()

    except NotADirectoryError as err:
        print(err)
        return

    export(args.path, args.out, args.file)


def args_handle():
    ''' Handle input options via command line arguments
    '''
    parser = argparse.ArgumentParser(prog='export.py')
    parser.add_argument("path", help="input path for the directory",
                        default="./")
    parser.add_argument("file", help="the file to export outside")
    parser.add_argument("-o", "--out", help="The output folder path",
                        default="./")

    args = parser.parse_args()

    if not os.path.isdir(args.path) or not os.path.isdir(args.out):
        raise NotADirectoryError("Directory doesn't exist")

    return args


def export(dir_path, out_path, file_name):
    ''' Export the file from all directories in dir to out Directory
    '''
    bads = []
    out_path = make_dir(out_path)

    for dir_entry in tqdm(list(filter(lambda entry: entry.is_dir(),
                                      (os.scandir(dir_path))))):
        file_path = "%s/%s" % (dir_entry.path, file_name)
        output_file = "%s/%s.md" % (out_path, dir_entry.name)
        if not os.path.isfile(file_path):
            bads.append(dir_entry.name)
        else:
            shutil.copy(file_path, output_file)
    if bads:
        print("There are", len(bads), "directories that do not have", file_name, ":")
        print("\n".join(bads))

def make_dir(out_path):
    ''' Smart making the output folder
    '''
    try:
        out = "%s/output-export" % out_path
        os.makedirs(out)

    except FileExistsError:
        count = 1
        while True:
            try:
                out = "%s/output-export-%d" % (out_path, count)
                os.makedirs(out)
                break
            except FileExistsError:
                count += 1
                continue
    return out

'''
if __name__ == "__main__":
    main()
'''