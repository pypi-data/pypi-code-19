# -*- coding: utf-8 -*-

import otree_save_the_change

from setuptools import setup, find_packages


tests_require = []
for line in open('test_requirements.txt', 'rU').readlines():
	if line and line not in '\n' and not line.startswith(('#', '-')):
		tests_require.append(line.replace('\n', ''))

setup(
	name="otree-save-the-change",
	version=otree_save_the_change.__version__,
	description="Automatically save only changed model data.",
	long_description="\n\n".join([open('README.rst', 'rU').read(), open('HISTORY.rst', 'rU').read()]),
	author=otree_save_the_change.__author__,
	author_email=otree_save_the_change.__contact__,
	url=otree_save_the_change.__homepage__,
	license=open('LICENSE', 'rU').read(),
	packages=['otree_save_the_change'],
	tests_require=tests_require,
	zip_safe=False,
	test_suite='tests.test.run_tests',
)
