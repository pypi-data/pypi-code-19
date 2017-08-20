#!/bin/python
import logging;
import sys;

project_name = "roomai";

logger = logging.getLogger(project_name);
handler = logging.StreamHandler(sys.stderr);
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s");

logger.setLevel(logging.INFO);
handler.setLevel(logging.INFO);
handler.setFormatter(formatter);
logger.addHandler(handler);


def set_level(level):
    """

    Args:
        level:
    """
    logger.setLevel(level)
    handler.setLevel(level)

def get_logger():
    """

    Returns:

    """
    return logger


def init_logger(opts):
    """

    Args:
        opts:
    """
    global logger;
    global handler;
    global project_name;

    print opts;
    if "project_name" in opts:
        project_name = opts["project_name"];
        print "in Logger", project_name;

    logger.removeHandler(handler);
    logger = logging.getLogger(project_name);

    #set longer
    if "logfile" in opts:
        handler = logging.FileHandler(opts["logfile"]);
    else:
        handler = logging.StreamHandler(sys.stderr);
    
    #set formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s");
    handler.setFormatter(formatter);

    ##set level
    logger.setLevel(logging.INFO);
    if "level" in opts:
        if "notset" == opts["level"].lowcase():
            logger.setLevel(logging.NOTSET)
        elif "debug" == opts["level"].lowcase():
            logger.setLevel(logging.DEBUG)
        elif "info"  == opts["level"].lowcase():
            logger.setLevel(logging.INFO)
        elif "warning" == opts["level"].lowcase():
            logger.setLevel(logging.WARNING)
        elif "error" == opts["level"].lowcase():
            logger.setLevel(logging.ERROR)
        elif "critical" == opts["level"].lowcase():
            logger.setLevel(logging.critical)

    logger.addHandler(handler);
   
