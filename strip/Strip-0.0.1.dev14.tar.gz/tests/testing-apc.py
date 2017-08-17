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

    logger.info("Connecting to APC")
    a = Apc.Apc(user="apc",
                password="apc",
                host="")

    logger.info("Current state of 18 : {}".format(a.state("18")))
    logger.info("Turning off 18")
    a.off("18")
    logger.info("Current state of 18 : {}".format(a.state("18")))
    logger.info("Turning on 18")
    a.on("18")
    logger.info("Current state of 18 : {}".format(a.state("18")))
# usage is broken with apc
#    a.usage()


if __name__ == '__main__':
    sys.exit(main())
