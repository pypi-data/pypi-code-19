# -*- coding: utf-8 -*-
"""
Created 2017/04/27
Last update 2017/08/14

@author: Markus Eisenbach

Description:
Automatic download of GAPs dataset if not available on PC.
"""

from __future__ import print_function
import os
import numpy as np
import ftplib
import cPickle as pkl
import hashlib

def _download_from_ftp(url, user, passwd, fpath, debug_outputs=False):
    """Helper function to retrieve a file from a FTP server."""
    # split url in host, directory and filename
    url_part = url.split('/')
    host = url_part[2]
    beg = len(host) + len(url_part[1]) + len(url_part[0]) + 2
    end = -len(url_part[-1])
    ftp_dir = url[beg:end]
    ftp_file = url_part[-1]
    # connect to ftp server
    try:
        ftp = ftplib.FTP(host, user=user, passwd=passwd)
    except (ftplib.error_perm):
        if debug_outputs:
            print('ERROR: cannot connect to FTP server')
        return
    except:
        if debug_outputs:
            print('ERROR: cannot establish an internet connection')
        return
    # change directory
    ftp.cwd(ftp_dir)
    # write to file
    with open(fpath, 'wb') as dst_file:
        ftp.retrbinary('RETR ' + ftp_file, dst_file.write)
    # close ftp connection
    ftp.quit()


def _download_from_ftp_if_neccessary(url, user, passwd, fpath,
                                     debug_outputs=False):
    """Helper function that checks if file exists. If not,
       the file is downloaded from FTP."""
    # check if download is necessary
    if not os.path.exists(fpath):
        # file not found -- download from ftp
        if debug_outputs:
            print('download {}'.format(url))
        _download_from_ftp(url, user, passwd, fpath, debug_outputs)
        
        
def _calc_md5(filename, debug_outputs=False):
    """Helper function to compute the MD5 checksum
       of the content of a file."""
    md5_checksum = None
    try:
        with open(filename) as file_to_check:
            # read contents of the file
            data = file_to_check.read()
            # pipe contents of the file through
            md5_checksum = hashlib.md5(data).hexdigest()
    except (IOError):
        if debug_outputs:
            print('ERROR: cannot open file {}'.format(filename))
    return md5_checksum


def _is_valid(filename, md5_checksum, debug_outputs=False):
    """Helper function to check whether the MD5 checksum
       of the content of a file matches the expected checksum."""
    file_md5 = _calc_md5(filename, debug_outputs)
    file_is_valid = file_md5 == md5_checksum
    return file_is_valid


def _download_if_not_available(datadir, source, checksum, login,
                               debug_outputs=False):
    """Helper function to download the dataset if it is not available on
       file system. Checks the correctness of each files checksum. Deletes
       files that do not match the checksum and downloads them again (maximum
       three times)."""
    if not os.path.exists(datadir):
        if debug_outputs:
            print('create directory {}'.format(datadir))
        try:
            os.makedirs(datadir)
        except:
            if debug_outputs:
                print('ERROR: cannot create directory {}'.format(datadir))

    # get filename from URL
    file_parts = source.split('/')
    dirname, filename = file_parts[-2], file_parts[-1]
    fpath = os.path.join(datadir, dirname, filename)

    # create subdir
    subdir = os.path.join(datadir, dirname)
    if not os.path.exists(subdir):
        if debug_outputs:
            print('create directory {}'.format(subdir))
        try:
            os.makedirs(subdir)
        except:
            if debug_outputs:
                print('ERROR: cannot create directory {}'.format(subdir))
    
    download_list = [(source, fpath, checksum, 3)]
    
    sha256 = '330453216adcadf76a60e0a0d4ecd0f7a399c9eb464efdc38cd5725398dc8fa9'
    if hashlib.sha256(login).hexdigest() != sha256:
        print('ERROR: login not correct')
        return
    split=int(login[-1])
    user=login[:split]
    passwd=login[split:-1]
    
    while len(download_list) > 0:
        s, f, c, tries = download_list.pop(0)
        if tries == 0:
            if debug_outputs:
                print('download failed 3x -- terminate')
            return
        
        # check if download is necessary
        _download_from_ftp_if_neccessary(s, user=user, passwd=passwd,
                                         fpath=f, debug_outputs=debug_outputs)
        
        if not _is_valid(f, c, debug_outputs):
            download_list.append((s, f, c, tries - 1))
            try:
                os.remove(f)
            except:
                pass
            if debug_outputs:
                print('checksum failed for file {} -- delete file'.format(f))
    
    # check if it is an info file listing all other download files
    if fpath[:-4] == '.pkl':
        # read info file
        with open(fpath, 'rb') as pkl_file:
            data = pkl.load(pkl_file)
        
        # get chunk names
        chunk_descriptor_digits = data['chunk_descriptor_digits']
        n_chunks = data['n_chunks']
        templ = 'chunk_{:0' + str(chunk_descriptor_digits) + 'd}_{}.npy'
        fpath_template = fpath[:-8] + templ
        source_template = source[:-8] + templ
        checksums = data['checksums']
        
        # download chunks if neccessary
        download_list = []
        for chunk_idx in range(n_chunks):
            md5_checksums = checksums[chunk_idx]
            for data_idx in ['x', 'y']:
                # get filename and URL of chunk
                fpath_chunk = fpath_template.format(chunk_idx, data_idx)
                source_chunk = source_template.format(chunk_idx, data_idx)
                
                if data_idx == 'x':
                    md5_compare = md5_checksums[0]
                else:
                    md5_compare = md5_checksums[1]
                download_list.append((source_chunk, fpath_chunk,
                                      md5_compare, 3))
    
        while len(download_list) > 0:
            s, f, c, tries = download_list.pop(0)
            if tries == 0:
                if debug_outputs:
                    print('download failed 3x -- terminate')
                return
            
            # check if download is necessary
            _download_from_ftp_if_neccessary(s, user=user, passwd=passwd,
                                             fpath=f,
                                             debug_outputs=debug_outputs)
            
            if not _is_valid(f, c, debug_outputs):
                download_list.append((s, f, c, tries - 1))
                try:
                    os.remove(f)
                except:
                    pass
                if debug_outputs:
                    print('checksum failed for file {} -- delete file'.format(f))


