#!/usr/bin/env python3

import curses
import requests
import json
import shutil
import traceback
from argparse import ArgumentParser
from time import sleep
from threading import Thread, Semaphore


__version__ = '0.2.1'
tsize = shutil.get_terminal_size()


class JasperCoreController:

	def __init__(self, args):
		self.__HOST = args.connect
		self.__PORT = 5237
		self.__NEED_EXIT = False
		self.__sem = Semaphore()
		self.__poll_rate = 5		# seconds
		self.__footbar_message_remaining = 10000
		self.modules = dict()
		self.focus = -1
		curses.wrapper(self.main)

	@property
	def BASE_URL(self):
		return 'http://{host}:{port}'.format(host=self.__HOST, port=self.__PORT)

	def refresh_modules(self, stdscr):
		while True:
			try:
				response = requests.get(self.BASE_URL + '/getall')
				response.raise_for_status()
				self.__sem.acquire()
				self.modules = response.json()
				self.__sem.release()
				sleep(self.__poll_rate)
			except requests.exceptions.HTTPError as error:
				stdscr.clear()
				stdscr.addstr(0, 0, '{} - {}'.format(response.status_code, response.reason), curses.A_STANDOUT)
				stdscr.refresh()
				sleep(3)
			except Exception as error:
				stdscr.clear()
				stdscr.addstr(0, 0, str(error), curses.A_STANDOUT)
				stdscr.refresh()
				sleep(3)

	def key_handler(self, key, stdscr):
		if key == curses.KEY_UP:
			self.focus -= 1
			if self.focus <= -1:
				self.focus = -1
		elif key == curses.KEY_DOWN:
			self.focus += 1
			self.__sem.acquire()
			if self.focus >= len(self.modules):
				self.focus = len(self.modules) - 1
			self.__sem.release()
		elif key == ord('q'):
			self.__NEED_EXIT = True
		elif key == ord('s'):
			# start/stop
			self.toggle_module(stdscr)

	def toggle_module(self, stdscr):
		if self.focus > -1:
			curses.flash()
			try:
				self.__sem.acquire()
				response = requests.get(self.BASE_URL + '/status/{}'.format(sorted(self.modules)[self.focus]))
				response.raise_for_status()
				data = response.json()
				if data['status'] == 'stopped':
					response = requests.get(self.BASE_URL + '/start/{}'.format(sorted(self.modules)[self.focus]))
				elif data['status'] == 'running':
					response = requests.get(self.BASE_URL + '/stop/{}'.format(sorted(self.modules)[self.focus]))
				else:
					stdscr.addstr(tsize.lines - 1, 0, 'ERROR in data[\'status\']', curses.A_STANDOUT)
					stdscr.refresh()
					self.__footbar_message_remaining = 10000
					return
				response.raise_for_status()
				data = response.json()
				if data['status'] == 'running':
					string = '{} is running with pid {}'.format(sorted(self.modules)[self.focus], data['pid'])
				elif data['status'] == 'stopped':
					string = '{} stopped'.format(sorted(self.modules)[self.focus])
				elif data['status'] == 'error':
					string = data['message']
				stdscr.addstr(tsize.lines - 1, 0, string, curses.A_STANDOUT)
				stdscr.refresh()
				self.__footbar_message_remaining = 10000
			except requests.exceptions.HTTPError as error:
				stdscr.clear()
				stdscr.addstr(0, 0, '{} - {}'.format(response.status_code, response.reason), curses.A_STANDOUT)
				stdscr.refresh()
				sleep(3)
			except Exception as e:
				stdscr.clear()
				stdscr.addstr(0, 0, str(traceback.format_exc()), curses.A_STANDOUT)
				stdscr.refresh()
				sleep(3)
			self.__sem.release()

	def print_table_content(self, stdscr):
		line = 4
		self.__sem.acquire()
		for module in sorted(self.modules):
			module_str = '{}'.format(module)
			while len(module_str) < tsize.columns / 4 + 5:
				module_str += ' '
			if self.modules[module]['pid'] >= 0:
				module_str += '{}'.format(self.modules[module]['pid'])
			else:
				module_str += '-'
			while len(module_str) < tsize.columns / 2 + 5:
				module_str += ' '
			module_str += '{}'.format(self.modules[module]['start_on_boot'])
			while len(module_str) < tsize.columns - len('Restart-on-crash'):
				module_str += ' '
			module_str += '{}'.format(self.modules[module]['restart_on_crash'])
			while len(module_str) < tsize.columns:
				module_str += ' '
			if line - 4 == self.focus:
				stdscr.addstr(line, 0, module_str, curses.A_STANDOUT)
			else:
				stdscr.addstr(line, 0, module_str)
			line += 1
		#stdscr.addstr(tsize.lines - 1, 0, ' '.join([' ' for i in range(tsize.columns - 2)]))
		self.__footbar_message_remaining -= 1
		if self.__footbar_message_remaining < 0:
			self.__footbar_message_remaining = -1
			stdscr.delch(tsize.lines - 1, 0)
		self.__sem.release()
		stdscr.refresh()

	def main(self, stdscr):
		curses.curs_set(0)
		curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
		stdscr.nodelay(1)
		# Start refesh thread
		self.__refresh_thread = Thread(target=self.refresh_modules, args=(stdscr, ))
		self.__refresh_thread.daemon = True
		self.__refresh_thread.start()
		# Set up top string
		top_string = 'JasperCore Controller v{} $ s Start/Stop | c Restart-on-crash [N/A] | q Quit'.format(__version__)
		while len(top_string) < tsize.columns:
			top_string = top_string.replace('$', '$ ')
		top_string = top_string.replace('$', ' ')
		stdscr.addstr(0, 0, top_string, curses.color_pair(1))
		stdscr.addstr(2, 0, 'Module', curses.A_BOLD)
		stdscr.addstr(2, int(tsize.columns / 4) + 5, 'PID', curses.A_BOLD)
		stdscr.addstr(2, int(tsize.columns / 2) + 5, 'Start-on-boot', curses.A_BOLD)
		stdscr.addstr(2, tsize.columns - len('restart on crash'), 'Restart-on-crash', curses.A_BOLD)
		stdscr.addstr(3, 0, ''.join(['-' for i in range(tsize.columns)]))
		stdscr.refresh()
		# Main interface
		while True:
			self.print_table_content(stdscr)
			c = stdscr.getch()
			self.key_handler(c, stdscr)
			if self.__NEED_EXIT:
				break


def main():
	parser = ArgumentParser('jasperctl')
	parser.add_argument('-c', '--connect', type=str, default='localhost')
	args = parser.parse_args()
	ctrl = JasperCoreController(args)


if __name__ == '__main__':
	main()
