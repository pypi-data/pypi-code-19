"""
Created on Jul 18, 2017

@author: khoi.ngo

Class define constant used for core selenium project
"""

class Browser():
    firefox = "FIREFOX"
    ie = "INTERNET_EXPLORER"
    edge = "EDGE"
    safari = "SAFARI"
    chrome = "CHROME"

class LocatorType():
    id = "ID"
    name = "NAME"
    link_text = "LINK_TEXT"
    partial_link_text = "PARTIAL_LINK_TEXT"
    tag_name = "TAG_NAME"
    class_name = "CLASS_NAME"
    css = "CSS"
    xpath = "XPATH"

class Platform():
    windows = "WINDOWS"
    mac = "MAC"
    android = "ANDROID"
    ios = "IOS"
    linux = "LINUX"
    osx = "OSX"
