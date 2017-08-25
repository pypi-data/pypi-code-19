# -*- coding: utf-8 -*-

# Copyright © 2017, François Laurent

# This file is part of the Escale software available at
# "https://github.com/francoislaurent/escale" and is distributed under
# the terms of the CeCILL-C license as circulated at the following URL
# "http://www.cecill.info/licenses.en.html".

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL-C license and that you accept its terms.


from .access import AccessController




class SplitCombine(AccessController):

	def __init__(self, cache_dir, name='parts', mode=None, min_split_size=None, logger=None, ui_controller=None, **kwargs):
		AccessController.__init__(self, name, path=cache_dir, mode=mode, persistent=None, logger=logger, ui_controller=ui_controller)
		self.min_split_size = kwargs.pop('minsplitsize', min_split_size)

	@property
	def cache_dir(self):
		return self.path

	def listFiles(self):
		return AccessController.listFiles(self)

	def confirmPull(self, filename):
		return PullCombine(self)

	def confirmPush(self, filename):
		return Push(self)

