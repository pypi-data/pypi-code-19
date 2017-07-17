###################################################################################
#
#
###################################################################################

##################################### IMPORTS #####################################

import datetime
import os, sys
import ConfigParser

config = ConfigParser.ConfigParser()
from subprocess import check_output

config.read(check_output("echo $ATS", shell=True).replace("\n", "") + "/framework_scripts/script_run_config.cnf")


############################### SET TIME FORMAT ####################################

def formatTime(time):
    timeFormat = "%Y-%m-%d_%H:%M:%S.%f"
    return time.strftime(timeFormat)


import F_remoteDriverHandler


############################ DEFINE THE TEST MODULE ###################################

def performActions(testData):
    logger = testData['logger']
    try:
        driver = testData['driver']
        logger.info("Current URL: %s" % driver.current_url)
    except:
        driver = False  # may be calling this function from a script not using webdriver
    resultsPath = testData['RESULTS_PATH']
    takeScreenshots = config.get("actionsOnFail", "takeScreenshots")
    if takeScreenshots == "yes" and driver != False:
        if not os.path.exists(resultsPath + "Screenshots/"):
            os.makedirs(resultsPath + "Screenshots/")
        currentTime = formatTime(datetime.datetime.today())
        screenshotFileName = resultsPath + "Screenshots/" + currentTime + ".png"
        retries = 0
        while True:
            try:
                driver.get_screenshot_as_file(screenshotFileName)
                logger.info("Screenshot saved as '%s'" % screenshotFileName)
                break
            except:
                retries += 1
                if retries >= 10:
                    logger.error("Could not save a screenshot")
                    break
    else:
        logger.info("Screenshot on fail disabled")


def exitTestScriptGracefully(testData):
    try:
        logger = testData['logger']
        performActions(testData)
        F_remoteDriverHandler.quitRemoteDriver(testData)
        logger.result("The result of the test was [FAILED]")
        sys.exit(0)
    except:
        logger = testData['logger']
        logger.result("The result of the test was [FAILED]")
        sys.exit(0)