def _check_file(dataset_file, debug_outputs=False):
    """Helper function plotting error messages in case of a failed download."""
    if not os.path.exists(dataset_file):
        if debug_outputs:
            msg = 'download failed for file {}'.format(dataset_file)
            msg2 = 'you may apply for a valid login first'
            msg3 = 'see http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/'
            print('ERROR: {}\nHINT: {}\nHINT: {}'.format(msg, msg2, msg3))
        else:
            msg4 = 'for detailed error messages set debug_outputs=True'
            print('ERROR occured during download: {}'.format(msg4))
        return None


def download(login='skip',
        datadir='/local/datasets/gaps/v1', version=1.0, size='64x64',
        source='ftp://141.24.24.121/GAPs/v1/',
        train='train/chunks_64x64_NORMvsDISTRESS_train_info.pkl',
        train_checksum='8ff1685346ee4809836e2173e17ab006',
        valid='valid/chunks_64x64_NORMvsDISTRESS_valid_info.pkl',
        valid_checksum='a04203dd87cf3387c9c3831ef930c1e4',
        test='test/chunks_64x64_NORMvsDISTRESS_test_info.pkl',
        test_checksum='0aca7893c6fcef41afdfa819c01dcef5',
        load_train=True, load_valid=True, load_test=True,
        debug_outputs=False, set_access_rights=False):
    """Downloads the GAPs dataset. Please enter a valid login."""
    if login == 'skip':
        return
    if version != 1.0:
        print('ERROR: currently only version 1.0 available')
        return
    if size != '64x64':
        print('ERROR: only patch size 64x64 available')
        print('HINT: other sizes will be available in later versions')
        return
    if load_train:
        _download_if_not_available(datadir, source + train, train_checksum,
                                   login, debug_outputs)
        _check_file(os.path.join(datadir, train), debug_outputs)
    if load_valid:
        _download_if_not_available(datadir, source + valid, valid_checksum,
                                   login, debug_outputs)
        _check_file(os.path.join(datadir, valid), debug_outputs)
    if load_test:
        _download_if_not_available(datadir, source + test, test_checksum,
                                   login, debug_outputs)
        _check_file(os.path.join(datadir, test), debug_outputs)
    if set_access_rights:
        os.system('chmod -R 777 ' + datadir)


