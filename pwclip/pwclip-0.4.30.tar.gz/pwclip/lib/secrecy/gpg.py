#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
gpgtool module
"""

# (std)lib imports
from os import X_OK, access, getcwd, environ, path, name as osname

from getpass import getpass

from psutil import process_iter as piter

from tkinter import TclError

from getpass import getpass

from gnupg import GPG

# local imports
from colortext import blu, red, yel, bgre, tabd, abort, error, fatal

from system import xinput, xyesno, xmsgok

class GPGTool(object):
	"""
	gnupg wrapper-wrapper :P
	although the gnupg module is quite handy and the functions are pretty and
	useable i need some modificated easing functions to be able to make the
	main code more easy to understand by wrapping multiple gnupg functions to
	one - also i can prepare some program related stuff in here
	"""
	dbg = None
	__ppw = None
	homedir = path.join(path.expanduser('~'), '.gnupg')
	__bindir = '/usr/bin'
	__gpgbin = 'gpg2'
	if osname == 'nt':
		homedir = path.join(
            path.expanduser('~'), 'AppData', 'Roaming', 'gnupg')
		__bindir = 'C:\Program Files (x86)\GNU\GnuPG'
		__gpgbin = 'gpg2.exe'
	_binary = path.join(__bindir, __gpgbin)
	if not path.isfile(_binary) or not access(_binary, X_OK):
		raise RuntimeError('%s needs to be executable'%binary)
	_keyserver = ''
	dmcfg = path.join(homedir, 'dirmngr.conf')
	agentinfo = path.join(homedir, 'S.gpg-agent')
	kginput = {}
	recvs = []
	def __init__(self, *args, **kwargs):
		for arg in args:
			if hasattr(self, arg):
				setattr(self, arg, True)
		for (key, val) in kwargs.items():
			if hasattr(self, key) and not isinstance(val, bool):
				setattr(self, key, val)
		if self.dbg:
			print(bgre(GPGTool.__mro__))
			print(bgre(tabd(GPGTool.__dict__, 2)))
			print(' ', bgre(self.__init__))
			print(bgre(tabd(self.__dict__, 4)))


	@property                # keyring <str>
	def keyring(self):
		if self.binary.endswith('.exe'):
			return path.join(self.homedir, 'pubring.gpg')
		return path.join(self.homedir, 'pubring.kbx') \
            if self.binary.endswith('2') else path.join(
                self.homedir, 'pubring.gpg')

	@property                # secring <str>
	def secring(self):
		if self.binary.endswith('.exe'):
			return path.join(self.homedir, 'secring.gpg')
		elif self.binary.endswith('2') and self.keyring.endswith('gpg'):
			return path.join(self.homedir, 'secring.gpg')
		return path.join(self.homedir, 'secring.kbx')

	@property                # dmcfg <str>
	def dmcfg(self):
		return self._dmcfg
	@dmcfg.setter
	def dmcfg(self, val):
		if path.exists(val):
			dmcfg = {}
			with open(dmcfg, 'r') as dfh:
				for ln in dfh.readlines():
					dmcfg[ln.split(' ')[0].strip()] = ln.split(' ')[1].strip()
		self._dmcfg = dmcfg

	@property                # binary <str>
	def binary(self):
		return self._binary
	@binary.setter
	def binary(self, val):
		self._binary = path.join(self.__bindir, val)

	@property                # _gpg_ <GPG>
	def _gpg_(self):
		"""object"""
		opts = ['--batch', '--always-trust']
		if osname != 'nt' and self.binary.rstrip('.exe').endswith('2'):
			opts.append('--pinentry-mode=loopback')
		elif osname == 'nt':
			if not self.__ppw:
				self.__ppw = xinput('enter passphrase')
			if self.__ppw is None:
				abort()
			opts.append('--passphrase="%s"'%self.__ppw)
		__g = GPG(
            keyring=self.keyring, secret_keyring=self.secring,
            gnupghome=self.homedir, gpgbinary=self.binary,
            use_agent=True, options=opts,
            verbose=1 if self.dbg else 0)
		if osname != 'nt':
			__g.encoding = 'utf-8'
		return __g

	@staticmethod
	def _passwd(rpt=False):
		"""
		password questioning function
		"""
		msg = 'enter passphrase: '
		tru = 'repeat that passphrase: '
		while True:
			try:
				if not rpt:
					return getpass(msg)
				__pwd = getpass(msg)
				if __pwd == getpass(tru):
					return __pwd
				error('passwords did not match')
			except KeyboardInterrupt:
				abort()

	def genkeys(self, **kginput):
		"""
		gpg-key-pair generator method
		"""
		if self.dbg:
			print(bgre(self.genkeys))
		kginput = kginput if kginput != {} else self.kginput
		if not kginput:
			error('no key-gen input received')
			return
		print(
            blu('generating new keys using:\n '),
            '\n  '.join('%s%s=  %s'%(blu(k),
                ' '*int(max(len(s) for s in kginput.keys())-len(k)+2),
                yel(v)
            ) for (k, v) in kginput.items()))
		if 'passphrase' in kginput.keys():
			if kginput['passphrase'] == 'nopw':
				del kginput['passphrase']
			elif kginput['passphrase'] == 'stdin':
				kginput['passphrase'] = self.__passwd(rpt=True)
		print(red('generating %s-bit keys - this WILL take some time'%(
            kginput['key_length'])))
		key = self._gpg_.gen_key(self._gpg_.gen_key_input(**kginput))
		if self.dbg:
			print('key has been generated:\n%s'%str(key))
		return key

	@staticmethod
	def __find(pattern, *vals):
		for val in vals:
			if isinstance(val, (list, tuple)) and \
			      [v for v in val if pattern in v]:
				#print(val, pattern)
				return True
			elif pattern in val:
				#print(val, pattern)
				return True

	def findkey(self, pattern='', **kwargs):
		typ = 'A' if not 'typ' in kwargs.keys() else kwargs['typ']
		secret = False if not 'secret' in kwargs.keys() else kwargs['secret']
		keys = {}
		pattern = pattern if not pattern.startswith('0x') else pattern[2:]
		for key in self._gpg_.list_keys():
			if pattern and not self.__find(pattern, *key.values()):
				continue
			for (k, v) in key.items():
				#print(k, v)
				if k == 'subkeys':
					#print(k)
					for sub in key[k]:
						#print(sub)
						short, typs, finger = sub
						#print(finger, typs)
						if typ == 'A' or (typ in typs):
							si = key[k].index(sub)
							ki = key[k][si].index(finger)
							kstr = self._gpg_.export_keys(
                                key[k][si][ki], secret=secret)
							#print(kstr)
							keys[finger] = {typs: kstr}
		return keys

	def export(self, *patterns, **kwargs):
		"""
		key-export method
		"""
		if self.dbg:
			print(bgre(self.export))
		typ = 'A' if not 'typ' in kwargs.keys() else kwargs['typ']
		secret = False if not 'secret' in kwargs.keys() else kwargs['secret']
		keys = dict((k, v) for (k, v) in self.findkey(**kwargs).items())
		if patterns:
			keys = dict((k, v) for p in list(patterns) \
                for (k, v) in self.findkey(p, **kwargs).items())
		return keys

	def _encryptwithkeystr(self, message, keystr, output):
		fingers = [
            r['fingerprint'] for r in self._gpg_.import_keys(keystr).results]
		return self._gpg_.encrypt(
            message, fingers, always_trust=True, output=output)

	def encrypt(self, message, *args, **kwargs):
		"""
		text encrypting function
		"""
		if self.dbg:
			print(bgre(self.encrypt))
		fingers = list(self.export())
		if self.recvs:
			fingers = list(self.export(*self.recvs, **{'typ': 'e'}))			
		if 'recipients' in kwargs.keys():
			fingers = list(self.export(*kwargs['recipients'], **{'typ': 'e'}))
		if 'keystr' in kwargs.keys():
			res = self._gpg_.import_keys(keystr).results[0]
			fingers = [res['fingerprint']]
		output = None if not 'output' in kwargs.keys() else kwargs['output']
		print(fingers)
		return self._gpg_.encrypt(
            message, fingers, always_trust=True, output=output)

	def decrypt(self, message, output=None):
		"""
		text decrypting function
		"""
		if self.dbg:
			print(bgre('%s\n  trying to decrypt:\n%s'%(self.decrypt, message)))
		c = 1
		try:
			while True:
				__plain = self._gpg_.decrypt(
                    message.strip(), always_trust=True,
					output=output, passphrase=self.__ppw)
				if __plain.ok:
					return __plain
				yesno = True
				if c > 3:
					yesno = False
					try:
						xmsgok('too many wrong attempts')
					except TclError:
						fatal('too many wrong attempts')
					exit(1)
				elif c >= 1 and c < 3:
					yesno = False
					try:
						yesno = xyesno('decryption failed - try again?')
					except TclError:
						yesno = True if str(input(
                            'decryption failed - retry? [Y/n]'
                            )).lower() in ('y', '') else False
				elif c > 1 and not self.__ppw:
					yesno = False
					try:
						yesno = xyesno('no passphrase entered, retry?')
					except TclError:
						yesno = True if str(input(
                            'no passphrase entered, retry? [Y/n]'
                            )).lower() in ('y', '') else False
				if not yesno:
					raise RuntimeError('cannot decrypt')
				c+=1
				try:
					self.__ppw = xinput('enter passphrase')
				except TclError:
					self.__ppw = self._passwd()
		except KeyboardInterrupt:
			abort()
