
"""The generate command."""


from json import dumps
from .base import Base
import sys
import os
import glob
import pathlib
from pbxproj import XcodeProject

from .messages import headerString
from .messages import pathError
from .messages import vcConfirmation
from .messages import exitMessage


class Generate(Base):
    """Generate a Swift/iOS components"""

    def run(self):
        # Print the header
        print(headerString)

        # Generate a ViewController
        if self.options["<blueprint>"] == "viewController" or self.options["<blueprint>"] == "vc":

            # Check if we are at the right path
            self.check_path()

            # Confirm the creation of the ViewController
            name = self.options["<name>"]
            response = input(vcConfirmation.replace('{}',name))
            self.check_response(response)


            print("done!")


    def check_path(self):
        """Check if the commandline is in the appropriate project path"""
        if glob.glob('*.xcodeproj'):
            print(" ✅  Xcode project found: {} \n".format(glob.glob('*.xcodeproj')[0]))
        else:
            print(pathError)
            sys.exit()


    def check_response(self, response):
        """Check if the answer is yes or no"""
        if response == "Y" or response == "y" or response == "YES" or response == "yes" or response == "Yes":
            pass
        else:
            print(exitMessage)
            sys.exit()
