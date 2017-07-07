#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

arguments = ['title', 'subtitle', 'sound', 'reply', 'actions', 'dropdownLabel', 'closeLabel', 'timeout',
	'group', 'activate', 'sender', 'appIcon', 'contentImage', 'open', 'execute']
params = ['reply', 'json']

def Notify(message, **kwargs):
	items = kwargs.items()

	for i in items:
		if not i[0] in arguments:
			print(str(i) + ' is not a valid argument. Removed from args list.')
			items.remove(i)

			if i in params:
				if not type(items[i]) == bool:
					items.remove(i)

	message = message.encode('utf-8')

	args = ['-message', message]
	args += [a for b in [("-%s" % arg, "'"+str(key)+"'") for arg, key in kwargs.items()] for a in b]

	os.system('terminal-notifier ' + ' '.join(args))

def RemoveByID(id):
	# Use ID 'ALL' to remove all messages.
	os.system('terminal-notifier -remove ' + str(id))

def ListByID(id):
	# use ID 'ALL' to list details about all messages.
	os.system('terminal-notifier -list ' + str(id))