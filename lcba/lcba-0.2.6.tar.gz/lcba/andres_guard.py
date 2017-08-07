#!/usr/bin/env python
# coding: utf-8
import os
import sys
import util

################################################
#AndResGuard 使用7zip和zipalign来压缩资源
#fixme 通过identify 来定位资源的要添加到白名单
###############################################
def useAndResGuard(inputApk,outDir,configPath=None):
    commandLine = "java -jar "

    curPath = os.path.dirname(os.path.realpath(__file__))
    andResJarPath = os.path.join(curPath,'AndResGuard-cli-1.2.0.jar')
    if not os.path.exists(andResJarPath):
        print "AndResGuard-cli-1.2.0.jar not exists !!!"
        util.safeQuit(None, None)
    pass
    commandLine = commandLine + " %s "%andResJarPath

    if not os.path.exists(inputApk):
        print "inputApk:%s not exists !!!" %inputApk
        return
    pass
    commandLine = commandLine + (" %s "%inputApk)

    print "configPath:%s"%configPath
    if not configPath or not os.path.exists(configPath):
        configPath = os.path.join(curPath,'AndResGuard_config.xml')
    if not os.path.exists(configPath):
        print "AndResGuard_config.xml not exists!!! path:%s"%configPath
        util.safeQuit(None, None)
    pass
    commandLine = commandLine + " -config %s "%configPath

    commandLine = commandLine + " -out %s "%outDir

    output = os.popen('which 7za')
    zipTool =  output.read()
    if zipTool.strip() == '':
        print "you have not install 7za command!!!"
        print "window： 对于window应下载命名行版本，若将7za指定到环境变量，即无须设置。地址：http://sparanoid.com/lab/7z/download.html"
        print "linux：sudo apt-get install p7zip-full"
        print "mac：brew install p7zip"
        util.safeQuit(None, None)
    pass

    zipAlign_path = os.path.join(curPath,'zipalign')
    if not os.path.exists(zipAlign_path):
        print "not find zipalign tools,zipalign may in your $ANDROID_SDK/build-tools/25.0.1/zipalign"
        print "please config const.ZIPALIGN_PATH !!!"
        util.safeQuit(None, None)
    pass
    commandLine = commandLine + " -zipalign %s "%zipAlign_path

    # print commandLine
    # (status, output) = commands.getstatusoutput(commandLine)
    # print status,output
    print "###############################"
    print "Now begin sign and zipalign : %s"%commandLine
    print "###############################"
    os.system(commandLine)
# output = os.popen(commandLine)
# print output.read()
pass

def main():
    inputApk = '/Users/tory/working/Codes/JUMEI/android/app/build/outputs/apk/app-debug.apk'
    outDir = '/Users/tory/working/Codes/JUMEI/android/lcba/app'
    outDir = os.path.join(outDir,"JumeiOut")
    useAndResGuard(inputApk,outDir)
pass

if __name__ == '__main__':
    main()