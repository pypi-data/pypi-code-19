#!/usr/bin/env python
# This script uses the pycamhd module to print the number of frames in a remote
# video file.
#
# Aaron Marburg (amarburg@apl.washington.edu)
# Copied from Timothy Crone (tjcrone@gmail.com)

import pycamhd.lazycache as camhd

# remote file
filename = '/RS03ASHS/PN03B/06-CAMHDA301/2016/11/13/CAMHDA301-20161113T000000Z.mov'
filename_num_frames = 25169
test_lazycache = 'https://camhd-cache.appspot.com/v1/org/oceanobservatories/rawdata/files'

def test_get_frame_count():
    # download moov_atom from remote file
    movie = camhd.get_metadata( test_lazycache + filename )
    assert movie["NumFrames"] == filename_num_frames


## Object-oriented version
def test_get_frame_count_default():
    r = camhd.lazycache()
    movie = r.get_metadata( filename )
    assert movie["NumFrames"] == filename_num_frames

def test_get_frame_count_specify():
    r = camhd.lazycache(test_lazycache)
    movie = r.get_metadata( filename )
    assert movie["NumFrames"] == filename_num_frames

def test_get_frame_count_none():
    r = camhd.lazycache(None)
    movie = r.get_metadata( filename )
    assert movie["NumFrames"] == filename_num_frames
