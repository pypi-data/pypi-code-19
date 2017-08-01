# -*- coding=utf-8 -*-
import os
import shutil
import struct
import zipfile


# 支持文件类型
# 用16进制字符串的目的是可以知道文件头是多少字节
# 各种文件头的长度不一样，少半2字符，长则8字符
def typeList():
    return {
        "52617221": "EXT_RAR",
        "504B0304": "EXT_ZIP",
        # 'TEXT'
    }


# 字节码转16进制字符串
def bytes2hex(bytes):
    num = len(bytes)
    hexstr = u""
    for i in range(num):
        t = u"%x" % bytes[i]
        if len(t) % 2:
            hexstr += u"0"
        hexstr += t
    return hexstr.upper()


# 获取文件类型
def check_file_type(filename):
    binfile = os.open(filename, 'rb') # 必需二制字读取
    tl = typeList()
    ftype = 'UNKNOWN'
    for hcode in tl.keys():
        numOfBytes = int(len(hcode) / 2) # 需要读多少字节
        binfile.seek(0) # 每次读取都要回到文件头，不然会一直往后读取
        hbytes = struct.unpack_from("B" * numOfBytes, binfile.read(numOfBytes)) # 一个 "B"表示一个字节
        f_hcode = bytes2hex(hbytes)
        if f_hcode == hcode:
            ftype = tl[hcode]
            break
    binfile.close()

    # if not ftype:
    #     if is_text_file(filename):
    #         ftype = 'TEXT'
    return ftype

# 获取文件大小
def get_file_size(path):
    try:
        size = os.path.getsize(path)
        return size
    except Exception as err:
        print(err)


def unzip_file(zipfilename, unziptodir):
    """
    | ##@函数目的: 解压zip文件到指定目录
    | ##@参数说明：zipfilename为zip文件路径，unziptodir为解压文件后的文件目录
    | ##@返回值：无
    | ##@函数逻辑：
    """
    if not os.path.exists(unziptodir):
        os.makedirs(unziptodir)

    zfobj = zipfile.ZipFile(zipfilename)
    for name in zfobj.namelist():
        name = name.replace('\\', '/')

        if name.endswith('/'):
            p = os.path.join(unziptodir, name[:-1])
            if os.path.exists(p):
                # 如果文件夹存在，就删除之：避免有新更新无法复制
                shutil.rmtree(p)
            os.mkdir(p)
        else:
            ext_filename = os.path.join(unziptodir, name)
            ext_dir = os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir):
                os.mkdir(ext_dir)
            outfile = open(ext_filename, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()
