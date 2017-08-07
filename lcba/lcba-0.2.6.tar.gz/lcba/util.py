#!/usr/bin/env python             
# coding: utf-8
import hashlib
import globalVar as glo
import os
import shutil
import smtplib
from email.mime.text import MIMEText


################################################
#删除某个文件特定的一行
###############################################
def deleteLine(srcFile, targetString):
	with open(srcFile, 'r') as f:
		#print "open:%s" % srcFile
		with open(srcFile+".new", 'w') as g:
			#print "open:new file" 
			for line in f.readlines():
				if targetString not in line:             
					g.write(line)
				else :
					print "delete line: %s" %targetString
			pass
		pass
	pass
	if os.path.exists(srcFile+".new"):
		shutil.move(srcFile+".new", srcFile)
	pass	
pass

################################################
#向某个文件写入特定的一行
###############################################
def writeLine(srcFile, targetString):
	f=open(srcFile,'a')
	f.write(targetString)
	f.write("\n")
	f.close()
pass

################################################
#md5 计算方案一直接读取计算，但是会消耗大量内存
###############################################
def generateMd5(filename): 
	if not os.path.isfile(filename):
		print ("%s is not a file!!!"%(filename))
		return
         
	fd = open(filename,"r")  
	fcont = fd.read()
	fd.close()
	fmd5 = hashlib.md5(fcont)
	md5 = fmd5.hexdigest()
	#print ("%s --MD5--> %s"%(filename,md5))
	return md5
pass

################################################
#md5 计算方案二直接读取计算最大占用8K内存
###############################################
def generateMd5_2(fname):  
    """ 计算文件的MD5值 """  
    def read_chunks(fh):  
        fh.seek(0)  
        chunk = fh.read(8096)  
        while chunk:  
            yield chunk  
            chunk = fh.read(8096)  
        else: #最后要将游标放回文件开头  
            fh.seek(0)  
    m = hashlib.md5()  
    if isinstance(fname, basestring) and os.path.exists(fname):  
        with open(fname, "rb") as fh:  
            for chunk in read_chunks(fh):  
                m.update(chunk)  
    #上传的文件缓存 或 已打开的文件流  
    elif fname.__class__.__name__ in ["StringIO", "StringO"] or isinstance(fname, file):  
        for chunk in read_chunks(fname):  
            m.update(chunk)  
    else:  
        return ""  
    return m.hexdigest()
pass

################################################
#检查gradle 任务
###############################################
def haveGradleTask(workPath,gradlewPath,taskName):
	if not gradlewPath:
		print "not find work path!!!"
		return False

	tmpFilePath = os.path.join(workPath,"tasks.new")
	os.chdir(r'%s'%workPath)
	print "haveGradleTask()?...%s ??? wait..."%taskName
	cmd = '%s tasks --all > %s'%(gradlewPath,tmpFilePath)
	#print cmd
	os.system(cmd)
	ret = False

	if not os.path.exists(tmpFilePath):
		print "not find work path!!!-->%s"%tmpFilePath
		return ret
	pass
	with open(tmpFilePath) as f:
		for line in f.readlines():
			if taskName in line:
				print "find gradlew task :%s"%taskName
				ret = True
				break
			pass
		pass
	pass

	if os.path.exists(tmpFilePath):
		os.remove(tmpFilePath)
	pass
	return ret
pass

################################################
#向资源文件写入一行内容，并且以"</resources>"结尾
###############################################
def writeIdsLine(srcFile,targetString):
	deleteLine(srcFile,"</resources>")
	deleteLine(srcFile,targetString)
	writeLine(srcFile,targetString)
	writeLine(srcFile,"</resources>")
pass

################################################
#创建资源文件，并且以写入
# "<?xml version="1.0" encoding="UTF-8"?>
# <resources>
# </resources>"内容
###############################################
def createIdsFile(filePath):
	if os.path.exists(filePath):
		pass
	else:
		f = open(filePath,'w')
		f.close()
		writeLine(filePath,'<?xml version="1.0" encoding="UTF-8"?>')
		writeLine(filePath,"<resources>")
		writeLine(filePath,"</resources>")
	pass
pass

################################################
#安全退出
###############################################
def safeQuit(signum, frame):
	print "###############################"
	print "Now safely Quit:%s"%glo.getValue('_reason')
	print "###############################"

	output = os.popen('find ./ -name "*.tiny" | xargs rm -rf')
	output = os.popen('rm -rf *.new')

	mailto_list = []
	mailto_list.append('xiangc@jumei.com')
	mailto_list.append('feiy1@jumei.com')
	title = glo.getValue("_title")
	if glo.getValue("_send_mail") and title:
		content = glo.getValue('_content','you branch need local lint check')
		content += (" where branch is :%s"%glo.getValue('branch'))
		send_mail(title,content,mailto_list)
	pass
	# output = os.popen('find ./ -name "*.new" | xargs rm -rf')
	# find ./ -name "*.tiny" | xargs rm -rf
	#find ./ -name "*.new" | xargs rm -rf
	#find ./ -name "*.orig" | xargs rm -rf
	exit()
pass

def send_mail(title,content, mailto_list):
	#############
	#要发给谁，这里发给1个人
	#####################
	#设置服务器，用户名、口令以及邮箱的后缀
	mail_host="mail.jumei.com"
	# mail_user="pythonm"
	# mail_pass="Wuhang0508."
	mail_postfix="jumei.com"
	mail_user="feiy1"
	mail_pass="113456Yf@@"
	######################
	'''''
    to_list:发给谁
    sub:主题
    content:内容
    send_mail("aaa@126.com","sub","content")
    '''
	if len(mailto_list) == 0:
		return False

	me=mail_user+"<"+mail_user+"@"+mail_postfix+">"
	msg = MIMEText(content,_charset='UTF-8')
	msg['Subject'] = title
	msg['From'] = me
	msg['To'] = ";".join(mailto_list)
	try:
		s = smtplib.SMTP()
		s.connect(mail_host)
		s.login(mail_user,mail_pass)
		s.sendmail(me, mailto_list, msg.as_string())
		s.close()
		return True
	except Exception, e:
		print str(e)
		return False

################################################
#主函数
###############################################
def main():
	safeQuit(None,None)
pass

if __name__ == '__main__':
	main()