#!/usr/bin/env python
# This script uses the pycamhd module to print the number of frames in a remote
# video file.
#
# Aaron Marburg (amarburg@apl.washington.edu)
# Copied from Timothy Crone (tjcrone@gmail.com)

import pycamhd.lazycache as camhd

# remote file
filename = '/RS03ASHS/PN03B/06-CAMHDA301/2016/11/13/CAMHDA301-20161113T000000Z.mov'
test_lazycache = 'https://camhd-app-dev-nocache.appspot.com/v1/org/oceanobservatories/rawdata/files'

def test_get_frame_count():
    # download moov_atom from remote file
    movie = camhd.get_metadata( test_lazycache + filename )

    ## This is known apriori
    assert movie["NumFrames"] == 25169


## Object-oriented version
def test_get_frame_count_oo():
    r = camhd.lazycache()
    movie = r.get_metadata( filename )
    ## This is known apriori
    assert movie["NumFrames"] == 25169
