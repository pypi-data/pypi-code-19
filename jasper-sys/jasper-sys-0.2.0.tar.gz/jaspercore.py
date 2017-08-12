#!/usr/bin/env python3

import os
import json
import logging
import psutil
from argparse import ArgumentParser
from sys import stdout
from threading import Thread
from signal import SIGTERM
from subprocess import getstatusoutput
from time import sleep
from bottle import Bottle


__version__ = '0.2.0'

logger = logging.getLogger('jaspercore')


# Initialize logging facility
if stdout.isatty():
	logging.basicConfig(format='[*] %(asctime)s : %(levelname)s : %(module)s : %(message)s',  level=getattr(logging, 'INFO'))
else:
	logging.basicConfig(format='[*] %(asctime)s : %(levelname)s : %(module)s : %(message)s',  level=getattr(logging, 'INFO'), filename='/var/log/jasper-core.log')


class JasperCore(object):

	def __init__(self, filepath, callback_table=dict(), port=5237, start_all=False, restarts_no=-1):
		logger.info('JASPER CORE ONLINE [PID {0}]'.format(os.getpid()))
		self.__port = port
		self.__restarts_no = restarts_no
		self.__callback_table = callback_table
		with open(filepath) as f:
			self.__modules = json.load(f)
		logger.info('Loaded conf')
		for module in self.__modules:
			self.__modules[module]['pid'] = self.__grep_pid(module)
			self.__modules[module]['task_need_stop'] = False
		if start_all:
			self.__start_all()
		self.__bottle_app = Bottle()
		self.__set_routes()
		self.__bottle_app.run(host='0.0.0.0', port=self.__port)

	def __set_routes(self):
		self.__bottle_app.route('/getall', callback=self.__APIgetall)
		self.__bottle_app.route('/start/<module>', callback=self.__APIstart)
		self.__bottle_app.route('/stop/<module>', callback=self.__APIstop)
		self.__bottle_app.route('/status/<module>', callback=self.__APIstatus)

	def __spawn_thread(self, module):
		thread = Thread(target=self.__monit_module, args=(module,))
		thread.daemon = True
		thread.start()

	def __monit_module(self, module):
		'''Start `module` in another process'''
		logger.info('Starting ' + module)
		remaining_restarts = self.__restarts_no
		while True:
			pid = os.fork()
			if pid < 0:
				self.__modules[module]['pid'] = pid
			if pid == 0:
				os.setsid()
				try:
					os.execv(self.__modules[module]['command'].split()[0], self.__modules[module]['command'].split())
					#os.execv(find(module+'.py'), [module+'.py'] + self.__modules[module]['args'])
				except:
					logger.error('execv failed (module \'{0}\')'.format(module))
					# $$$ CALLBACK "exec_fail"
					if 'exec_fail' in self.__callback_table and callable(self.__callback_table['exec_fail']):
						self.__callback_table['exec_fail'](module)
					exit(1)
			else:
				sleep(1)
				self.__modules[module]['pid'] = pid
				# $$$ CALLBACK "start"
				if 'start' in self.__callback_table and callable(self.__callback_table['exec_fail']):
					self.__callback_table['start'](module)
				if self.__modules[module]['restart_on_crash']:
					os.waitpid(pid, 0)
					if self.__modules[module]['task_need_stop']:
						return
					else:
						if remaining_restarts != 0:
							sleep(15)
							logger.info('Restarting ' + module)
							remaining_restarts -= 1
							# $$$ CALLBACK "restart"
							if 'restart' in self.__callback_table and callable(self.__callback_table['restart']):
								self.__callback_table['restart'](module)
						else:
							# $$$ CALLBACK "stop_restart"
							if 'stop_restart' in self.__callback_table and callable(self.__callback_table['stop_restart']):
								self.__callback_table['stop_restart'](module)
							return
				else:
					return

	def __grep_pid(self, module):
		'''Get pid of `module` using ps and grep'''
		output = getstatusoutput('ps aux | grep -v grep | grep {0}'.format(module+'.py'))
		if output[0] == 0 and len(output[1].splitlines()) == 1:
			return int(output[1].split()[1])
		else:
			output = getstatusoutput('ps | grep -v grep | grep {0}'.format(module+'.py'))
			if output[0] == 0 and len(output[1].splitlines()) == 1:
				return int(output[1].split()[0])
			elif len(output[1].splitlines()) > 1:
				return -2
			else:
				return -1

	def __start_all(self):
		'''Start all the modules in `modules` dictionary'''
		for module in self.__modules:
			if self.__modules[module]['start_on_boot']:
				if self.__modules[module]['pid'] < 0:
					self.__spawn_thread(module)
					sleep(2)
					if self.__modules[module]['pid'] >= 0:
						message = '{0} started [PID {1}]'.format(module, self.__modules[module]['pid'])
					else:
						message = 'ERROR {0} failed starting'.format(module)
				else:
					message = '{0} is already running'.format(module)
				logger.info(message)

	def __APIgetall(self):
		return self.__modules

	def __APIstart(self, module):
		if self.__modules[module]['pid'] < 0:
			self.__modules[module]['task_need_stop'] = False
			self.__spawn_thread(module)
			sleep(2)
			if self.__modules[module]['pid'] >= 0:
				return {'module': module, 'status': 'running', 'pid': self.__modules[module]['pid']}
			else:
				return {'module': module, 'status': 'error', 'message': '{} failed starting.'.format(module)}
		else:
			return {'module': module, 'status': 'error', 'message': '{} is already runnning.'.format(module)}

	def __APIstop(self, module):
		if module == 'all':
			for module in self.__modules:
				self.__modules[module]['task_need_stop'] = True
			for module in self.__modules:
				counter = 0
				while self.__grep_pid(module) >= 0:
					try:
						os.kill(self.__modules[module]['pid'], SIGTERM)
						self.__modules[module]['pid'] = self.__grep_pid(module)
						# $$$ CALLBACK "stop"
						if 'stop' in self.__callback_table and callable(self.__callback_table['stop']):
							self.__callback_table['stop'](module)
					except:
						if counter > 3:
							break
						else:
							counter += 1
							pass
		elif self.__modules[module]['pid'] >= 0:
			self.__modules[module]['task_need_stop'] = True
			try:
				os.kill(self.__modules[module]['pid'], SIGTERM)
			except:
				pass
			sleep(2)
			self.__modules[module]['pid'] = self.__grep_pid(module)
			if self.__modules[module]['pid'] < 0:
				message = {'module': module, 'status': 'stopped'}
				# $$$ CALLBACK "stop"
				if 'stop' in self.__callback_table and callable(self.__callback_table['stop']):
					self.__callback_table['stop'](module)
			else:
				message = {'module': module, 'status': 'error', 'message': '{} failed stopping.'.format(module)}
		else:
			message = {'module': module, 'status': 'error', 'message': '{} is not running.'.format(module)}
		return message

	def __APIstatus(self, module):
		pid = self.__grep_pid(module)
		self.__modules[module]['pid'] = pid
		if pid < 0:
			message = {'module': module, 'status': 'stopped'}
		else:
			message = {'module': module, 'status': 'running', 'pid': pid}
		return message


if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument('modules', type=str)
	parser.add_argument('--start-all', action='store_true')
	args = parser.parse_args()
	jasper = JasperCore(args.modules, start_all=args.start_all)
