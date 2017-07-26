from utils import Utils
import logging
l = logging.getLogger(__name__)
import os,shutil,uuid,re


class FileManager(Utils):
    savepath = "/tmp/finale"
    tmppath = "/tmp"
    myconf = ['savepath','tmppath']

    def __init__(self):
        pass

    @classmethod
    def saveToTmp(cls,requestfile):
        infile = requestfile.file
        file_path = os.path.join(cls.tmppath, str(uuid.uuid4()) + str(requestfile.name) )
        l.debug("FileManager.saveToTmp path={path}".format(path=file_path))
        temp_file_path = file_path + '~'
        output_file = open(temp_file_path, 'wb')

        infile.seek(0)
        while True:
            data = infile.read(2<<16)
            if not data:
                break
            output_file.write(data)
        output_file.close()
        os.rename(temp_file_path, file_path)
        return file_path

    @classmethod
    def moveToDestination(cls,source,filename,subfolder=""):
        target = os.path.join(cls.savepath,subfolder,filename)
        l.debug("target filename:{target}".format(target=target))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))

        os.rename(source,target)
        return target



    @classmethod
    def deleteFile(cls,file):
        os.remove(file)

