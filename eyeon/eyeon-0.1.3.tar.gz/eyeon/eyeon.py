import hashlib
import os
import subprocess
import sys
import time

def get_files():
    files = []

    if len(sys.argv) == 1:
        print("You must provide files to watch.\n \
            COMMAND: watcher [html file] [css file]\n")
        sys.exit()
    else:
        for item in sys.argv[1:]:
            files.append(os.path.abspath(item))
        return files

#reset watched file and its hash value to None.
def reset():
    global html_file
    global html_hashval
    global css_file
    global css_hashval
    html_file = None
    html_hashval = None
    css_file = None
    css_hashval = None

#update watched file and its hash value.
def update(files):
    global html_file
    global html_hashval
    global css_file
    global css_hashval
    html_file = open(files[0], "r")
    css_file = open(files[1], "r")
    html_hashval = hashlib.md5(html_file.read().encode("utf-8")).digest()
    css_hashval = hashlib.md5(css_file.read().encode("utf-8")).digest()

#Check if wathced file hash has changed by opening and rehashing.
def check(files):
    html_new = open(files[0], "r")
    html_hashval_new = hashlib.md5(html_new.read().encode("utf-8")).digest()
    css_new = open(files[1], "r")
    css_hashval_new = hashlib.md5(css_new.read().encode("utf-8")).digest()
    
    #if hash values differ update watched file hash and reopen file.
    if html_hashval_new != html_hashval or css_hashval_new != css_hashval:
        reopen(files)

#reopen the file
def reopen(files):
    if sys.platform == "win32":
        subprocess.call(["start", files[0]], shell=True)
    elif sys.platform == "darwin":
        subprocess.call(["open", files[0], "--background", "--fresh"])
    update(files)
        
#start the application
def start():
    reset()
    file_list = get_files()
    print("started watching file(s) {}".format(file_list))
    update(file_list)
    while True:
        check(file_list)
        #1 second delay between checking hash values.
        time.sleep(1)