def load_chunk(no, subset='train', login='skip',
               datadir='/local/datasets/gaps/v1', version=1.0, size='64x64',
               debug_outputs=False):
    """Loads a 500MB chunk of the GAPs dataset. If you did not download the
       dataset first, please enter a valid login to make up this step."""
    download(login=login, version=version, size=size, datadir=datadir,
             debug_outputs=debug_outputs)
    # check if dataset is downloaded
    dataset_file = '{0}/chunks_64x64_NORMvsDISTRESS_{0}_info.pkl'.format(subset)
    dataset_file = os.path.join(datadir, dataset_file)
    if not os.path.exists(dataset_file):
        if login == 'skip':
            msg = 'could not load chunk'
            msg2 = 'you must download the dataset first by entering '
            msg2 += 'a valid login'
            msg3 = 'see http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/'
            print('ERROR: {}\nHINT: {}\nHINT: {}'.format(msg, msg2, msg3))
            return None
        else:
            msg = 'cannot download dataset without valid login'
            msg2 = 'if you do not have one, please apply for a login'
            msg3 = 'see http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/'
            print('ERROR[1]: {}\nHINT: {}\nHINT: {}'.format(msg, msg2, msg3))
            if not debug_outputs:
                msg4 = 'for detailed error messages set debug_outputs=True'
                print('HINT: {}'.format(msg4))
            return None
    # continue extracting the chunk
    filename = '{0}/chunks_64x64_NORMvsDISTRESS_{0}_chunk_{1:03d}_{2}.npy'
    chunk_filepath_fmt = os.path.join(datadir, filename)
    chunk_x = chunk_filepath_fmt.format(subset, no, 'x')
    if not os.path.exists(chunk_x):
        msg = 'cannot load chunk; file {} does not exist'.format(chunk_x)
        msg2 = 'you may download the dataset first by entering a valid login'
        msg3 = 'see http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/'
        print('ERROR[2]: {}\nHINT: {}\nHINT: {}'.format(msg, msg2, msg3))
        if not debug_outputs:
            msg4 = 'for detailed error messages set debug_outputs=True'
            print('HINT: {}'.format(msg4))
        return None
    x = np.load(chunk_x)
    chunk_y = chunk_filepath_fmt.format(subset, no, 'y')
    if not os.path.exists(chunk_y):
        msg = 'cannot load chunk; file {} does not exist'.format(chunk_y)
        msg2 = 'you may download the dataset first by entering a valid login'
        msg3 = 'see http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/'
        print('ERROR[3]: {}\nHINT: {}\nHINT: {}'.format(msg, msg2, msg3))
        if not debug_outputs:
            msg4 = 'for detailed error messages set debug_outputs=True'
            print('HINT: {}'.format(msg4))
        return None
    y = np.load(chunk_y)
    return x, y


def download_images(login='skip',
        datadir='/local/datasets/gaps/v1', version=1.0, size='64x64',
        source='ftp://141.24.24.121/GAPs/v1/',
        images='images/images.zip',
        images_checksum='8df7a86b6c5c04776a539001d893e047',
        train='images/patch_references_train.npy',
        train_checksum='23253cff2efc61e5e2cf37509d0cdb68',
        valid='images/patch_references_valid.npy',
        valid_checksum='9691cfd3bb4714398fe4f431b3124e26',
        test='images/patch_references_test.npy',
        test_checksum='481e1407800e940cef3f4ae9c9de21a8',
        load_images=True, load_train=True, load_valid=True, load_test=True,
        debug_outputs=False, set_access_rights=False):
    """Downloads the images of the GAPs dataset. Please enter a valid login."""
    if login == 'skip':
        msg = 'could not load chunk'
        msg2 = 'you must download the dataset first by entering '
        msg2 += 'a valid login'
        msg3 = 'see http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/'
        print('ERROR: {}\nHINT: {}\nHINT: {}'.format(msg, msg2, msg3))
        return
    if version != 1.0:
        print('ERROR: currently only version 1.0 available')
        return
    if size != '64x64':
        print('ERROR: only patch size 64x64 available')
        print('HINT: other sizes will be available in later versions')
        return
    if load_images:
        _download_if_not_available(datadir, source + images, images_checksum,
                                   login, debug_outputs)
        _check_file(os.path.join(datadir, images), debug_outputs)
    if load_train:
        _download_if_not_available(datadir, source + train, train_checksum,
                                   login, debug_outputs)
        _check_file(os.path.join(datadir, train), debug_outputs)
    if load_valid:
        _download_if_not_available(datadir, source + valid, valid_checksum,
                                   login, debug_outputs)
        _check_file(os.path.join(datadir, valid), debug_outputs)
    if load_test:
        _download_if_not_available(datadir, source + test, test_checksum,
                                   login, debug_outputs)
        _check_file(os.path.join(datadir, test), debug_outputs)
    if set_access_rights:
        os.system('chmod -R 777 ' + datadir)

