#encoding:utf-8
from fdfs_client.client import *

import zipfile
import os.path
import os


class ZFile(object):
    def __init__(self, filename, mode='r', basedir=''):
        self.filename = filename
        self.mode = mode
        if self.mode in ('w', 'a'):
            self.zfile = zipfile.ZipFile(filename, self.mode, compression=zipfile.ZIP_DEFLATED)
        else:
            self.zfile = zipfile.ZipFile(filename, self.mode)
        self.basedir = basedir
        if not self.basedir:
            self.basedir = os.path.dirname(filename)

    def addfile(self, path, arcname=None):
        path = path.replace('//', '/')
        if not arcname:
            if path.startswith(self.basedir):
                arcname = path[len(self.basedir):]
            else:
                arcname = ''
        self.zfile.write(path, arcname)

    def addfiles(self, paths):
        for path in paths:
            if isinstance(path, tuple):
                self.addfile(*path)
            else:
                self.addfile(path)

    def close(self):
        self.zfile.close()

    def extract_to(self, path):
        fileList = []
        for p in self.zfile.namelist():
            fileList.append(p)
            self.extract(p, path)
        return fileList

    def extract(self, filename, path):
        if not filename.endswith('/'):
            f = os.path.join(path, filename)
            dir = os.path.dirname(f)
            if not os.path.exists(dir):
                os.makedirs(dir)
            open(f, 'wb').write(self.zfile.read(filename))

class FileManager(object):
    def __init__(self,clientFile=''):
        self.__domainName = 'http://www.igap.cc/'
        if clientFile == '':
            self.__client_file = os.getcwd() + '/Conf/fastDfsClient.conf'
        else:
            self.__client_file = clientFile

    def uploadToFastDFS(self,sourceFile):
        try:
            client = Fdfs_client(self.__client_file)
            ret_upload = client.upload_by_filename(sourceFile)
        except Exception as e:
            return None
        if ret_upload.get('Status','') == 'Upload successed.':
            return self.__domainName + ret_upload['Remote file_id']
        else:
            return None

    def downloadFile(self,sourceFile,destFileName):
        client = Fdfs_client(self.__client_file)
        j = len(self.__domainName)
        s = sourceFile[:j].lower()
        if s == self.__domainName.lower():
            sFile = sourceFile[j:]
        else:
            sFile = sourceFile
        ret_download = client.download_to_file(destFileName, sFile)
        if ret_download.get('Download size',''):
            return destFileName
        else:
            return None

    def directoryToZip(self,zfile,files):
        result = zfile
        try:
            z = ZFile(zfile, 'w')
            z.addfiles(files)
            z.close()
        except:
            result = None
        return result

    def zipToDirectory(self,zfile, path=''):
        try:
            z = ZFile(zfile)
            result = z.extract_to(path)
            z.close()
            if path.endswith('/'):
                result = [path + f for f in result]
            else:
                result = [path + '/' + f for f in result]
        except:
            result = None
        return result

    def mkdirs(self,dirs):
        if not os.path.exists(dirs):
            os.makedirs(dirs)

    def divisionFileName(self,fileAllPath=''):
        i = fileAllPath.rfind('/')
        return fileAllPath[i + 1:]

if __name__ == '__main__':
    fileManager = FileManager('/root/work/testing-platform-execute/Conf/fastDfsClient.conf')
    # result = fileManager.uploadToFastDFS('/data/02.jmx')
    # print(result)
    #
    # fileName = fileManager.directoryToZip('/data/02.zip',['/data/02.jmx'])
    # print(fileName)
    result = fileManager.uploadToFastDFS('/data/001.zip')
    print(result)
#     #
#     # result = fileManager.downloadFile(result,'/data/4.txt')
#     # print(result)
#     files = ['/data/01.txt','/data/02.jpg','/data/03.jpg','/data/04.jpg']
#     fileName = fileManager.directoryToZip('/data/1.zip',files)
#     print(fileName)
#     fileList = fileManager.zipToDirectory('/data/1.zip','/data/1')
#     print(fileList)


