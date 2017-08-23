#
# Module containing an extension of the setuptools build_ext class.
# Part of the esig Python package.
# 
# Author: David Maxwell <maxwelld90@gmail.com>
# Date: 2017-07-07
#

__author__ = 'David Maxwell <dmaxwell@turing.ac.uk>'
__date__ = '2017-07-07'

from setuptools.command.build_ext import build_ext

class NumpyExtensionCommand(build_ext):
    """
    Extends the build_ext class.
    Overrides the run() method.
    """
    def run(self):
        """
        Attempts to import numpy and append the result of numpy.get_include() to the self.include_dirs list.
        Why is this required?
        
        Args:
            self (NumpyExtensionCommand): Instance of self.
        
        Returns:
            None
        """
        import numpy
        self.include_dirs.append(numpy.get_include())
        build_ext.run(self)