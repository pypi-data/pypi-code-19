#!/usr/bin/env python             
# coding: utf-8
import tinify
import os
import time
import shutil
import  util
from hashmap import HashMap
import lcba.globalVar as glo
from PIL import Image

# 常量: 服务器最大容错次数
MAX_SERVER_ERROR_COUNT = 3
# 常量: 图片最大容错次数
MAX_PIC_ERROR_COUNT = 3
# 常量:账号列表
ACCOUNT_KEY_LIST = [
    "WaNaNSYc84TNr8DZpgZFRo8QnxhSaV3L",  # use hongc@jumei.com register
    "tdSdRzIvicVO3oTfrXZ6374P7uyBx-Kf",  # use changqiangl@jumei.com register
    "Jltmnr4b7xkQedUyiza-v12FZpIOPG8O",  # use test1_jumei@mail.com register
    "tFrVjiAQyYshUKvGDGuCZZa0cmW_VuM9",  # use xiangc register
]

# 全局变量:服务器错误次数
serverErrorCount = 0
# 全局变量:单次图片错误次数
picErrorCount = 0
# 全局变量:当前帐号索引
curApiKeyIndex = 0

PLATFORM_ANDROID='_android'
PLATFORM_IOS = '_ios'
gJustCheck = None
gPlatForm = PLATFORM_ANDROID


# mac 安装python -m pip install --upgrade pip
# pip install --upgrade tinify
# 怎样使用请访问 https://tinypng.com/developers/reference/python
################################################
# 对图片进行实际压缩,请求tinyPng压缩图片 接受xxx.png和xxx.jpeg的图片
###############################################
def compressSingleTinypng(src, dest):
    try:
        # if方案一使用文件作为源
        source = tinify.from_file(src)
        source.to_file(dest)

    # elseif方案二使用文件buffer来作为源
    # with open("unoptimized.jpg", 'rb') as source:
    # source_data = source.read()
    # result_data = tinify.from_buffer(source_data).to_buffer()

    # elseif方案三使用url来作为源
    # source = tinify.from_url("https://cdn.tinypng.com/images/panda-happy.png")
    # source.to_file("optimized.jpg")
    # pass
    except tinify.AccountError, e:
        # 账号错误，请重试或者换账号
        # Verify your API key and account limit.
        print "The error message is: %s  index:%s" % (e.message, curApiKeyIndex)
        return -1
    except tinify.ClientError, e:
        # 不建议重试请求，可能是图片有问题
        # Check your source image and request options.
        print "The error picture is: %s" % src
        print "The error message is: %s" % e.message
        return -2
    except tinify.ServerError, e:
        # 建议重试请求；官方说法一般是几分钟之后会恢复
        # Temporary issue with the Tinify API.
        print "The error picture is: %s  server error count is:%s" % (src, picErrorCount)
        print "The error message is: %s" % e.message
        return -3
    except tinify.ConnectionError, e:
        # 检查网络连接或者重试
        # A network connection error occurred.
        print "The error picture is: %s  pic error count is:%s" % (src, picErrorCount)
        print "The error message is: %s" % e.message
        return -4
    except Exception, e:
        # 未知异常
        # Something else went wrong, unrelated to the Tinify API.
        print "The error picture is: %s " % src
        print "The error message is: %s" % e.message
        return -5
    return 0


pass


################################################
# 对图片进行逻辑压缩处理
###############################################
def compressTinypngLogic(src, dest, keyName, mintor_md5_filename):
    global picErrorCount
    global serverErrorCount
    global curApiKeyIndex

    # print "compressSinglePicLogic()...%s" %src
    if not src or not os.path.exists(src):
        print "src: %s not exists!!!"%src
        util.safeQuit(None,None)

    ret = compressSingleTinypng(src, dest)
    if 0 == ret:
        oldSize = os.path.getsize(src)
        newSize = os.path.getsize(dest)
        print "%s compressed from:%s to:%s -------->saving:%s" % (keyName, oldSize, newSize, oldSize - newSize)
        # 3，删除源文件，把新文件重新命名为源文件
        shutil.move(dest, src)
        # 1，在md5文件中删除老的一行，并把新的md5写入
        util.deleteLine(mintor_md5_filename, keyName)
        newMd5 = util.generateMd5_2(src)
        md5Line = "%s--MD5-->%s" % (keyName, newMd5)
        # print md5Line
        util.writeLine(mintor_md5_filename, md5Line)
    elif -1 == ret:
        curApiKeyIndex += 1
        validateApiKey(curApiKeyIndex)
        print "retry compressPic()..-1.src:%s" % src
        compressTinypngLogic(src, dest, keyName, mintor_md5_filename)
    elif -2 == ret:
        util.safeQuit(None, None)
    elif -3 == ret:
        if serverErrorCount >= MAX_SERVER_ERROR_COUNT:
            util.safeQuit(None, None)
        else:
            serverErrorCount += 1
            print "we will retry in 2 minute later!!"
            time.sleep(60 * 2)
            print "retry compressPic()..-3.src:%s" % src
            compressTinypngLogic(src, dest, keyName, mintor_md5_filename)
        pass
    elif -4 == ret:
        if picErrorCount >= MAX_PIC_ERROR_COUNT:
            util.safeQuit(None)
        else:
            picErrorCount += 1
            print "retry compressPic()..-4.src:%s" % src
            compressTinypngLogic(src, dest, keyName, mintor_md5_filename)
        pass
    elif -5 == ret:
        util.safeQuit(None, None)
    else:
        util.safeQuit(None, None)
        pass
