###################################################################################
#
#	SELENIUM WEBDRIVER COMMAND WRAPPERS FOR USE IN THE ATF TEST SCRIPTS
#
###################################################################################

##################################### IMPORTS #####################################

import sys,time, re
import ConfigParser
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from subprocess import check_output

################################# GET CONFIG ######################################

config = ConfigParser.ConfigParser()
ATS = check_output( "echo $ATS" , shell=True ).replace( "\n", "" ) + "/"
config.read( ATS + "framework_scripts/script_run_config.cnf" )
waitForTime = int(config.get("selenium-config", "waitForElementsAndValuesTime"))

########################## ADD MODULE IMPORT PATHS ################################

sys.path.insert( 0 , '$ATF/framework/atflib' )
import modulePathManager
modulePathManager.addModulePaths()

############################# TEST MODULE IMPORT ##################################

import actionsOnFail

############################## GENERAL FUNCTIONS ###################################

## switch frame
def selectFrame( testData , frame ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.switch_to_frame( frame )
		return "PASSED"
	except Exception as e:
		logger.error( str(e) )
		logger.error("Error selecting iframe '%s'" % frame )
		actionsOnFail.exitTestScriptGracefully( testData )

def switchBackToDefault( testData ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.switch_to_default_content()
		return "PASSED"
	except Exception as e:
		logger.error( str(e) )
		logger.error("Error selecting the default content")
		actionsOnFail.exitTestScriptGracefully( testData )

## switch window
def selectWindowByName( testData , windowName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		for handle in driver.window_handles:
			driver.switch_to_window( handle )
			title = driver.title
			if title == windowName :
				logger.info("Window found")
				return "PASSED"
		logger.failed("Couldn't find window '%s'" % windowName )
		actionsOnFail.exitTestScriptGracefully( testData )
#		driver.switch_to_window( windowName )
	except Exception as e:
		logger.failed( str(e) )
		logger.failed("Error selecting window '%s'" % windowName )
		actionsOnFail.exitTestScriptGracefully( testData )

## got to url
def goto(testData,URL, direct=False, timeout=False): # to be used for normal testing
	driver = testData['driver']
	logger = testData['logger']
	if timeout != False : driver.set_page_load_timeout( int(timeout) ) 
	if direct == False : setURL = testData['driver_url']+URL
	else : setURL = URL
	logger.info(str(setURL))
	try:
		driver.get(setURL)
		currentURL = driver.current_url
		logger.info("Current URL is %s"%currentURL)
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		logger.error("Error opening url = %s"%setURL)
		actionsOnFail.exitTestScriptGracefully(testData)

## send keys
def sendKeysByTinyMCE( testData , text ):
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.execute_script( "tinyMCE.activeEditor.selection.setContent('"+text+"')" )
		logger.passed( "Sent '%s' to the TinyMCE widget" )
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"

def sendKeysByID( testData , elementID , text ):
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_id( elementID )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try :
		driver.find_element_by_id(elementID).clear()
	except :
		logger.info("Element id '%s' was not cleared, this could be because it is not a standard text field" % elementID)
	try:
		driver.find_element_by_id( elementID ).send_keys( text )
		logger.passed("Text '%s' was entered into element '%s'"%( text , elementID ))
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"

def sendKeysByName( testData , name , text ):
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_name( name )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try :
		driver.find_element_by_name( name ).clear()
	except :
		logger.info("Element name '%s' was not cleared, this could be because it is not a standard text field" % name )
	try:
		driver.find_element_by_name( name ).send_keys( text )
		logger.passed("Text '%s' was entered into element '%s'"%( text , name ))
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def sendKeysByXPath( testData , xpath , text ):
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_xpath( xpath )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try :
		driver.find_element_by_xpath( xpath ).clear()
	except :
		logger.info("Element xpath '%s' was not cleared, this could be because it is not a standard text field" % xpath )
	try:
		driver.find_element_by_xpath( xpath ).send_keys(text)
		logger.passed("Text '%s' was entered into xpath '%s'"%( text , xpath ))
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def sendKeysByCSS( testData , css_selector , text ):
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_css_selector( css_selector )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try :
		driver.find_element_by_css_selector( css_selector ).clear()
	except :
		logger.info("Element css_selector '%s' was not cleared, this could be because it is not a standard text field" % css_selector )
	try:
		driver.find_element_by_css_selector( css_selector ).send_keys( text )
		logger.passed("Text '%s' was entered into css_selector '%s'"%( text , css_selector ))
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"

## clear field
def clearByID( testData , elementID ):
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_id( elementID )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try:
		driver.find_element_by_id( elementID ).clear()
		logger.passed("id '%s' field cleared" % elementID )
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def clearByXPath( testData , xpath ):
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_xpath( xpath )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try:
		driver.find_element_by_xpath( xpath ).clear()
		logger.passed("xpath '%s' field cleared" % xpath )
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def clearByName( testData , name ):
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_name( name )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try:
		driver.find_element_by_name( name ).clear()
		logger.passed("name '%s' field cleared" % name )
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def clearByCSS( testData , css_selector ):
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_css_selector( css_selector )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try:
		driver.find_element_by_css_selector( css_selector ).clear()
		logger.passed("css_selector '%s' field cleared" % css_selector )
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

## click 
def clickByID(testData,elementID):
	driver = testData['driver']
	logger = testData['logger']
	try:
		driver.find_element_by_id(elementID).click()
		logger.passed("Clicked element '%s'"%(elementID))
		return "PASSED"
	except Exception as e:
		logger.failed( "Could not click on id: %s" % elementID )
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def clickByText( testData, text , tagType="*" ):
	driver = testData['driver']
	logger = testData['logger']
	if str(text) == "" :
		logger.error( "Cannot use a blank value '' to search for text" )
		actionsOnFail.performActions(testData)
		return "ERROR"
	xpath = '//'+str(tagType)+'[contains(text(),"' + str(text) + '")]'
	try:
		driver.find_element_by_xpath( xpath ).click()
		logger.passed("Clicked text '%s'" % ( text ) )
		return "PASSED"
	except Exception as e:
		logger.failed( "Could not click on text: %s (xpath: %s)" % ( text , xpath ) )
		logger.failed( str(e) )
		actionsOnFail.performActions( testData )
		return "FAILED"

def clickByXPath(testData,xpath):
	driver = testData['driver']
	logger = testData['logger']
	try:
		driver.find_element_by_xpath(xpath).click()
		logger.passed("Clicked element at xpath '%s'"%(xpath))
		return "PASSED"
	except Exception as e:
		logger.failed( "Could not click on xpath: %s" % xpath )
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def clickByCSS(testData,css_selector):
	driver = testData['driver']
	logger = testData['logger']
	try:
		driver.find_element_by_css_selector(css_selector).click()
		logger.passed("Clicked element at css_selector '%s'"%(css_selector))
		return "PASSED"
	except Exception as e:
		logger.failed( "Could not click on css: %s" % css_selector )
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def clickByName( testData , name ):
	driver = testData['driver']
	logger = testData['logger']
	try:
		driver.find_element_by_name( name ).click()
		logger.passed("Clicked element at name '%s'"%( name ))
		return "PASSED"
	except Exception as e:
		logger.failed( "Could not click on name: %s" % name )
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def clickByLink( testData , link ):
	driver = testData['driver']
	logger = testData['logger']
	try:
		driver.find_element_by_link_text( link ).click()
		logger.passed("Clicked element at link '%s'"%( link ))
		return "PASSED"
	except Exception as e:
		logger.failed( "Could not click on link: %s" % link )
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"
	
## cannot click/select

def verifyNotClickableByXPath(testData,xpath):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if not driver.find_element_by_xpath(xpath).click():
			logger.passed( "Could not click on xpath: %s" % xpath )
			return "PASSED"
		else:
			logger.failed("Clicked element at xpath '%s' - element should not be available"%(xpath))
			return "FAILED"
	except Exception as e:
		logger.failed("Element at xpath: %s cannot be found" % xpath)
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"	
	
## check (check box)
def checkByID( testData , elementID ):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if not driver.find_element_by_id( elementID ).is_selected() :
			driver.find_element_by_id( elementID ).click()
		logger.passed("Checked element with id: '%s'"%( elementID ))
		return "PASSED"
	except Exception as e:
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def checkByXPath(testData,xpath):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if not driver.find_element_by_xpath( xpath ).is_selected() :
			driver.find_element_by_xpath( xpath ).click()
		logger.passed("Checked element at xpath '%s'"%(xpath))
		return "PASSED"
	except Exception as e:
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def checkByCSS(testData,css_selector):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if not driver.find_element_by_css_selector( css_selector ).is_selected() :
			driver.find_element_by_css_selector( css_selector ).click()
		logger.passed("Checked element at css_selector '%s'"%(css_selector))
		return "PASSED"
	except Exception as e:
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def checkByName( testData , name ):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if not driver.find_element_by_name( name ).is_selected() :
			driver.find_element_by_name( name ).click()
		logger.passed("Checked element at name '%s'"%( name ))
		return "PASSED"
	except Exception as e:
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

## uncheck (check box)
def uncheckByID( testData , elementID ):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_id( elementID ).is_selected() :
			driver.find_element_by_id( elementID ).click()
		logger.passed("Unchecked element with id: '%s'"%( elementID ))
		return "PASSED"
	except Exception as e:
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def uncheckByXPath(testData,xpath):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_xpath( xpath ).is_selected() :
			driver.find_element_by_xpath( xpath ).click()
		logger.passed("Unchecked element at xpath '%s'"%(xpath))
		return "PASSED"
	except Exception as e:
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def uncheckByCSS(testData,css_selector):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_css_selector( css_selector ).is_selected() :
			driver.find_element_by_css_selector( css_selector ).click()
		logger.passed("Unchecked element at css_selector '%s'"%(css_selector))
		return "PASSED"
	except Exception as e:
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def uncheckByName( testData , name ):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_name( name ).is_selected() :
			driver.find_element_by_name( name ).click()
		logger.passed("Unchecked element at name '%s'"%( name ))
		return "PASSED"
	except Exception as e:
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

## mouse over
def mouseOverByID( testData , elementID ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		element = driver.find_element_by_id( elementID )
		action = ActionChains( driver ).move_to_element( element )
		action.perform()
		logger.passed("mouseOver '%s'" % ( elementID ))
		return "PASSED"
	except Exception as e:
		logger.failed(str(e))
		actionsOnFail.performActions(testData)
		return "FAILED"

def mouseOverByXPath( testData , xpath ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		element = driver.find_element_by_xpath( xpath )
		action = ActionChains( driver ).move_to_element( element )
		action.perform()
		logger.passed("mouseOver '%s'" % ( xpath ))
		return "PASSED"
	except Exception as e:
		logger.failed(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"

def mouseOverByName( testData , name ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		element = driver.find_element_by_name( name )
		action = ActionChains( driver ).move_to_element( element )
		action.perform()
		logger.passed("mouseOver '%s'" % ( name ))
		return "PASSED"
	except Exception as e:
		logger.failed(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"

def mouseOverByCSS( testData , css_selector ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		element = driver.find_element_by_css_selector( css_selector )
		action = ActionChains( driver ).move_to_element( element )
		action.perform()
		logger.passed("mouseOver '%s'" % ( css_selector ))
		return "PASSED"
	except Exception as e:
		logger.failed(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"

## pause
def pause( testData , seconds ):
	logger = testData['logger']
	time.sleep( float(seconds) )
	logger.info("Paused for '%s' seconds" % seconds )
	return "PASSED"

## wait for attribute
def waitForAttributeByXPath( testData , xpath , attribute , value , timeToWait=waitForTime ) :
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			if value in driver.find_element_by_xpath(xpath).get_attribute(attribute): 
				logger.passed("Value '%s' was found in xpath '%s', attribute '%s'"%( value , xpath , attribute ))
				return "PASSED"
		except: pass
		time.sleep(1)
	logger.failed("Value '%s' was not found in xpath '%s', attribute '%s' after '%s' seconds"%( value , xpath , attribute, str(timeToWait) ))
	actionsOnFail.performActions( testData )
	return "FAILED"

def waitForAttributeByID( testData , elementID , attribute , value , timeToWait=waitForTime ) :
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			if value in driver.find_element_by_id(elementID).get_attribute(attribute): 
				logger.passed("Value '%s' was found in element '%s', attribute '%s'"%( value , elementID , attribute ))
				return "PASSED"
		except: pass
		time.sleep(1)
	logger.failed("Value '%s' was not found in elementID '%s', attribute '%s' after '%s' seconds"%( value , elementID , attribute, str(timeToWait) ))
	actionsOnFail.performActions( testData )
	return "FAILED"

def waitForAttributeByCSS( testData , css_selector , attribute , value , timeToWait=waitForTime ) :
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			if value in driver.find_element_by_css_selector(css_selector).get_attribute(attribute): 
				logger.passed("Value '%s' was found in css_selector '%s', attribute '%s'"%( value , css_selector, attribute ))
				return "PASSED"
		except: pass
		time.sleep(1)
	logger.failed("Value '%s' was not found in css_selector '%s', attribute '%s' after '%s' seconds"%( value , css_selector, attribute, str(timeToWait) ))
	actionsOnFail.performActions( testData )
	return "FAILED"

def waitForAttributeByName( testData , name , attribute , value , timeToWait=waitForTime ) :
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			if value in driver.find_element_by_name(name).get_attribute(attribute): 
				logger.passed("Value '%s' was found in name '%s', attribute '%s'"%( value , name , attribute ))
				return "PASSED"
		except: pass
		time.sleep(1)
	logger.failed("Value '%s' was not found in name '%s', attribute '%s' after '%s' seconds"%( value , name , attribute, str(timeToWait) ))
	actionsOnFail.performActions( testData )
	return "FAILED"

## wait for value

def waitForValueByXPath(testData, xpath, value , timeToWait=waitForTime ):
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			if value == driver.find_element_by_xpath(xpath).get_attribute("value"): 
				logger.passed("Value '%s' found by xpath '%s'"%(value,xpath))
				return "PASSED"
		except: pass
		time.sleep(1)
	logger.failed("Value '%s' was not found in element '%s' after '%s' seconds" % ( value , xpath , str(timeToWait)) )
	actionsOnFail.performActions(testData)
	return "FAILED"

def waitForValueByID(testData, elementID, value , timeToWait=waitForTime ):
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			if value == driver.find_element_by_id(elementID).get_attribute("value"): 
				logger.passed("Value '%s' found by id '%s'"%(value,elementID))
				return "PASSED"
		except: pass
		time.sleep(1)
	logger.failed("Value '%s' was not found in element '%s' after '%s' seconds" % ( value , elementID , str(timeToWait)) )
	actionsOnFail.performActions(testData)
	return "FAILED"

def waitForValueByCSS(testData, css_selector, value , timeToWait=waitForTime ):
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			if value == driver.find_element_by_css_selector(css_selector).get_attribute("value"): 
				logger.passed("Value '%s' found by css '%s'"%(value,css_selector))
				return "PASSED"
		except: pass
		time.sleep(1)
	logger.failed("Value '%s' was not found in element '%s' after '%s' seconds" % ( value , css_selector , str(timeToWait)) )
	actionsOnFail.performActions(testData)
	return "FAILED"

def waitForValueByName(testData, name, value , timeToWait=waitForTime ):
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			if value == driver.find_element_by_name(name).get_attribute("value"): 
				logger.passed("Value '%s' found by name '%s'"%(value,name))
				return "PASSED"
		except: pass
		time.sleep(1)
	logger.failed("Value '%s' was not found in element '%s' after '%s' seconds" % ( value , value , str(timeToWait)) )
	actionsOnFail.performActions(testData)
	return "FAILED"
	
## wait for element present

def waitForElementPresentByXPath(testData, xpath , timeToWait=waitForTime ):
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			driver.find_element_by_xpath( xpath )
			logger.passed("Element '%s' found" % xpath )
			return "PASSED"
		except: pass
		time.sleep(1)
	logger.failed("Xpath '%s' was not found on the page after '%d' seconds" %( xpath,timeToWait) )
	actionsOnFail.performActions(testData)
	return "FAILED"

def waitForElementNotPresentByXPath(testData, xpath , timeToWait=waitForTime ):
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			driver.find_element_by_xpath( xpath )
			pass
		except: 
			logger.passed("Element '%s' no longer present" % xpath )
			return "PASSED"
		time.sleep(1)
	logger.failed("Element '%s' was still found on the page after '%d' seconds" %( xpath,timeToWait) )
	actionsOnFail.performActions(testData)
	return "FAILED"

def waitForElementPresentByID(testData, elementID , timeToWait=waitForTime ):
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			driver.find_element_by_id( elementID )
			logger.passed("Element '%s' found" % elementID)
			return "PASSED"
		except: pass
		time.sleep(1)
	logger.failed("Element '%s' was not found on the page after '%d' seconds" %(elementID,timeToWait) )
	actionsOnFail.performActions(testData)
	return "FAILED"

def waitForElementNotPresentByID(testData, elementID , timeToWait=waitForTime ):
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			driver.find_element_by_id( elementID )
			pass
		except: 
			logger.passed("Element '%s' no longer present" % elementID )
			return "PASSED"
		time.sleep(1)
	logger.failed("Element '%s' was still found on the page after '%d' seconds" %(elementID,timeToWait) )
	actionsOnFail.performActions(testData)
	return "FAILED"

def waitForElementPresentByCSS(testData, css_selector , timeToWait=waitForTime ):
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			driver.find_element_by_css_selector( css_selector )
			logger.passed("Element '%s' found" % css_selector)
			return "PASSED"
		except: pass
		time.sleep(1)
	logger.failed("Element '%s' was not found on the page after '%d' seconds" %(css_selector,timeToWait) )
	actionsOnFail.performActions(testData)
	return "FAILED"

def waitForElementNotPresentByCSS(testData, css_selector , timeToWait=waitForTime ):
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			driver.find_element_by_css_selector( css_selector )
			pass
		except: 
			logger.passed("Element '%s' no longer present" % css_selector )
			return "PASSED"
		time.sleep(1)
	logger.failed("Element '%s' was still found on the page after '%d' seconds" %(css_selector,timeToWait) )
	actionsOnFail.performActions(testData)
	return "FAILED"

def waitForElementPresentByName(testData, name , timeToWait=waitForTime ):
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			driver.find_element_by_name( name )
			logger.passed("Element '%s' found" % name)
			return "PASSED"
		except: pass
		time.sleep(1)
	logger.failed("Element '%s' was not found on the page after '%d' seconds" %(name,timeToWait) )
	actionsOnFail.performActions(testData)
	return "FAILED"

def waitForElementNotPresentByName(testData, name , timeToWait=waitForTime ):
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			driver.find_element_by_name( name )
			pass
		except: 
			logger.passed("Element '%s' no longer present" % name )
			return "PASSED"
		time.sleep(1)
	logger.failed("Element '%s' was still found on the page after '%d' seconds" %(name,timeToWait) )
	actionsOnFail.performActions(testData)
	return "FAILED"

def waitForElementPresentByLink( testData , link , timeToWait=waitForTime ):
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			driver.find_element_by_link_text( link )
			logger.passed("Element '%s' found" % link )
			return "PASSED"
		except: pass
		time.sleep(1)
	logger.failed("Element '%s' was not found on the page after '%d' seconds" %( link , timeToWait ) )
	actionsOnFail.performActions(testData)
	return "FAILED"

def waitForElementNotPresentByLink( testData , link , timeToWait=waitForTime ):
	driver = testData['driver']
	logger = testData['logger']
	for i in range( int(timeToWait) ):
		try:
			driver.find_element_by_link_text( link )
			pass
		except: 
			logger.passed("Element '%s' no longer present" % link )
			return "PASSED"
		time.sleep(1)
	logger.failed("Element '%s' was still found on the page after '%d' seconds" %( link , timeToWait ) )
	actionsOnFail.performActions( testData )
	return "FAILED"

############################## SCROLL TO ELEMENT ##################################

def scrollToElementByID( testData , elementID ) :
	driver = testData['driver']
	logger = testData['logger']
	retry = 100
	logger.info( "Attempting to scroll to element" )
	try :
		driver.find_element_by_id( elementID ).is_displayed()
		logger.passed( "Element elementID '%s' already visible" % elementID )
		return "PASSED"
	except :
		attempt = 1
		pixelsToScroll = 100
		while attempt <= retry :
			driver.execute_script( "window.scrollTo(0, " + str( pixelsToScroll ) + ");" )
			totalScroll = attempt * pixelsToScroll
			try :
				driver.find_element_by_id( elementID ).is_displayed()
				logger.passed( "elementID '%s' is now visible after scrolling a total of '%s' pixels" % ( elementID , totalScroll ) )
				return "PASSED"
			except :
				pass
			attempt += 1
	logger.failed( "After scrolling down '%s' pixels, the elementID '%s' was still not visible" % ( totalScroll , elementID ) )
				

def scrollToElementByName( testData , name ) :
	driver = testData['driver']
	logger = testData['logger']
	retry = 100
	try :
		driver.find_element_by_xpath( name ).is_displayed()
		logger.passed( "Element xpath '%s' already visible" % name )
		return "PASSED"
	except :
		attempt = 1
		pixelsToScroll = 100
		while attempt <= retry :
			driver.execute_script( "window.scrollTo(0, " + str( pixelsToScroll ) + ");" )
			totalScroll = attempt * pixelsToScroll
			try :
				driver.find_element_by_xpath( name ).is_displayed()
				logger.passed( "Element xpath '%s' is now visible after scrolling a total of '%s' pixels" % ( name , totalScroll ) )
				return "PASSED"
			except :
				pass
			attempt += 1
	logger.failed( "After scrolling down '%s' pixels, the element xpath '%s' was still not visible" % ( totalScroll , name ) )

def scrollToElementByXPath( testData , xpath ) :
	driver = testData['driver']
	logger = testData['logger']
	retry = 100
	try :
		driver.find_element_by_xpath( xpath ).is_displayed()
		logger.passed( "Element xpath '%s' already visible" % xpath )
		return "PASSED"
	except :
		attempt = 1
		pixelsToScroll = 100
		while attempt <= retry :
			driver.execute_script( "window.scrollTo(0, " + str( pixelsToScroll ) + ");" )
			totalScroll = attempt * pixelsToScroll
			try :
				driver.find_element_by_xpath( xpath ).is_displayed()
				logger.passed( "Element xpath '%s' is now visible after scrolling a total of '%s' pixels" % ( xpath , totalScroll ) )
				return "PASSED"
			except :
				pass
			attempt += 1
	logger.failed( "After scrolling down '%s' pixels, the element xpath '%s' was still not visible" % ( totalScroll , xpath ) )

def scrollToElementByCSS( testData , css_selector ) :
	driver = testData['driver']
	logger = testData['logger']
	retry = 100
	try :
		driver.find_element_by_xpath( css_selector ).is_displayed()
		logger.passed( "Element xpath '%s' already visible" % css_selector )
		return "PASSED"
	except :
		attempt = 1
		pixelsToScroll = 100
		while attempt <= retry :
			driver.execute_script( "window.scrollTo(0, " + str( pixelsToScroll ) + ");" )
			totalScroll = attempt * pixelsToScroll
			try :
				driver.find_element_by_xpath( css_selector ).is_displayed()
				logger.passed( "Element xpath '%s' is now visible after scrolling a total of '%s' pixels" % ( css_selector , totalScroll ) )
				return "PASSED"
			except :
				pass
			attempt += 1
	logger.failed( "After scrolling down '%s' pixels, the element xpath '%s' was still not visible" % ( totalScroll , css_selector ) )


######################## AUTO-COMPLETE FIELD FUNCTIONS ############################

def autocompleteByXPath( testData , xpath , entry ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_xpath( xpath )
	except Exception as e :
		logger.error(str(e))
		logger.error("There was an ERROR locating the autocomplete box xpath '%s'" % xpath )
		actionsOnFail.exitTestScriptGracefully( testData )
	try :
		driver.find_element_by_xpath( xpath ).clear()
		driver.find_element_by_xpath( xpath ).send_keys( entry )
		logger.info("'%s' has been typed into the autocomplete box '%s'" % ( entry , xpath ))
	except Exception as e :
		logger.error(str(e))
		logger.error("There was an ERROR typing '%s' into autocomplete box xpath '%s'" % ( entry , xpath ))
		actionsOnFail.exitTestScriptGracefully( testData )
	selection = xpath.replace( "input" , "a/span" )
	try :
		driver.find_element_by_xpath( selection ).click()
		logger.info("xpath '%s' was clicked from the autocomplete options list" % selection)
	except Exception as e :
		logger.error(str(e))
		logger.error("There was an ERROR clicking the selection '%s' using xpath option '%s'" % ( entry , selection ))
		actionsOnFail.exitTestScriptGracefully( testData )
	try :
		actualSelection = driver.find_element_by_xpath( xpath ).get_attribute( "value" )
		if entry == actualSelection :
			logger.passed("Selection has been retained in the autocomplete field")
			return "PASSED"
		else :
			logger.failed("'%s' did not match our selection '%s'" % ( actualSelection , entry ))
			actionsOnFail.exitTestScriptGracefully( testData )
	except Exception as e :
		logger.error(str(e))
		logger.error("Unable to assert that selection was retained")
		actionsOnFail.exitTestScriptGracefully( testData )


########################## DROP DOWN FIELD FUNCTIONS ##############################

#new drop down selector
def selectDropDownItemByID( testData , dropDownID , itemText ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		select = Select(driver.find_element_by_id( dropDownID ))
		logger.info( "Dropdown with id '%s' found" % dropDownID )		
	except Exception as e :
		logger.error( str( e ) )
		logger.error( "Could not find the dropdown menu at id '%s'" % dropDownID )
		actionsOnFail.exitTestScriptGracefully( testData )
	try :
		select.select_by_visible_text( itemText )
		logger.passed( "'%s' selected from drop down '%s'" % ( itemText , dropDownID ) )
		return "PASSED"
	except Exception as e :
		logger.error( str( e ) )
		logger.error( "Error selecting the correct option '%s' from drop down '%s'" % ( itemText , dropDownID ) )
		logger.info( "The dropdown contents were: " + [str(o.text) for o in select.options] ) ## this can potentially take a long time to execute
		actionsOnFail.exitTestScriptGracefully( testData )
		
#Select drop down item by value attribute		
def selectDropDownItemByID_Attribute( testData , dropDownID , itemValue ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		Select(driver.find_element_by_id( dropDownID ))
		#logger.info( [str(o.value) for o in select.options] )
	except Exception as e :
		logger.error( str( e ) )
		logger.error( "Could not find the dropdown menu at id '%s'" % dropDownID )
		actionsOnFail.exitTestScriptGracefully( testData )
	try :
		Select(driver.find_element_by_value( itemValue ))
		logger.passed( "'%s' selected from drop down '%s'" % ( itemValue , dropDownID ) )
		return "PASSED"
	except Exception as e :
		logger.error( str( e ) )
		logger.error( "Error selecting the correct option '%s' from drop down '%s'" % ( itemValue , dropDownID ) )
		actionsOnFail.exitTestScriptGracefully( testData )

def selectDropDownItemByIDOld( testData , dropDownID , itemText ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_id( dropDownID ).click()
		pause( testData , testData['dropDownExpandPause'] )
	except Exception as e :
		logger.error(str(e))
		logger.error("There was an ERROR locating the dropdown box dropDownID '%s'" % dropDownID )
		actionsOnFail.exitTestScriptGracefully( testData )
	dropDown = driver.find_element_by_id( dropDownID )
	itemTextFound = False
	try :
		for option in dropDown.find_elements_by_tag_name('option'):
			logger.info("Option = '%s' // Looking for '%s'" % ( option.text , itemText ))
			if itemText in option.text :
				mouseOverByXPath( testData , option )
				option.click()
				logger.info("Clicked to open drop down '%s'" % dropDownID)
				pause( testData , testData['dropDownExpandPause'] )
				itemTextFound = True
				break
	except Exception as e :
		logger.error(str(e))
		logger.error("There was an ERROR collecting options from the dropdown box dropDownID '%s' or selecting option '%s'" % ( dropDownID , itemText ))
		actionsOnFail.exitTestScriptGracefully( testData )
	if itemTextFound == True :
		logger.passed("Option '%s' was found and selected" % itemText )
		return "PASSED"
	else :
		logger.failed("Option '%s' could not be found in drop down '%s'" % ( itemText , dropDownID ))
		actionsOnFail.exitTestScriptGracefully( testData )

def selectDropDownItemByXPath( testData , dropDownXPath , itemText ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_xpath( dropDownXPath ).click()
		pause( testData , testData['dropDownExpandPause'] )
	except Exception as e :
		logger.error(str(e))
		logger.error("There was an ERROR locating the dropdown box dropDownXPath '%s'" % dropDownXPath )
		actionsOnFail.exitTestScriptGracefully( testData )
	dropDown = driver.find_element_by_xpath( dropDownXPath )
	itemTextFound = False
	logger.info( "'%s' options found in drop down xpath '%s'" % ( len( dropDown.find_elements_by_tag_name('option') ) , dropDownXPath ) )
	try :
		for option in dropDown.find_elements_by_tag_name('option'):
			logger.info("Option = '%s' // Looking for '%s'" % ( option.text , itemText ))
			if itemText in option.text :
				option.click()
				logger.info("Clicked to open drop down '%s'" % dropDownXPath)
				pause( testData , testData['dropDownExpandPause'] )
				itemTextFound = True
				break
	except Exception as e :
		logger.error(str(e))
		logger.error("There was an ERROR collecting options from the dropdown box dropDownXPath '%s' or selecting option '%s'" % ( dropDownXPath , itemText ))
		actionsOnFail.exitTestScriptGracefully( testData )
	if itemTextFound == True :
		logger.passed("Option '%s' was found and selected" % itemText )
		return "PASSED"
	else :
		logger.failed("Option '%s' could not be found in drop down '%s'" % ( itemText , dropDownXPath ))
		actionsOnFail.exitTestScriptGracefully( testData )

def selectDropDownItemByCSS( testData , dropDownCSS , itemText ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_css_selector( dropDownCSS ).click()
		pause( testData , testData['dropDownExpandPause'] )
	except Exception as e :
		logger.error(str(e))
		logger.error("There was an ERROR locating the dropdown box dropDownCSS '%s'" % dropDownCSS )
		actionsOnFail.exitTestScriptGracefully( testData )
	dropDown = driver.find_element_by_css_selector( dropDownCSS )
	itemTextFound = False
	try :
		for option in dropDown.find_elements_by_tag_name('option'):
			logger.info("Option = '%s' // Looking for '%s'" % ( option.text , itemText ))
			if itemText in option.text :
				option.click()
				logger.info("Clicked to open drop down '%s'" % dropDownCSS)
				pause( testData , testData['dropDownExpandPause'] )
				itemTextFound = True
				break
	except Exception as e :
		logger.error(str(e))
		logger.error("There was an ERROR collecting options from the dropdown box dropDownCSS '%s' or selecting option '%s'" % ( dropDownCSS , itemText ))
		actionsOnFail.exitTestScriptGracefully( testData )
	if itemTextFound == True :
		logger.passed("Option '%s' was found and selected" % itemText )
		return "PASSED"
	else :
		logger.failed("Option '%s' could not be found in drop down '%s'" % ( itemText , dropDownCSS ))
		actionsOnFail.exitTestScriptGracefully( testData )

def selectDropDownItemByName( testData , dropDownName , itemText ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_name( dropDownName ).click()
		pause( testData , testData['dropDownExpandPause'] )
	except Exception as e :
		logger.error(str(e))
		logger.error("There was an ERROR locating the dropdown box dropDownName '%s'" % dropDownName )
		actionsOnFail.exitTestScriptGracefully( testData )
	dropDown = driver.find_element_by_name( dropDownName )
	itemTextFound = False
	try :
		for option in dropDown.find_elements_by_tag_name('option'):
			logger.info("Option = '%s' // Looking for '%s'" % ( option.text , itemText ))
			if itemText in option.text :
				option.click()
				logger.info("Clicked to open drop down '%s'" % dropDownName)
				pause( testData , testData['dropDownExpandPause'] )
				itemTextFound = True
				break
	except Exception as e :
		logger.error(str(e))
		logger.error("There was an ERROR collecting options from the dropdown box dropDownName '%s' or selecting option '%s'" % ( dropDownName , itemText ))
		actionsOnFail.exitTestScriptGracefully( testData )
	if itemTextFound == True :
		logger.passed("Option '%s' was found and selected" % itemText )
		return "PASSED"
	else :
		logger.failed("Option '%s' could not be found in drop down '%s'" % ( itemText , dropDownName ))
		actionsOnFail.exitTestScriptGracefully( testData )
		
def selectDropDownItemByDescription( testData , fieldId , dropDownItemDesc ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		Select(driver.find_element_by_id( fieldId )).select_by_visible_text(dropDownItemDesc)
		logger.passed("Option '%s' has been found in the drop down" % dropDownItemDesc)
		return "PASSED"
	except Exception as e :
		logger.error(str(e))
		logger.error("There was an ERROR locating the item by description '%s'" % dropDownItemDesc )
		actionsOnFail.exitTestScriptGracefully( testData )
		return "ERROR"

############################### STORE FUNCTIONS ###################################

## attribute
def storeAttributeByXPath( testData , xpath , attribute , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_xpath( xpath )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		testData[variableName] = "There was an ERROR trying to store attribute '%s' from xpath '%s' here" % ( attribute , xpath )
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_xpath( xpath ).get_attribute( attribute )
		logger.data("Attribute '%s' (found at xpath '%s') = '%s' (stored as '%s' in testData)" % ( attribute , xpath , testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (xpath: '%s') was found, but attribute '%s' could not be stored" % ( xpath , attribute ))
		testData[variableName] = "There was an ERROR trying to store attribute '%s' from xpath '%s' here" % ( attribute , xpath )
		actionsOnFail.performActions(testData)
		return "FAILED"

def storeAttributeByCSS( testData , css_selector , attribute , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_css_selector( css_selector )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		testData[variableName] = "There was an ERROR trying to store attribute '%s' from css_selector '%s' here" % ( attribute , css_selector )
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_css_selector( css_selector ).get_attribute( attribute )
		logger.data("Attribute '%s' (found at css_selector '%s') = '%s' (stored as '%s' in testData)" % ( attribute , css_selector , testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (css_selector: '%s') was found, but attribute '%s' could not be stored" % ( css_selector , attribute ))
		testData[variableName] = "There was an ERROR trying to store attribute '%s' from css_selector '%s' here" % ( attribute , css_selector )
		actionsOnFail.performActions(testData)
		return "FAILED"

def storeAttributeByID( testData , elementID , attribute , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_id( elementID )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		testData[variableName] = "There was an ERROR trying to store attribute '%s' from elementID '%s' here" % ( attribute , elementID )
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_id( elementID ).get_attribute( attribute )
		logger.data("Attribute '%s' (found at elementID '%s') = '%s' (stored as '%s' in testData)" % ( attribute , elementID , testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (elementID: '%s') was found, but attribute '%s' could not be stored" % ( elementID , attribute ))
		testData[variableName] = "There was an ERROR trying to store attribute '%s' from elementID '%s' here" % ( attribute , elementID )
		actionsOnFail.performActions(testData)
		return "FAILED"

def storeAttributeByName( testData , name , attribute , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_name( name )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		testData[variableName] = "There was an ERROR trying to store attribute '%s' from name '%s' here" % ( attribute , name )
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_name( name ).get_attribute( attribute )
		logger.data("Attribute '%s' (found at name '%s') = '%s' (stored as '%s' in testData)" % ( attribute , name , testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (name: '%s') was found, but attribute '%s' could not be stored" % ( name , attribute ))
		testData[variableName] = "There was an ERROR trying to store attribute '%s' from name '%s' here" % ( attribute , name )
		actionsOnFail.performActions(testData)
		return "FAILED"

def storeAttributeByLink( testData , link , attribute , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_link_text( link )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		testData[variableName] = "There was an ERROR trying to store attribute '%s' from link '%s' here" % ( attribute , link )
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_link_text( link ).get_attribute( attribute )
		logger.data("Attribute '%s' (found at link '%s') = '%s' (stored as '%s' in testData)" % ( attribute , link , testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (link: '%s') was found, but attribute '%s' could not be stored" % ( link , attribute ))
		testData[variableName] = "There was an ERROR trying to store attribute '%s' from link '%s' here" % ( attribute , link )
		actionsOnFail.performActions(testData)
		return "FAILED"

## selected (e.g. check boxes, radio buttons)
def storeSelectedByXPath( testData , xpath , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_xpath( xpath )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		testData[variableName] = "There was an ERROR trying to store 'selected status' for xpath '%s' here" % xpath
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_xpath( xpath ).is_selected()
		logger.data("'Selected status' for xpath '%s' = '%s' (stored as '%s')" % ( xpath , testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (xpath: '%s') was found, but 'selected status' could not be stored" % xpath )
		testData[variableName] = "There was an ERROR trying to store 'selected status' for xpath '%s' here" % xpath
		actionsOnFail.performActions(testData)
		return "FAILED"

def storeSelectedByCSS( testData , css_selector , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_css_selector( css_selector )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		testData[variableName] = "There was an ERROR trying to store 'selected status' for css_selector '%s' here" % css_selector
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_css_selector( css_selector ).is_selected()
		logger.data("'Selected status' for css_selector '%s' = '%s' (stored as '%s')" % ( css_selector , testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (css_selector: '%s') was found, but 'selected status' could not be stored" % css_selector )
		testData[variableName] = "There was an ERROR trying to store 'selected status' for css_selector '%s' here" % css_selector
		actionsOnFail.performActions(testData)
		return "FAILED"

def storeSelectedByID( testData , elementID , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_id( elementID )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		testData[variableName] = "There was an ERROR trying to store 'selected status' for elementID '%s' here" % elementID
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_id( elementID ).is_selected()
		logger.data("'Selected status' for elementID '%s' = '%s' (stored as '%s')" % ( elementID , testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (elementID: '%s') was found, but 'selected status' could not be stored" % elementID )
		testData[variableName] = "There was an ERROR trying to store 'selected status' for elementID '%s' here" % elementID
		actionsOnFail.performActions(testData)
		return "FAILED"

def storeSelectedByName( testData , name , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_name( name )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		testData[variableName] = "There was an ERROR trying to store 'selected status' for name '%s' here" % name
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_name( name ).is_selected()
		logger.data("'Selected status' for name '%s' = '%s' (stored as '%s')" % ( name , testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (name: '%s') was found, but 'selected status' could not be stored" % name )
		testData[variableName] = "There was an ERROR trying to store 'selected status' for name '%s' here" % name
		actionsOnFail.performActions(testData)
		return "FAILED"

## location
def storeLocation( testData , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		testData[variableName] = driver.current_url
		logger.data("Current Location = '%s' (stored as '%s')" % ( testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Current Location could not be stored, error: %s" % str(e) )
		testData[variableName] = "There was an ERROR trying to store 'current location' here"
		actionsOnFail.performActions(testData)
		return "FAILED"

## title
def storeTitle( testData , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		testData[variableName] = driver.title
		logger.data("'Title' = '%s' (stored as '%s')" % ( testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("'Title' could not be stored, error: %s" % str(e) )
		testData[variableName] = "There was an ERROR trying to store 'title' here"
		actionsOnFail.performActions(testData)
		return "FAILED"

## text
def storeTextByXPath( testData , xpath , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_xpath( xpath )
	except Exception as e :
		logger.error(str(e))
		testData[variableName] = "There was an ERROR trying to 'store text' from xpath '%s' here" % xpath
		actionsOnFail.performActions(testData)
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_xpath( xpath ).text
		logger.data("Variable '%s' stored as '%s'" % ( variableName , testData[variableName] ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (xpath: '%s') was found, but text could not be stored" % xpath )
		testData[variableName] = "There was an ERROR trying to 'store text' from xpath '%s' here, error: %s" % ( xpath , str(e) )
		actionsOnFail.performActions(testData)
		return "FAILED"

def storeTextByCSS( testData , css_selector , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_css_selector( css_selector )
	except Exception as e :
		logger.error(str(e))
		testData[variableName] = "There was an ERROR trying to 'store text' from css_selector '%s' here" % css_selector
		actionsOnFail.performActions(testData)
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_css_selector( css_selector ).text
		logger.data("Variable '%s' stored as '%s'" % ( variableName , testData[variableName] ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (css_selector: '%s') was found, but text could not be stored, error: %s" % ( css_selector , str(e) ))
		testData[variableName] = "There was an ERROR trying to 'store text' from css_selector '%s' here" % css_selector
		actionsOnFail.performActions(testData)
		return "FAILED"

def storeTextByID( testData , elementID , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_id( elementID )
	except Exception as e :
		logger.error(str(e))
		testData[variableName] = "There was an ERROR trying to 'store text' from elementID '%s' here" % elementID
		actionsOnFail.performActions(testData)
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_id( elementID ).text
		logger.data("Variable '%s' stored as '%s'" % ( variableName , testData[variableName] ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (elementID: '%s') was found, but text could not be stored, error: %s" % ( elementID , str(e) ))
		testData[variableName] = "There was an ERROR trying to 'store text' from elementID '%s' here" % elementID
		actionsOnFail.performActions(testData)
		return "FAILED"

def storeTextByName( testData , name , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_name( name )
	except Exception as e :
		logger.error(str(e))
		testData[variableName] = "There was an ERROR trying to 'store text' from name '%s' here" % name
		actionsOnFail.performActions(testData)
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_name( name ).text
		logger.data("Variable '%s' stored as '%s'" % ( variableName , testData[variableName] ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (name: '%s') was found, but text could not be stored, error: %s" % ( name , str(e) ))
		testData[variableName] = "There was an ERROR trying to 'store text' from name '%s' here" % name
		actionsOnFail.performActions(testData)
		return "FAILED"

## visible
def storeVisibleByXPath( testData , xpath , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_xpath( xpath )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		testData[variableName] = "There was an ERROR trying to store 'visible status' for xpath '%s' here" % xpath
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_xpath( xpath ).is_displayed()
		logger.data("'Visible status' for xpath '%s' = '%s' (stored as '%s')" % ( xpath , testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (xpath: '%s') was found, but 'visible status' could not be stored" % xpath )
		testData[variableName] = "There was an ERROR trying to store 'visible status' for xpath '%s' here" % xpath
		actionsOnFail.performActions(testData)
		return "FAILED"

def storeVisibleByCSS( testData , css_selector , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_css_selector( css_selector )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		testData[variableName] = "There was an ERROR trying to store 'visible status' for css_selector '%s' here" % css_selector
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_css_selector( css_selector ).is_displayed()
		logger.data("'Visible status' for css_selector '%s' = '%s' (stored as '%s')" % ( css_selector , testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (css_selector: '%s') was found, but 'visible status' could not be stored" % css_selector )
		testData[variableName] = "There was an ERROR trying to store 'visible status' for css_selector '%s' here" % css_selector
		actionsOnFail.performActions(testData)
		return "FAILED"

def storeVisibleByID( testData , elementID , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_id( elementID )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		testData[variableName] = "There was an ERROR trying to store 'visible status' for elementID '%s' here" % elementID
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_id( elementID ).is_displayed()
		logger.data("'Visible status' for elementID '%s' = '%s' (stored as '%s')" % ( elementID , testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (elementID: '%s') was found, but 'visible status' could not be stored" % elementID )
		testData[variableName] = "There was an ERROR trying to store 'visible status' for elementID '%s' here" % elementID
		actionsOnFail.performActions(testData)
		return "FAILED"

def storeVisibleByName( testData , name , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_name( name )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions(testData)
		testData[variableName] = "There was an ERROR trying to store 'visible status' for name '%s' here" % name
		return "FAILED"
	try :
		testData[variableName] = driver.find_element_by_name( name ).is_displayed()
		logger.data("'Visible status' for name '%s' = '%s' (stored as '%s')" % ( name , testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Element (name: '%s') was found, but 'visible status' could not be stored" % name )
		testData[variableName] = "There was an ERROR trying to store 'visible status' for name '%s' here" % name
		actionsOnFail.performActions(testData)
		return "FAILED"

## xpath and css count
def storeXPathCount( testData , xpath , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		testData[variableName] = len( driver.find_elements_by_xpath( xpath ) )
		logger.data("'xpath count' for xpath '%s' = '%s' (stored as '%s')" % ( xpath , testData[variableName] , variableName ))
		return "PASSED"
	except :
		logger.error("Could not determine an xpath count for '%s'" % xpath )
		testData[variableName] = "This variable could not be set (should have been an xpath count using '%s')" % xpath
		actionsOnFail.performActions( testData )
		return "FAILED"

def storeCSSCount( testData , css_selector , variableName ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		testData[variableName] = len( driver.find_elements_by_css_selector( css_selector ) )
		logger.data("'css count' for css_selector '%s' = '%s' (stored as '%s')" % ( css_selector , testData[variableName] , variableName ))
		return "PASSED"
	except Exception as e :
		logger.failed("Could not determine a css count for '%s'" % css_selector )
		logger.failed("Exception error: %s" % str(e) )
		testData[variableName] = "This variable could not be set (should have been a css count using '%s')" % css_selector
		actionsOnFail.performActions( testData )
		return "FAILED"

############################## VERIFY FUNCTIONS ###################################

## verify (not) equal
def verifyEqual( testData , value1 , value2 ) :
	logger = testData['logger']
	if str(value1) == str(value2):
		logger.passed("'%s' == '%s'" % ( value1 , value2 ))
		return "PASSED"
	else:
		logger.failed("'%s' != '%s'" % ( value1 , value2 ))
		actionsOnFail.performActions(testData)
		return "FAILED"

def verifyNotEqual( testData , value1 , value2 ) :
	logger = testData['logger']
	if str(value1) != str(value2 ):
		logger.passed("'%s' != '%s'" % ( value1 , value2 ))
		return "PASSED"
	else:
		logger.failed("'%s' == '%s'" % ( value1 , value2 ))
		actionsOnFail.performActions(testData)
		return "FAILED"

## element present
def verifyElementPresentByID( testData , elementID ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_id( elementID )
		logger.passed("Element '%s' found by id" % elementID )
		return "PASSED"
	except Exception:
		logger.failed("Element ID '%s' was not found on the page" % elementID )
		actionsOnFail.performActions(testData)
		return "FAILED"

def verifyElementPresentByName( testData , name ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_name( name )
		logger.passed("Element '%s' found by name" % name )
		return "PASSED"
	except Exception:
		logger.failed("Element name '%s' was not found on the page" % name )
		actionsOnFail.performActions(testData)
		return "FAILED"

def verifyElementPresentByXPath( testData , xpath ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_xpath( xpath )
		logger.passed("Element '%s' found by xpath" % xpath )
		return "PASSED"
	except Exception:
		logger.failed("Element Xpath '%s' was not found on the page" % xpath )
		actionsOnFail.performActions(testData)
		return "FAILED"

def verifyElementPresentByCSS( testData , css_selector ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_css_selector( css_selector )
		logger.passed("Element '%s' found by css_selector" % css_selector )
		return "PASSED"
	except Exception:
		logger.failed("Element css_Selector '%s' was not found on the page" % css_selector )
		actionsOnFail.performActions(testData)
		return "FAILED"

def verifyElementPresentByLink( testData , link ):
	driver = testData['driver']
	logger = testData['logger']
	try:
		driver.find_element_by_link_text( link )
		logger.passed("Element '%s' found by link" %  link )
		return "PASSED"
	except Exception:
		logger.failed("Element link '%s' was not found on the page" % link )
		actionsOnFail.performActions(testData)
		return "FAILED"

## element not present
def verifyElementNotPresentByID( testData , elementID ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_id( elementID )
		logger.failed("Element '%s' found by id" % elementID )
		actionsOnFail.performActions(testData)
		return "FAILED"
	except Exception:
		logger.passed("Element ID '%s' was not found on the page" % elementID )
		return "PASSED"

def verifyElementNotPresentByName( testData , name ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_name( name )
		logger.failed("Element '%s' found by name" % name )
		actionsOnFail.performActions(testData)
		return "FAILED"
	except Exception:
		logger.failed("Element name '%s' was not found on the page" % name )
		return "PASSED"

def verifyElementNotPresentByXPath( testData , xpath ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_xpath( xpath )
		logger.failed("Element '%s' found by xpath" % xpath )
		actionsOnFail.performActions(testData)
		return "FAILED"
	except Exception:
		logger.passed("Element Xpath '%s' was not found on the page" % xpath )
		return "PASSED"

def verifyElementNotPresentByCSS( testData , css_selector ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_css_selector( css_selector )
		logger.failed("Element '%s' found by css_selector" % css_selector )
		actionsOnFail.performActions(testData)
		return "FAILED"
	except Exception:
		logger.passed("Element css_Selector '%s' was not found on the page" % css_selector )
		return "PASSED"

def verifyElementNotPresentByLink( testData , link ):
	driver = testData['driver']
	logger = testData['logger']
	try:
		driver.find_element_by_link_text( link )
		logger.failed("Element '%s' found by link" %  link )
		actionsOnFail.performActions(testData)
		return "FAILED"
	except Exception:
		logger.passed("Element link '%s' was not found on the page" % link )
		return "PASSED"

## text present
def verifyTextNotPresent(testData,text):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if text not in driver.find_element_by_css_selector("BODY").text:
			logger.passed("Text '%s' was not found on page"%text)
			return "PASSED"
		else:
			logger.failed("Text '%s' was found on the page"%text)
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyTextPresent(testData,text):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if text in driver.find_element_by_css_selector("BODY").text:
			logger.passed("Text '%s' was found on page"%text)
			return "PASSED"
		else:
			logger.failed("Text '%s' was not found on the page"%text)
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

## text
def verifyTextByID( testData , elementID , text ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_id( elementID )
	except Exception as e:
#		logger.error(str(e))
		logger.failed("Element ID '%s' was not found on the page" % elementID )
		actionsOnFail.performActions(testData)
		return "FAILED"
	try:
		elementText = driver.find_element_by_id( elementID ).text
		if text == elementText:
			logger.passed("Text '%s' was found in element '%s'"%( text , elementID ))
			return "PASSED"
		else:
			logger.failed("Text '%s' was not found in element '%s'" % ( text , elementID ))
			logger.failed("Text '%s' was found in element '%s'" % ( elementText , elementID ))
			actionsOnFail.performActions( testData )
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotTextByID( testData , elementID , text ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_id( elementID )
	except Exception as e:
#		logger.error(str(e))
		logger.failed("Element ID '%s' was not found on the page" % elementID )
		actionsOnFail.performActions( testData )
		return "FAILED"
	try:
		if text != driver.find_element_by_id( elementID ).text:
			logger.passed("Text '%s' was not found in element '%s'"%( text , elementID ))
			return "PASSED"
		else:
			logger.failed("Text '%s' was found in element '%s'"%( text , elementID ))
			actionsOnFail.performActions( testData )
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"


def verifyTextByXPath( testData , xpath , text ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_xpath( xpath )
	except Exception as e:
#		logger.error(str(e))
		logger.failed("Element xpath '%s' was not found on the page" % xpath )
		actionsOnFail.performActions(testData)
		return "FAILED"
	try:
		elementText = driver.find_element_by_xpath( xpath ).text
		if text == elementText:
			logger.passed("Text '%s' was found in xpath '%s'"%( text , xpath ))
			return "PASSED"
		else:
			logger.failed("Text '%s' was not found in element '%s'"%( text , xpath ))
			logger.failed("Text '%s' was found in element '%s'"%( elementText , xpath ))
			actionsOnFail.performActions( testData )
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotTextByXPath( testData , xpath , text ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_xpath( xpath )
	except Exception as e:
#		logger.error(str(e))
		logger.failed("Element xpath '%s' was not found on the page" % xpath )
		actionsOnFail.performActions( testData )
		return "FAILED"
	try:
		if text != driver.find_element_by_xpath( xpath ).text:
			logger.passed("Text '%s' was not found in xpath '%s'"%( text , xpath ))
			return "PASSED"
		else:
			logger.failed("Text '%s' was found in xpath '%s'"%( text , xpath ))
			actionsOnFail.performActions( testData )
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyTextByCSS( testData , css_selector , text ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_css_selector( css_selector )
	except Exception as e:
#		logger.error(str(e))
		logger.failed("Element css_selector '%s' was not found on the page" % css_selector )
		actionsOnFail.performActions(testData)
		return "FAILED"
	try:
		elementText = driver.find_element_by_css_selector( css_selector ).text
		if text == elementText:
			logger.passed("Text '%s' was found in css_selector '%s'"%( text , css_selector ))
			return "PASSED"
		else:
			logger.failed("Text '%s' was not found in element '%s'"%( text , css_selector ))
			logger.failed("Text '%s' was found in element '%s'"%( elementText , css_selector ))
			actionsOnFail.performActions( testData )
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotTextByCSS(testData,css_selector,text):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_css_selector( css_selector )
	except Exception as e:
#		logger.error(str(e))
		logger.failed("Element css_selector '%s' was not found on the page" % css_selector )
		actionsOnFail.performActions(testData)
		return "FAILED"
	try:
		if text != driver.find_element_by_css_selector(css_selector).text:
			logger.passed("Text '%s' was not found in css_selector '%s'"%(text,css_selector))
			return "PASSED"
		else:
			logger.failed("Text '%s' was found in css_selector '%s'"%(text,css_selector))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyTextByName( testData , name , text ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_name( name )
	except Exception as e:
#		logger.error(str(e))
		logger.failed("Element name '%s' was not found on the page" % name )
		actionsOnFail.performActions(testData)
		return "FAILED"
	try:
		elementText = driver.find_element_by_name( name ).text
		if text == elementText:
			logger.passed("Text '%s' was found in name '%s'"%( text , name ))
			return "PASSED"
		else:
			logger.failed("Text '%s' was not found in element '%s'"%( text , name ))
			logger.failed("Text '%s' was found in element '%s'"%( elementText , name ))
			actionsOnFail.performActions( testData )
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotTextByName( testData , name , text ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_name( name )
	except Exception as e:
#		logger.error(str(e))
		logger.failed("Element name '%s' was not found on the page" % name )
		actionsOnFail.performActions(testData)
		return "FAILED"
	try:
		if text != driver.find_element_by_name( name ).text:
			logger.passed("Text '%s' was not found in name '%s'"%( text , name ))
			return "PASSED"
		else:
			logger.failed("Text '%s' was found in name '%s'"%( text , name ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

## attribute
def verifyAttributeByXPath( testData , xpath , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		actual = driver.find_element_by_xpath( xpath ).get_attribute( attribute )
		if value == actual :
			logger.passed("Value '%s' was found in xpath '%s', attribute '%s'"%( value , xpath , attribute ))
			return "PASSED"
		else:
			logger.failed("Value '%s' was not found in xpath '%s', attribute '%s' ('%s' was found instead)"%( value , xpath , attribute , actual ))
			actionsOnFail.performActions( testData )
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotAttributeByXPath( testData , xpath , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if value != driver.find_element_by_xpath( xpath ).get_attribute( attribute ):
			logger.passed("Value '%s' was not found in xpath '%s', attribute '%s'"%( value , xpath , attribute ))
			return "PASSED"
		else:
			logger.failed("Value '%s' was found in xpath '%s', attribute '%s'"%( value , xpath , attribute ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"
		
def verifyAttributeByCSS( testData , css_selector , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		actual = driver.find_element_by_xpath( css_selector ).get_attribute( attribute )
		if value == actual :
			logger.passed("Value '%s' was found in css_selector '%s', attribute '%s'"%( value , css_selector , attribute))
			return "PASSED"
		else:
			logger.failed("Value '%s' was not found in css_selector '%s', attribute '%s' ('%s' was found instead)"%( value , css_selector , attribute , actual ))
			actionsOnFail.performActions( testData )
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotAttributeByCSS( testData , css_selector , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if value != driver.find_element_by_css_selector(css_selector).get_attribute(attribute):
			logger.passed("Value '%s' was not found in css_selector '%s', attribute '%s'"%( value , css_selector , attribute ))
			return "PASSED"
		else:
			logger.failed("Value '%s' was found in css_selector '%s', attribute '%s'"%( value , css_selector , attribute ))
			actionsOnFail.performActions( testData )
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyAttributeByID( testData , elementID , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		actual = driver.find_element_by_id( elementID ).get_attribute( attribute )
		if value == actual :
			logger.passed("Value '%s' was found in elementID '%s', attribute '%s'" % ( value , elementID , attribute ))
			return "PASSED"
		else:
			logger.failed("Value '%s' was not found in elementID '%s', attribute '%s' ('%s' was found instead)" % ( value , elementID , attribute , actual ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotAttributeByID( testData , elementID , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if value != driver.find_element_by_id( elementID ).get_attribute( attribute ):
			logger.passed("Value '%s' was not found in elementID '%s', attribute '%s'"%( value , elementID , attribute ))
			return "PASSED"
		else:
			logger.failed("Value '%s' was found in elementID '%s', attribute '%s'"%( value , elementID , attribute ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

## checked
def verifyCheckedByID( testData , elementID ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_id( elementID ).is_selected() == True :
			logger.passed("Element '%s' was checked" % ( elementID ))
			return "PASSED"
		else:
			logger.failed("Element '%s' was not checked" % ( elementID ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotCheckedByID( testData , elementID ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_id( elementID ).is_selected() == False :
			logger.passed("Element '%s' was not checked" % ( elementID ))
			return "PASSED"
		else:
			logger.failed("Element '%s' was checked" % ( elementID ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyCheckedByXPath( testData , xpath ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_xpath( xpath ).is_selected() == True :
			logger.passed("xpath '%s' was checked" % ( xpath ))
			return "PASSED"
		else:
			logger.failed("xpath '%s' was not checked" % ( xpath ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotCheckedByXPath( testData , xpath ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_xpath( xpath ).is_selected() == False :
			logger.passed("xpath '%s' was not checked" % ( xpath ))
			return "PASSED"
		else:
			logger.failed("xpath '%s' was checked" % ( xpath ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyCheckedByCSS( testData , css_selector ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_css_selector( css_selector ).is_selected() == True :
			logger.passed("Element '%s' was checked" % ( css_selector ))
			return "PASSED"
		else:
			logger.failed("Element '%s' was not checked" % ( css_selector ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotCheckedByCSS( testData , css_selector ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_css_selector( css_selector ).is_selected() == False :
			logger.passed("css_selector '%s' was not checked" % ( css_selector ))
			return "PASSED"
		else:
			logger.failed("css_selector '%s' was checked" % ( css_selector ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyCheckedByName( testData , name ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_name( name ).is_selected() == True :
			logger.passed("Element '%s' was checked" % ( name ))
			return "PASSED"
		else:
			logger.failed("Element '%s' was not checked" % ( name ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotCheckedByName( testData , name ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_name( name ).is_selected() == False :
			logger.passed("Element '%s' was not checked" % ( name ))
			return "PASSED"
		else:
			logger.failed("Element '%s' was checked" % ( name ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

## title
def verifyTitle( testData , text ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if text == driver.title :
			logger.passed("Page title '%s' matched '%s'"%( driver.title , text ))
			return "PASSED"
		else:
			logger.failed("Page title '%s' did not match '%s'"%( driver.title , text ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"
	
## location
def verifyLocation( testData , location ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if location in driver.current_url :
			logger.passed("Current location ('%s') is correct" % ( driver.current_url ))
			return "PASSED"
		else:
			logger.failed("Current location ('%s') was not what was expected ('%s')" % ( driver.current_url, location ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotLocation( testData , location ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if location not in driver.current_url :
			logger.passed("Current location ('%s') is correct" % ( driver.current_url ))
			return "PASSED"
		else:
			logger.failed("Current location ('%s') was not what was expected ('%s')" % ( location , driver.current_url ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"


## visible
def verifyVisibleByID( testData , elementID ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_id( elementID ).is_displayed() == True :
			logger.passed("Element '%s' was visible" % ( elementID ))
			return "PASSED"
		else:
			logger.failed("Element '%s' was not visible" % ( elementID ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotVisibleByID( testData , elementID ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_id( elementID ).is_displayed() == False :
			logger.passed("Element '%s' was not visible" % ( elementID ))
			return "PASSED"
		else:
			logger.failed("Element '%s' was visible" % ( elementID ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyVisibleByXPath( testData , xpath ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_xpath( xpath ).is_displayed() == True :
			logger.passed("xpath '%s' was visible" % ( xpath ))
			return "PASSED"
		else:
			logger.failed("xpath '%s' was not visible" % ( xpath ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotVisibleByXPath( testData , xpath ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_xpath( xpath ).is_displayed() == False :
			logger.passed("xpath '%s' was not visible" % ( xpath ))
			return "PASSED"
		else:
			logger.failed("xpath '%s' was visible" % ( xpath ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyVisibleByCSS( testData , css_selector ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_css_selector( css_selector ).is_displayed() == True :
			logger.passed("Element '%s' was visible" % ( css_selector ))
			return "PASSED"
		else:
			logger.failed("Element '%s' was not visible" % ( css_selector ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotVisibleByCSS( testData , css_selector ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_css_selector( css_selector ).is_displayed() == False :
			logger.passed("css_selector '%s' was not visible" % ( css_selector ))
			return "PASSED"
		else:
			logger.failed("css_selector '%s' was visible" % ( css_selector ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyVisibleByName( testData , name ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_name( name ).is_displayed() == True :
			logger.passed("Element '%s' was visible" % ( name ))
			return "PASSED"
		else:
			logger.failed("Element '%s' was not visible" % ( name ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotVisibleByName( testData , name ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_name( name ).is_displayed() == False :
			logger.passed("Element '%s' was not checked" % ( name ))
			return "PASSED"
		else:
			logger.failed("Element '%s' was visible" % ( name ))
			actionsOnFail.performActions(testData)
			return "FAILED"
	except Exception as e:
		logger.error(str(e))
		return "FAILED"

def verifyNotEditableByID(testData, elementID):
	driver = testData['driver']
	logger = testData['logger']
	text = "Text has been edited"
	try :
		driver.find_element_by_id( elementID )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try:
		driver.find_element_by_id(elementID).clear()
		driver.find_element_by_id( elementID ).send_keys( text )
		if driver.find_element_by_id(elementID).text == text:
			logger.failed("Found text '%s' in element ID '%s' this field should NOT be editable"%(text,elementID))
			return "FAILED"
		else:
			logger.passed("Text '%s'  was not able to be entered into element '%s' - confirmed NOT editable"%( text , elementID ))
			return "PASSED"
	except Exception as e:
		if "Element is disabled and so may not be used for actions" in str(e):
			logger.passed("Text '%s'  was not able to be entered into element '%s' - confirmed NOT editable"%( text , elementID ))
			return "PASSED"
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"

def verifyNotEditableByXPath(testData, xpath):
	driver = testData['driver']
	logger = testData['logger']
	text = "Text has been edited"
	try :
		driver.find_element_by_xpath( xpath )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try:
		driver.find_element_by_xpath(xpath).clear()
		driver.find_element_by_xpath( xpath ).send_keys( text )
		if driver.find_element_by_xpath(xpath).text == text:
			logger.failed("Found text '%s' in element '%s' this field should NOT be editable"%(text,xpath))
			return "FAILED"
		else:
			logger.passed("Text '%s'  was not able to be entered into element '%s' - confirmed NOT editable"%( text , xpath ))
			return "PASSED"
	except Exception as e:
		if "Element is disabled and so may not be used for actions" in str(e):
			logger.passed("Text '%s'  was not able to be entered into element '%s' - confirmed NOT editable"%( text , xpath ))
			return "PASSED"
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"

def verifyNotEditableByCSS(testData, css_selector):
	driver = testData['driver']
	logger = testData['logger']
	text = "Text has been edited"
	try :
		driver.find_element_by_css_selector( css_selector )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try:
		driver.find_element_by_css_selector(css_selector).clear()
		driver.find_element_by_css_selector( css_selector ).send_keys( text )
		if driver.find_element_by_css_selector(css_selector).text == text:
			logger.failed("Found text '%s' in element '%s' this field should NOT be editable"%(text,css_selector))
			return "FAILED"
		else:
			logger.passed("Text '%s' was not able to be entered into element '%s' - confirmed NOT editable"%( text , css_selector ))
			return "PASSED"
	except Exception as e:
		if "Element is disabled and so may not be used for actions" in str(e):
			logger.passed("Text '%s'  was not able to be entered into element '%s' - confirmed NOT editable"%( text , css_selector ))
			return "PASSED"
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"

def verifyNotEditableByName(testData, name):
	driver = testData['driver']
	logger = testData['logger']
	text = "Text has been edited"
	try :
		driver.find_element_by_name(name )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try:
		driver.find_element_by_name(name).clear()
		driver.find_element_by_name(name).send_keys( text )
		if driver.find_element_by_name(name).text == text:
			logger.failed("Found text '%s' in element '%s' this field should NOT be editable"%(text,name))
			return "FAILED"
		else:
			logger.passed("Text '%s' was not able to be entered into element '%s' - confirmed NOT editable"%( text , name))
			return "PASSED"
	except Exception as e:
		if "Element is disabled and so may not be used for actions" in str(e):
			logger.passed("Text '%s'  was not able to be entered into element '%s' - confirmed NOT editable"%( text , name ))
			return "PASSED"
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"

## text by regex
def verifyTextByXPathRegex( testData , xpath , regex ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_xpath( xpath )
	except Exception as e:
		logger.failed("Element xpath '%s' was not found on the page" % xpath )
		actionsOnFail.performActions(testData)
		return "FAILED"
	regexC = re.compile( regex , re.DOTALL )
	try:
		elementText = driver.find_element_by_xpath( xpath ).text
	except Exception as e:
		logger.error( str(e) )
		return "FAILED"
	try :
		regexC.findall( elementText )[0]
		logger.passed( "Text '%s' matched regex '%s'" % ( elementText , regex ))
		return "PASSED"
	except :
		logger.failed( "Text '%s' did NOT match regex '%s'" % ( elementText , regex ))
		actionsOnFail.performActions( testData )
		return "FAILED"

def verifyTextByIDRegex( testData , elementID , regex ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_id( elementID )
	except Exception as e:
		logger.failed("Element ID '%s' was not found on the page" % elementID )
		actionsOnFail.performActions(testData)
		return "FAILED"
	regexC = re.compile( regex , re.DOTALL )
	try:
		elementText = driver.find_element_by_id( elementID ).text
	except Exception as e:
		logger.error( str(e) )
		return "FAILED"
	try :
		regexC.findall( elementText )[0]
		logger.passed( "Text '%s' matched regex '%s'" % ( elementText , regex ))
		return "PASSED"
	except :
		logger.failed( "Text '%s' did NOT match regex '%s'" % ( elementText , regex ))
		actionsOnFail.performActions( testData )
		return "FAILED"

def verifyTextByCSSRegex( testData , css_selector , regex ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_css_selector( css_selector )
	except Exception as e:
		logger.failed("Element CSS '%s' was not found on the page" % css_selector )
		actionsOnFail.performActions(testData)
		return "FAILED"
	regexC = re.compile( regex , re.DOTALL )
	try:
		elementText = driver.find_element_by_css_selector( css_selector ).text
	except Exception as e:
		logger.error( str(e) )
		return "FAILED"
	try :
		regexC.findall( elementText )[0]
		logger.passed( "Text '%s' matched regex '%s'" % ( elementText , regex ))
		return "PASSED"
	except :
		logger.failed( "Text '%s' did NOT match regex '%s'" % ( elementText , regex ))
		actionsOnFail.performActions( testData )
		return "FAILED"

## text 'in'
def verifyTextInByXPath( testData , xpath , text ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_xpath( xpath )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try :
		fullText = driver.find_element_by_xpath( xpath ).text
		logger.data("Element '%s' contains: %s" % ( xpath , fullText ))
	except Exception as e :
		logger.failed("Could not extract text from xpath: '%s'" % xpath )
		actionsOnFail.performActions( testData )
		return "FAILED"
	if text in fullText :
		logger.passed("Text '%s' was found in element '%s'" % ( text , xpath ))
		return "PASSED"
	else :
		logger.failed("Text '%s' was NOT found in element '%s' (actual text: '%s')" % ( text , xpath , fullText ))
		actionsOnFail.performActions(testData)
		return "FAILED"

def verifyTextNotInByXPath( testData , xpath , text ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_xpath( xpath )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try :
		fullText = driver.find_element_by_xpath( xpath ).text
		logger.data("Element '%s' contains: %s" % ( xpath , fullText ))
	except Exception as e :
		logger.failed("Could not extract text from xpath: '%s'" % xpath )
		actionsOnFail.performActions( testData )
		return "FAILED"
	if text not in fullText :
		logger.passed("Text '%s' was found in element '%s'" % ( text , xpath ))
		return "PASSED"
	else :
		logger.failed("Text '%s' was NOT found in element '%s'" % ( text , xpath ))
		actionsOnFail.performActions(testData)
		return "FAILED"

def verifyTextInByID( testData , elementID , text ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_id( elementID )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try :
		fullText = driver.find_element_by_id( elementID ).text
		logger.data("Element '%s' contains: %s" % ( elementID , fullText ))
	except Exception as e :
		logger.failed("Could not extract text from elementID: '%s'" % elementID )
		actionsOnFail.performActions( testData )
		return "FAILED"
	if text in fullText :
		logger.passed("Text '%s' was found in element '%s'" % ( text , elementID ))
		return "PASSED"
	else :
		logger.failed("Text '%s' was NOT found in element '%s'" % ( text , elementID ))
		actionsOnFail.performActions(testData)
		return "FAILED"

def verifyTextNotInByID( testData , elementID , text ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_id( elementID )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try :
		fullText = driver.find_element_by_id( elementID ).text
		logger.data("Element '%s' contains: %s" % ( elementID , fullText ))
	except Exception as e :
		logger.failed("Could not extract text from elementID: '%s'" % elementID )
		actionsOnFail.performActions( testData )
		return "FAILED"
	if text not in fullText :
		logger.passed("Text '%s' was found in element '%s'" % ( text , elementID ))
		return "PASSED"
	else :
		logger.failed("Text '%s' was NOT found in element '%s'" % ( text , elementID ))
		actionsOnFail.performActions(testData)
		return "FAILED"

def verifyTextInByCSS( testData , css_selector , text ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_css_selector( css_selector )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try :
		fullText = driver.find_element_by_css_selector( css_selector ).text
		logger.data("Element '%s' contains: %s" % ( css_selector , fullText ))
	except Exception as e :
		logger.failed("Could not extract text from css_selector: '%s'" % css_selector )
		actionsOnFail.performActions( testData )
		return "FAILED"
	if text in fullText :
		logger.passed("Text '%s' was found in element '%s'" % ( text , css_selector ))
		return "PASSED"
	else :
		logger.failed("Text '%s' was NOT found in element '%s'" % ( text , css_selector ))
		actionsOnFail.performActions(testData)
		return "FAILED"

def verifyTextNotInByCSS( testData , css_selector , text ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_css_selector( css_selector )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try :
		fullText = driver.find_element_by_css_selector( css_selector ).text
		logger.data("Element '%s' contains: %s" % ( css_selector , fullText ))
	except Exception as e :
		logger.failed("Could not extract text from css_selector: '%s'" % css_selector )
		actionsOnFail.performActions( testData )
		return "FAILED"
	if text not in fullText :
		logger.passed("Text '%s' was found in element '%s'" % ( text , css_selector ))
		return "PASSED"
	else :
		logger.failed("Text '%s' was NOT found in element '%s'" % ( text , css_selector ))
		actionsOnFail.performActions(testData)
		return "FAILED"

def verifyTextInByName( testData , name , text ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_name( name )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try :
		fullText = driver.find_element_by_name( name ).text
		logger.data("Element '%s' contains: %s" % ( name , fullText ))
	except Exception as e :
		logger.failed("Could not extract text from name: '%s'" % name )
		actionsOnFail.performActions( testData )
		return "FAILED"
	if text in fullText :
		logger.passed("Text '%s' was found in element '%s'" % ( text , name ))
		return "PASSED"
	else :
		logger.failed("Text '%s' was NOT found in element '%s'" % ( text , name ))
		actionsOnFail.performActions(testData)
		return "FAILED"

def verifyTextNotInByName( testData , name , text ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		driver.find_element_by_name( name )
	except Exception as e :
		logger.error(str(e))
		actionsOnFail.performActions( testData )
		return "FAILED"
	try :
		fullText = driver.find_element_by_name( name ).text
		logger.data("Element '%s' contains: %s" % ( name , fullText ))
	except Exception as e :
		logger.failed("Could not extract text from name: '%s'" % name )
		actionsOnFail.performActions( testData )
		return "FAILED"
	if text not in fullText :
		logger.passed("Text '%s' was found in element '%s'" % ( text , name ))
		return "PASSED"
	else :
		logger.failed("Text '%s' was NOT found in element '%s'" % ( text , name ))
		actionsOnFail.performActions(testData)
		return "FAILED"


###################################################################################
###################################################################################
############################## ASSERT FUNCTIONS ###################################

## url
def assertCurrentUrl( testData , url ) :
	driver = testData['driver']
	logger = testData['logger']
	try :
		currentURL = driver.current_url
		logger.debug("Current URL is %s"%currentURL)
	except Exception as e :
		logger.error( str( e ) )
		actionsOnFail.performActions( testData )
		return "FAILED"
	timeout = 2
	while True :
		currentURL = driver.current_url
		if url in currentURL :
			break
		elif timeout <= 0 :
			logger.failed( "[ASSERTION] Current URL '%s' did not match expected URL '%s'" % ( currentURL , url ) )
			return "FAILED"
		time.sleep( 0.2 )
		timeout -= 0.2
	logger.passed( "Driver is at '%s' (exact current URL = '%s')" % ( url , currentURL ) )
	return "PASSED"
		

## (not) equal
def assertEqual( testData , value1 , value2 ) :
	logger = testData['logger']
	if str(value1) ==  str(value2):
		logger.passed("'%s' == '%s'" % ( value1 , value2 ))
		return "PASSED"
	else:
		logger.failed("[ASSERTION] '%s' != '%s'" % ( value1 , value2 ))
		actionsOnFail.exitTestScriptGracefully( testData )
		return "FAILED"

def assertNotEqual( testData , value1 , value2 ) :
	logger = testData['logger']
	if str(value1) !=  str(value2):
		logger.passed("'%s' != '%s'" % ( value1 , value2 ))
		return "PASSED"
	else:
		logger.failed("[ASSERTION] '%s' == '%s'" % ( value1 , value2 ))
		actionsOnFail.exitTestScriptGracefully( testData )

## element present
def assertElementPresentByID( testData , elementID ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_id( elementID )
		logger.passed("Element found: ID='%s'" % elementID)
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		logger.failed("[ASSERTION] Element ID '%s' was not found on the page" % elementID )
		actionsOnFail.exitTestScriptGracefully( testData )
		
def assertElementNotPresentByID( testData , elementID ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_id( elementID )
		logger.failed("[ASSERTION] Element ID '%s' was found on the page" % elementID )
		actionsOnFail.exitTestScriptGracefully( testData )
	except :
		logger.passed("Element not found: ID='%s'" % elementID)
		return "PASSED"

def assertElementPresentByName( testData , name ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_name( name )
		logger.passed("Element found: Name='%s'" % name)
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		logger.failed("[ASSERTION] Element name '%s' was not found on the page" % name )
		actionsOnFail.exitTestScriptGracefully( testData )

def assertElementPresentByXPath( testData , xpath ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_xpath( xpath )
		logger.passed("Element found: xpath='%s'" % xpath )
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		logger.failed("[ASSERTION] Element Xpath '%s' was not found on the page" % xpath )
		actionsOnFail.exitTestScriptGracefully(testData)

def assertElementNotPresentByXPath( testData , xpath ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_xpath( xpath )
		logger.failed("[ASSERTION] XPath '%s' was found on the page" % xpath )
		actionsOnFail.exitTestScriptGracefully( testData )
	except :
		logger.passed("Element not found: xpath='%s'" % xpath)
		return "PASSED"

def assertElementPresentByCSS( testData , css_selector ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_css_selector( css_selector )
		logger.passed("Element found: css_selector='%s'" % css_selector )
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		logger.failed("[ASSERTION] Element css_Selector '%s' was not found on the page" % css_selector )
		actionsOnFail.exitTestScriptGracefully( testData )

def assertElementPresentByLink( testData , link ):
	driver = testData['driver']
	logger = testData['logger']
	try:
		driver.find_element_by_link_text( link )
		logger.passed("Element '%s' found by link" %  link )
		return "PASSED"
	except Exception as e:
		logger.error(str(e))
		logger.failed("[ASSERTION] Element link '%s' was not found on the page" % link )
		actionsOnFail.exitTestScriptGracefully( testData )
		return "FAILED"

## text present
def assertTextNotPresent(testData,text):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if text not in driver.find_element_by_css_selector("BODY").text:
			logger.passed("Text '%s' was not found on page"%text)
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Text '%s' was found on the page"%text)
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertTextPresent(testData,text):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if text in driver.find_element_by_css_selector("BODY").text:
			logger.passed("Text '%s' was found on page"%text)
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Text '%s' was not found on the page"%text)
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

## text
def assertTextByID(testData,elementID,text):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if text == driver.find_element_by_id(elementID).text:
			logger.passed("Text '%s' was found in element '%s'"%(text,elementID))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Text '%s' was not found in element '%s'"%(text,elementID))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotTextByID(testData,elementID,text):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if text != driver.find_element_by_id(elementID).text:
			logger.passed("Text '%s' was not found in element '%s'"%(text,elementID))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Text '%s' was found in element '%s'"%(text,elementID))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertTextByXPath(testData,xpath,text):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if text == driver.find_element_by_xpath(xpath).text:
			logger.passed("Text '%s' was found in xpath '%s'"%(text,xpath))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Text '%s' was not found in xpath '%s'"%(text,xpath))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotTextByXPath(testData,xpath,text):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if text != driver.find_element_by_xpath(xpath).text:
			logger.passed("Text '%s' was not found in xpath '%s'"%(text,xpath))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Text '%s' was found in xpath '%s'"%(text,xpath))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)
	
def assertTextByCSS(testData,css_selector,text):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if text == driver.find_element_by_css_selector(css_selector).text:
			logger.passed("Text '%s' was found in css_selector '%s'"%(text,css_selector))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Text '%s' was not found in css_selector '%s'"%(text,css_selector))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotTextByCSS(testData,css_selector,text):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if text != driver.find_element_by_css_selector(css_selector).text:
			logger.passed("Text '%s' was not found in css_selector '%s'"%(text,css_selector))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Text '%s' was found in css_selector '%s'"%(text,css_selector))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertTextByName( testData , name , text ):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if text == driver.find_element_by_name( name ).text:
			logger.passed("Text '%s' was found in element '%s'"%( text , name ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Text '%s' was not found in element '%s'"%( text , name ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotTextByName( testData , name , text ):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if text != driver.find_element_by_name( name ).text:
			logger.passed("Text '%s' was not found in element '%s'"%( text , name ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Text '%s' was found in element '%s'"%( text , name ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

## text by regex
def assertTextByXPathRegex( testData , xpath , regex ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_xpath( xpath )
	except Exception as e:
		logger.failed("Element xpath '%s' was not found on the page" % xpath )
		actionsOnFail.performActions(testData)
		return "FAILED"
	regexC = re.compile( regex , re.DOTALL )
	try:
		elementText = driver.find_element_by_xpath( xpath ).text
	except Exception as e:
		logger.error( str(e) )
		return "FAILED"
	try :
		regexC.findall( elementText )[0]
		logger.passed( "Text '%s' matched regex '%s'" % ( elementText , regex ))
		return "PASSED"
	except :
		logger.failed( "[ASSERTION] Text '%s' did NOT match regex '%s'" % ( elementText , regex ))
		actionsOnFail.exitTestScriptGracefully( testData )
		return "FAILED"

def assertTextByIDRegex( testData , elementID , regex ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_id( elementID )
	except Exception as e:
		logger.failed("Element ID '%s' was not found on the page" % elementID )
		actionsOnFail.performActions(testData)
		return "FAILED"
	regexC = re.compile( regex , re.DOTALL )
	try:
		elementText = driver.find_element_by_id( elementID ).text
	except Exception as e:
		logger.error( str(e) )
		return "FAILED"
	try :
		regexC.findall( elementText )[0]
		logger.passed( "Text '%s' matched regex '%s'" % ( elementText , regex ))
		return "PASSED"
	except :
		logger.failed( "[ASSERTION] Text '%s' did NOT match regex '%s'" % ( elementText , regex ))
		actionsOnFail.exitTestScriptGracefully( testData )
		return "FAILED"

def assertTextByCSSRegex( testData , css_selector , regex ):
	driver = testData['driver']
	logger = testData['logger']
	try: 
		driver.find_element_by_css_selector( css_selector )
	except Exception as e:
		logger.failed("Element CSS '%s' was not found on the page" % css_selector )
		actionsOnFail.performActions(testData)
		return "FAILED"
	regexC = re.compile( regex , re.DOTALL )
	try:
		elementText = driver.find_element_by_css_selector( css_selector ).text
	except Exception as e:
		logger.error( str(e) )
		return "FAILED"
	try :
		regexC.findall( elementText )[0]
		logger.passed( "Text '%s' matched regex '%s'" % ( elementText , regex ))
		return "PASSED"
	except :
		logger.failed( "[ASSERTION] Text '%s' did NOT match regex '%s'" % ( elementText , regex ))
		actionsOnFail.exitTestScriptGracefully( testData )
		return "FAILED"

## attribute
def assertAttributeByCSS( testData , css_selector , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if value == driver.find_element_by_css_selector( css_selector ).get_attribute( attribute ):
			logger.passed("Attribute '%s' was found in css_selector '%s', attribute '%s'"%( value , css_selector , attribute ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Attribute '%s' was not found in css_selector '%s', attribute '%s'"%( value , css_selector , attribute ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotAttributeByCSS( testData , css_selector , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if value != driver.find_element_by_css_selector(css_selector).get_attribute(attribute):
			logger.passed("Attribute '%s' was not found in css_selector '%s', attribute '%s'"%( value , css_selector , attribute))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Attribute '%s' was found in css_selector '%s', attribute '%s'"%( value , css_selector , attribute ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertAttributeByLink( testData , link , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		actualValue = driver.find_element_by_link_text( link ).get_attribute( attribute )
		if value == actualValue :
			logger.passed("Attribute '%s' was found in link '%s', attribute '%s'"%( value , link , attribute ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Attribute '%s' was not found in link '%s', attribute '%s', actual attribute was: '%s'"%( value , link , attribute , actualValue ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotAttributeByLink( testData , link , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if value != driver.find_element_by_link_text( link ).get_attribute(attribute):
			logger.passed("Attribute '%s' was not found in link '%s', attribute '%s'"%( value , link , attribute))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Attribute '%s' was found in link '%s', attribute '%s'"%( value , link , attribute ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertAttributeByXPath( testData , xpath , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if value == driver.find_element_by_xpath( xpath ).get_attribute( attribute ):
			logger.passed("Attribute '%s' was found in xpath '%s', attribute '%s'"%( value , xpath , attribute ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Attribute '%s' was not found in xpath '%s', attribute '%s'"%( value , xpath , attribute ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotAttributeByXPath( testData , xpath , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if value != driver.find_element_by_xpath( xpath ).get_attribute( attribute ):
			logger.passed("Attribute '%s' was not found in xpath '%s', attribute '%s'"%( value , xpath , attribute ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Attribute '%s' was found in xpath '%s', attribute '%s'"%( value , xpath , attribute ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertAttributeByID( testData , elementID , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if value == driver.find_element_by_id( elementID ).get_attribute( attribute ):
			logger.passed("Attribute '%s' was found in elementID '%s', attribute '%s'"%( value , elementID , attribute ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Attribute '%s' was not found in elementID '%s', attribute '%s'"%( value , elementID , attribute ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotAttributeByID( testData , elementID , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if value != driver.find_element_by_id( elementID ).get_attribute( attribute ):
			logger.passed("Attribute '%s' was not found in elementID '%s', attribute '%s'"%( value , elementID , attribute ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Attribute '%s' was found in elementID '%s', attribute '%s'"%( value , elementID , attribute ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertAttributeByName( testData , name , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if value == driver.find_element_by_name( name ).get_attribute( attribute ):
			logger.passed("Attribute '%s' was found in name '%s', attribute '%s'"%( value , name , attribute ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Attribute '%s' was not found in name '%s', attribute '%s'"%( value , name , attribute ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotAttributeByName( testData , name , attribute , value ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if value != driver.find_element_by_name( name ).get_attribute( attribute ):
			logger.passed("Attribute '%s' was not found in name '%s', attribute '%s'"%( value , name , attribute ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Attribute '%s' was found in name '%s', attribute '%s'"%( value , name , attribute ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

##checked
def assertCheckedByID( testData , elementID ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_id( elementID ).is_selected() == True :
			logger.passed("Element '%s' was checked" % ( elementID ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Element '%s' was not checked" % ( elementID ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotCheckedByID( testData , elementID ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_id( elementID ).is_selected() == False :
			logger.passed("Element '%s' was not checked" % ( elementID ))
			return "PASSED"
		else:
			logger.failed("Element '%s' was checked" % ( elementID ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertCheckedByXPath( testData , xpath ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_xpath( xpath ).is_selected() == True :
			logger.passed("xpath '%s' was checked" % ( xpath ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] xpath '%s' was not checked" % ( xpath ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotCheckedByXPath( testData , xpath ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_xpath( xpath ).is_selected() == False :
			logger.passed("xpath '%s' was not checked" % ( xpath ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] xpath '%s' was checked" % ( xpath ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertCheckedByCSS( testData , css_selector ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_css_selector( css_selector ).is_selected() == True :
			logger.passed("Element '%s' was checked" % ( css_selector ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Element '%s' was not checked" % ( css_selector ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotCheckedByCSS( testData , css_selector ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_css_selector( css_selector ).is_selected() == False :
			logger.passed("css_selector '%s' was not checked" % ( css_selector ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] css_selector '%s' was checked" % ( css_selector ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertCheckedByName( testData , name ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_name( name ).is_selected() == True :
			logger.passed("Element '%s' was checked" % ( name ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Element '%s' was not checked" % ( name ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotCheckedByName( testData , name ) :
	driver = testData['driver']
	logger = testData['logger']
	resultsPath = testData['RESULTS_PATH']
	try:
		if driver.find_element_by_name( name ).is_selected() == False :
			logger.passed("Element '%s' was not checked" % ( name ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Element '%s' was checked" % ( name ))
			actionsOnFail.exitTestScriptGracefully(logger,driver,resultsPath, testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

## title
def assertTitle(testData,text):
	driver = testData['driver']
	logger = testData['logger']
	try:
		if text == driver.title:
			logger.passed("Page title '%s' matched '%s'"%(driver.title,text ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Page title '%s' did not match '%s'"%(driver.title,text ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

## location
def assertLocation( testData , location ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if location in driver.current_url :
			logger.passed("Current location ('%s') is correct" % ( driver.current_url ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Current location ('%s') was not what was expected ('%s')" % ( driver.current_url , location ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotLocation( testData , location ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if location != driver.current_url :
			logger.passed("Current location ('%s') is correct" % ( driver.current_url ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Current location ('%s') was not what was expected, it matches '%s'" % ( driver.current_url , location ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

## visible
def assertVisibleByID( testData , elementID ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_id( elementID ).is_displayed() == True :
			logger.passed("Element '%s' was visible" % ( elementID ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Element '%s' was not visible" % ( elementID ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotVisibleByID( testData , elementID ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_id( elementID ).is_displayed() == False :
			logger.passed("Element '%s' was not visible" % ( elementID ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Element '%s' was visible" % ( elementID ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertVisibleByXPath( testData , xpath ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_xpath( xpath ).is_displayed() == True :
			logger.passed("xpath '%s' was visible" % ( xpath ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] xpath '%s' was not visible" % ( xpath ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotVisibleByXPath( testData , xpath ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_xpath( xpath ).is_displayed() == False :
			logger.passed("xpath '%s' was not visible" % ( xpath ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] xpath '%s' was visible" % ( xpath ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertVisibleByCSS( testData , css_selector ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_css_selector( css_selector ).is_displayed() == True :
			logger.passed("Element '%s' was visible" % ( css_selector ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Element '%s' was not visible" % ( css_selector ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotVisibleByCSS( testData , css_selector ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_css_selector( css_selector ).is_displayed() == False :
			logger.passed("css_selector '%s' was not visible" % ( css_selector ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] css_selector '%s' was visible" % ( css_selector ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertVisibleByName( testData , name ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_name( name ).is_displayed() == True :
			logger.passed("Element '%s' was visible" % ( name ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Element '%s' was not visible" % ( name ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)

def assertNotVisibleByName( testData , name ) :
	driver = testData['driver']
	logger = testData['logger']
	try:
		if driver.find_element_by_name( name ).is_displayed() == False :
			logger.passed("Element '%s' was not checked" % ( name ))
			return "PASSED"
		else:
			logger.failed("[ASSERTION] Element '%s' was visible" % ( name ))
			actionsOnFail.exitTestScriptGracefully(testData)
	except Exception as e:
		logger.error(str(e))
		actionsOnFail.exitTestScriptGracefully(testData)










