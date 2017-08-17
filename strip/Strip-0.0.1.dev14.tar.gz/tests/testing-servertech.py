import sys
import pprint
import time
import logging
import inspect
import os
sys.path.append('./strip/')
sys.path.append('../strip/')
import Apc
import ServerTech
import PowerManagement
import Outlets

def main() :
    logger = logging.getLogger('Strip')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info("PowerStrip Work")

    logger.info("Connecting to ServerTech")
    s = ServerTech.ServerTech(user="admn",
                          password="admn",
                          host="")

    logger.info("Current state of BC7 : {}".format(s.state(".BC7")))
    logger.info("Turning off BC7")
    s.off(".BC7")
    logger.info("Current state of BC7 : {}".format(s.state(".BC7")))
    logger.info("Turning on BC7")
    s.on(".BC7")
    logger.info("Current state of BC7 : {}".format(s.state(".BC7")))
    s.usage()

if __name__ == '__main__':
    sys.exit(main())
