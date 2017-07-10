#!/usr/bin/env python
#-*- coding: utf-8 -*-
#Author: Colin
#Date: 2017-01-10
#Desc: 定义发送邮件的公共函数
#


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from colinws.colinwsLogs import printLog, warnLog
import smtplib
import os
import sys


class sendEmail():
	"""
	class for send out email by python.
	"""
	def __help(self):
		print("""

		you need excute below commands on you Linux system:
			export MAILHOST='smtp.xxx.com'
			export MAILUSER='XXX@mail.com'
			export MAILPASSWD='xxxxxxxxx'	

		""")


	def __init__(self, subject, content, mailto, attachment=None, images=None):
		"""
		initialize for class
		partA:
			get mail host/user/password from system variables 
			make sure you have added  these commands in /root/.bashrc file under centos

			export MAILHOST='smtp.xxx.com'
			export MAILUSER='XXX@mail.com'
			export MAILPASSWD='xxxxxxxxx'

		partB:
			self get params from class		
		"""
		

		## get system variables about mail
		if os.getenv('MAILHOST') is None or os.getenv('MAILUSER') is None or os.getenv('MAILPASSWD') is None:
			self.__help()
			sys.exit()
		else:
			self.MAILHOST = os.getenv('MAILHOST')
			self.MAILUSER = os.getenv('MAILUSER')
			self.MAILPASSWD = os.getenv('MAILPASSWD')
	

		self.subject = subject
		self.content = content
		self.mailto = mailto
		self.attachment = attachment		
		self.images = images 


	def __addIMG(self, src, imgid):
		"""
		params:
			src: the image filename with absolute or relative path
			imgid: for image object add_header function, the second param
		"""

		with open(src, 'rb') as fp:
			msgImage = MIMEImage(fp.read())
			msgImage.add_header('Content-ID', imgid)
			return msgImage


	def __addAttach(self, src):
		"""
		params:
			src: the attachment filename with absolute or relative path
		"""

		realname = os.path.basename(src)
		with open(src, 'rb') as fp:
			msgAttach = MIMEText(fp.read(), 'base64', 'utf-8')
			msgAttach['Content-Type'] = 'application/octet-stream'
			msgAttach['Content-Disposition'] = 'attachment; filename=' + str(realname)
			return msgAttach


	def sendMsg(self):
		"""
		send out email function
		"""
		
		msg = MIMEMultipart('related')
		
		msgContent = MIMEText(self.content, 'html', 'utf-8')
		msg.attach(msgContent)

		if self.attachment:
			if isinstance(self.attachment, list):
				for msgfile in self.attachment:
					msg.attach(self.__addAttach(msgfile))
		
		if self.images:
			if isinstance(self.images, list):
				for msgImage in self.images:
					msg.attach(self.__addIMG(msgImage['file'],msgImage['nameflag'] ))
					
		msg['Subject'] = self.subject
		msg['From'] = self.MAILUSER
		msg['To'] = self.mailto

		try:
			smtp = smtplib.SMTP()
			smtp.connect(self.MAILHOST)
			smtp.login(self.MAILUSER, self.MAILPASSWD)
			smtp.sendmail(self.MAILUSER, self.mailto.split(','), msg.as_string())
			smtp.close()
			printLog('send successfully!')
		except Exception as e:
			senderr = str(e)
			warnLog(senderr)