pass


################################################
# 验证账户
###############################################
def validateApiKey(index):
    global curApiKeyIndex
    if index >= len(ACCOUNT_KEY_LIST):
        util.safeQuit(None, None)
        return
    print "validateApiKey()... %s" % ACCOUNT_KEY_LIST[index]
    try:
        tinify.key = ACCOUNT_KEY_LIST[index]
        tinify.validate
    except tinify.Error, e:
        # Validation of API key failed.
        print "The error message is: %s  index:%s" % (e.message, curApiKeyIndex)
        if index >= ACCOUNT_KEY_LIST.size():
            util.safeQuit(None, None)
            return
        else:
            curApiKeyIndex += 1
            validateApiKey(curApiKeyIndex)
        pass
    pass
pass

################################################
# 检查受监视的图片目录
###############################################
def checkMintorDir(app_dir,mintor_dir_path, mintor_md5_filepath,function_compress):
    print "checkMintorDir()...%s  from file: %s where module is:%s" % (mintor_dir_path, mintor_md5_filepath,app_dir)
    if not app_dir or not mintor_dir_path or not mintor_md5_filepath:
        print "###########ERROR###############"
        print "checkMintorDir param error app_dir:%s mintor_dir_path:%s mintor_md5_filepath:%s"%(app_dir,
                                                                                                mintor_dir_path,mintor_md5_filepath)
        return
    pass
    # 读区已经压缩过文件和md5到hashmap
    md5HashMap = HashMap()
    if os.path.exists(mintor_md5_filepath):
        for line in open(mintor_md5_filepath):
            # print line
            line = line.replace('\r', '').replace('\n', '').replace('\t', '')
            lineItems = line.rsplit('--MD5-->', 2)
            #print "%s   %s" %(lineItems[0],lineItems[1])
            md5HashMap.add(lineItems[0], lineItems[1])
        pass
    else:
        f = open(mintor_md5_filepath, 'w')
        f.close()
    pass

    # 遍历被监控的文件夹，计算新的md5值和老的md5Hashmap值是否相等
    for dirpath, dirnames, filenames in os.walk(mintor_dir_path):
        # print "dirpath:%s dirnames:%s filenames:%s" %(dirpath,dirnames,filenames)
        # if "build" not in dirpath and "intermediates" not in dirpath and "generated" not in dirpath and "outputs" not in dirpath and "gen" not in dirpath:
        #     continue
        for file in filenames:
            fullpath = os.path.join(dirpath, file)

            simplepath = fullpath.replace(app_dir, '')
            if simplepath and simplepath.startswith('/'):
                simplepath = simplepath[1:len(simplepath)]
            pass
            # print "this is: %s" %simplepath
            # 9.png 压缩了之后不能缩放
            if simplepath.endswith(".9.png"):
                print "ignore: %s" % simplepath
                continue

            if checkFormat(fullpath):
                oldMd5 = None
                try:
                    oldMd5 = md5HashMap.get(simplepath)
                except KeyError, e:
                    pass
                md5 = util.generateMd5_2(fullpath)
                print "\ncompressing %s oldMd5:%s md5:%s" % (simplepath, oldMd5, md5)
                if cmp(oldMd5, md5) == 0:
                    print "%s is already compressed!!! skiped" % simplepath
                else:
                    if gJustCheck:
                        title = "you have picture not compressed yet!!!"
                        content = "please local run:python lcba/lintCompress.py to compress Resources!!!"
                        print title
                        print content
                        glo.set_value('_reason',title)
                        glo.set_value('_title',title)
                        glo.set_value('_content',content)
                        util.safeQuit(None,None)
                    pass

                    #fixme local sdk 暂时只支持png
                    if function_compress.__name__ == compressPngquantLogic.__name__ and not fullpath.endswith(".png"):
                        print "############# ERROR ###########"
                        print "local sdk can't handle picture:%s"%fullpath
                        continue
                    #回调压缩函数
                    function_compress(fullpath, fullpath + ".tiny", simplepath, mintor_md5_filepath)
                    # 2，上传tinypng压缩图片
                    #compressTinypngLogic(fullpath, fullpath + ".tiny", simplepath, mintor_md5_filepath)
                pass
            pass
        pass
    pass
pass

