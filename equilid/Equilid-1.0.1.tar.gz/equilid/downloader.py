#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys, os
import tempfile
import tarfile
import urllib
if (sys.version_info>(3,0)): from urllib.request import urlretrieve 
else : from urllib import urlretrieve

pkg_path = '/tmp/test/equilid/' # os.path.dirname(os.path.abspath(__file__))
sys.path.append(pkg_path)

def Schedule(a,b,c):
    '''''
    a: Data already downloaded
    b: Size of Data block
    c: Size of remote file
   '''
    per = 100.0 * a * b / c
    per = min(100.0, per)
    if(int(round(per, 2)) % 10 == 0):
        print ('Downloading %.2f%%' % per)


host_root = "https://cs.stanford.edu/~jurgens/models/"

lang_70_model = (host_root + "70lang.tar.gz", pkg_path + '/../models/70lang/')
lang_214_model = (host_root + "214lang.tar.gz", pkg_path + '/../models/214lang/')

def download_model(model):
    print model
    url, model_dir = model
        
    if not os.path.exists(model_dir):
        print 'Creating model directory', model_dir
        os.makedirs(model_dir)
        
    if len(os.listdir(model_dir)) > 2:
        print ("Model files already %s exist..." % model_dir)
    else:
        print ("Downloading file %s" % url)
        td = tempfile.mkdtemp('equilid')
        print td
        urlretrieve(url, td + '/model.tar.gz', Schedule)
        # Unpack the model
        tar = tarfile.open(td + '/model.tar.gz', mode='r:gz')
        tar.extractall(path=model_dir)
        tar.close()
        os.unlink(td)

def download(module = None):
    if module:
        if (module.lower() == "70lang"):
            print ("Downloading 70-language model...")
            download_model(lang_70_model)
        elif (module.lower() == "214lang"):
            print ("Downloading 214-language module...")
            download_model(lang_214_model)
        else:
            print ("module not found...")
    
    else:
        print ("Downloading 70-language module...")
        download_model(lang_70_model)

def test():
    download()

if __name__ == '__main__':
    test()
