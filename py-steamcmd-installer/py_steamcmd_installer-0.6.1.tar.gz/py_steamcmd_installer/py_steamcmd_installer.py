"""Simple tool that handels the steamcmd to install apps and get the full output
works under Windows an Linux """
__author__ = "Tobias Liese"
__license__ = "MIT"
__version__ = 0.6
__maintainer__ = "Tobias Liese"
__email__ = "tobiasliese@outlook.com"
__status__ = "Beta"


import os
import logging
import platform
import logging

from sys import argv

def setup_logger():
    debug_level = logging.INFO


    logger = logging.getLogger(__name__)
    logger.setLevel(debug_level)

    # create a file handler
    if not os.path.isdir("log"):
        os.makedirs("log")
    handler = logging.FileHandler('log/installer.log')
    handler.setLevel(debug_level)

    # create a logging format
    formatter = logging.Formatter('[ %(levelname)s ] %(asctime)s  %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the self.logger
    logger.addHandler(handler)

    return logger

class Steamcmd(object):
    __platform = platform.system()

    def __init__(self, path, logger=setup_logger()):
        self.logger = logger
        self.STEAMCMD_PATH = path

    # This method should be overriten when using this libary
    def handleOutput(self, output):
        self.logger.debug(output)

    def _installServer(self, app_id, path):
        self.logger.info(
          "Initiating server installation for steam app: " + str(app_id)
        )

        # Making sure the path to install the app to is absoulut
        if not os.path.isabs(path):
            path = os.path.abspath(path)

        # Starting the installer function for the current running OS
        if self.__platform == "Windows":
            return self.__installSteamAppWindows(app_id, path)
        elif self.__platform == "Linux":
            return self.__installSteamAppLinux(app_id, path)
        else:
            """
            maybe add an option to install unsave this would just use the
            Windows app install procedere
            """
            raise NotImplementedError("OS not implemented")

    def __installSteamAppWindows(self, appID, path):
        """
        Under Windows we can simply PIPE the output from the started steamcmd
        subprocess to get the full output
        """
        from subprocess import Popen, PIPE
        self.logger.info("Starting server installation")
        return Popen(
                     [
                       self.STEAMCMD_PATH,
                       "+login", "anonymous",
                       "+force_install_dir", path,
                       "+app_update", str(appID),
                       "+quit"
                      ],
                      stdout=PIPE
                     )

    def __installSteamAppLinux(self, appID, path):
        """
        Because under Linux steamcmd doesn't output the download process
        in our PIPE we need to emulate a terminal that gives us the output
        therefore pty is requiered under Linux
        """
        import pty

        # Creating a reader for our pty
        def ptyReader(fd):
            data = os.read(fd, 1024)
            self.handleOutput(data.decode())
            return data

        self.logger.info("Starting server installation")
        # spawn the pty
        pty.spawn(
                  [
                    self.STEAMCMD_PATH,
                    "+login", "anonymous",
                    "+force_install_dir", path,
                    "+app_update", str(appID),
                    "+quit"
                  ],
                  ptyReader)
        # pty stopped here nothing more to do
        exit()

    def installServer(self, app_id, path):
        process = self._installServer(app_id, path)

        # Keeping process alive while subprocess in running
        while process.poll() == None:

            # getting theping process alive while subprocesses process output current line migth be empty
            line = process.stdout.readline().decode()

            # Process all lines that aren't empty
            if len(line) >= 1:
                output_parser(line)

        self.logger.info("Finished installing")


if __name__ == "Main":
    print("This File is a little libary and therefore not meant to be executed\
    directly")