#检查文件格式
def checkFormat(filePath):

    # ext = os.path.splitext(filePath)[1]
    if filePath.endswith(".9.png"):
        print "ignore: %s" % filePath
        return False
    elif filePath.endswith(".png"):
        img = Image.open(filePath)
        format = img.format
        if format and format.lower() == 'png':
            return True
        else:
            print "the file:%s endswith .png,but the format is:%s"%(filePath,format)
            util.safeQuit(None,None)
            return False
    elif filePath.endswith(".jpg") or filePath.endswith(".jpeg"):
        img = Image.open(filePath)
        format = img.format
        if format and format.lower() == 'jpeg':
            return True
        else:
            print "the file:%s endswith .jpg,but the format is:%s"%(filePath,format)
            util.safeQuit(None,None)
            return False
    pass

    return False
pass

#监测出该目录有多少个图片文件夹
def getPictureDirs(app_dir):
    mintordirPaths = []
    for dirpath, dirnames, filenames in os.walk(app_dir):
        # print "dirpath:%s dirnames:%s filenames:%s" %(dirpath,dirnames,filenames)
        if gPlatForm == PLATFORM_IOS:
            #fixme 这里处理ios和android 平台
            print "handle ios platform..."
            for dirname in dirnames:
                if dirname.endswith(".imageset"):
                    fullDirPath = os.path.join(dirpath, dirname)
                    print fullDirPath
                    mintordirPaths.append(fullDirPath)
                pass
            pass
        else:
            for dirname in dirnames:
                if "build" not in dirpath and "intermediates" not in dirpath and "generated" not in dirpath and "outputs" not in dirpath and "gen" not in dirpath:
                    if dirname.startswith("asserts") or dirname.startswith("drawable") or dirname.startswith("mipmap"):
                        fullDirPath = os.path.join(dirpath, dirname)
                        print fullDirPath
                        mintordirPaths.append(fullDirPath)
                    pass
                pass
            pass
        pass
    pass
    return mintordirPaths
pass

#使用在线tinypng的在线sdk 压缩方案;
def compressModule(inDir=None,outDir=None,accountList=None,just_check=False,platform=PLATFORM_ANDROID):
    if accountList:
        global ACCOUNT_KEY_LIST
        ACCOUNT_KEY_LIST.extend(accountList)
        try:
            validateApiKey(curApiKeyIndex)
        except Exception, exc:
            print exc
            util.safeQuit(None,None)

    if not inDir or not outDir or not os.path.exists(inDir):
        print "compressModule()...param error inDir:%s outDir:%s" %(inDir,outDir)
        return

    if not os.path.exists(outDir):
        os.makedirs(r'%s' % outDir)
    pass

    global gJustCheck
    gJustCheck = just_check

    global gPlatForm
    gPlatForm = platform

    mintordirPaths = getPictureDirs(inDir)
    if mintordirPaths:
        for mintor_dir_path in mintordirPaths:
            mintor_md5_path = os.path.join(outDir, 'picture_md5.txt')
            if accountList:
                #如果有账户列表使用tinypng在线压缩
                print "online compress!!!"
                checkMintorDir(inDir,mintor_dir_path, mintor_md5_path, compressTinypngLogic)
            else:
                #如果账户列表为空使用pngquant本地压缩图片
                print "local sdk compress!!!"
                checkMintorDir(inDir,mintor_dir_path, mintor_md5_path, compressPngquantLogic)
        pass
    pass
pass

#使用pngquant本地压缩图片
def compressPngquantLogic(src, dest, keyName, mintor_md5_filename):
    if not src or not os.path.exists(src):
        print "src: %s not exists!!!"%src
        util.safeQuit(None,None)

    curPath = os.path.dirname(os.path.realpath(__file__))
    pngquantPath = os.path.join(curPath,'pngquant')
    oldSize = os.path.getsize(src)
    if not os.path.exists(pngquantPath):
        print "pngquant execute file not exists !!!"
        util.safeQuit(None, None)
    pass
    commandLine = pngquantPath +" --force --quality 50-80 "+src +" --output "+src
    output = os.popen(commandLine)
    msg = output.read()
    if msg:
        print "############## ERROR ################"
        print "The picture:%s can't compress!!!"%src
        print msg
        util.safeQuit(None,None)
    else:
        newSize = os.path.getsize(src)
        print "local %s compressed from:%s to:%s -------->saving:%s" % (keyName, oldSize, newSize, oldSize - newSize)
        # 3，删除源文件，把新文件重新命名为源文件
        # shutil.move(dest, src)
        # 1，在md5文件中删除老的一行，并把新的md5写入
        util.deleteLine(mintor_md5_filename, keyName)
        newMd5 = util.generateMd5_2(src)
        md5Line = "%s--MD5-->%s" % (keyName, newMd5)
        # print md5Line
        util.writeLine(mintor_md5_filename, md5Line)
pass

################################################
# 主函数
###############################################
def main():
    curPath = '/Users/tory/working/Codes/JUMEI/android/app/'
    outDir = '/Users/tory/working/Codes/JUMEI/android/fine_resources/app/'
    # compressModule(inDir=curPath,outDir=outDir,accountList="sXzp30KfRZaf0NlWaQP0U3qEwQwoCl7s")
    compressModule(inDir=curPath,outDir=outDir)
pass

if __name__ == '__main__':
    main()
