# error.py
#
#

""" BOTLIB Exceptions. """

import builtins

class Error(builtins.Exception):
    """ yooooo !!!. """
    pass

class EDEFAULT(Error):
    """ missing default value. """

class ENOWORKDIR(Error):
    """ a workdir is not provided. """
    pass

class ERSINGLENAME(Error):
    """ firs level directory names are reserved. """
    pass

class ETOPLEVELDIR(Error):
    """ Path is a toplevel directory and cannot be written to. """
    pass

class ENODEFAULT(Error):
    """ No default provided. """
    pass

class ENOBID(Error):
    """ no bot id available. """
    pass

class EDEFINE(Error):
    """ define error. """
    pass

class ENETWORK(Error):
    """ heerlijk de heden ten dage. """
    pass

class ENOTXT(Error):
    """ no text to parse. """
    pass

class ENOPATH(Error):
    """ there is not path available to save to disk. """ 
    pass

class ENODATA(Error):
    """ the objectect loaded from file has no data section. """ 
    pass

class ERE(Error):
    """ error in a regular expression. """

class ENOPREFIX(Error):
    """ first argument is not a directory in the workdir. """
    pass

class EBORDER(Error):
    """ program is reaching out of its cfgured workdir. """ 
    pass

class EDIR(Error):
    """ file is a directory error. """
    pass

class EWORKDIR(Error):
    """ workdir is not set or not reachable. """
    pass

class ERESUME(Error):
    """ An error occured during resume. """
    pass

class EREBOOT(Error):
    """ An error occured during reboot. """
    pass

class EPASSWORD(Error):
    """ wrong password provided. """
    pass

class ERESERVED(Error):
    """ a reserved word is used. """
    pass

class ELOAD(Error):
    """ loading of the objectect failed. """
    pass

class EFILENAME(Error):
    """ filename is not correct. """
    pass

class EISMETHOD(Error):
    """ Attribute is a method. """
    pass

class ENOMETHOD(Error):
    """ no method is provided. """
    pass

class ENODATE(Error):
    """ date cannot be determined. """
    pass

class ENOTIME(Error):
    """ no time can be detected. """
    pass

class ENODIR(Error):
    """ directory is not available. """
    pass

class EDISPATCHER(Error):
    """ dispatcher is missing. """
    pass

class EATTRIBUTE(Error):
    """ item is already an attribute. """
    pass

class ENOTSET(Error):
    """ variable is not set. """
    pass

class ESET(Error):
    """ Attribute is already set. """
    pass

class ESIGNATURE(Error):
    """ signature check failed. """
    pass

class ENOTIMPLEMENTED(Error):
    """ method or function is not implemented. """
    pass

class ENOJSON(Error):
    """ string cannot be _parsed as JSON. """
    pass

class EJSON(Error):
    """ A JSON compiling error occured. """
    pass

class EDISCONNECT(Error):
    """ server has disconnect. """
    pass

class ECONNECT(Error):
    """ connect error occured. """
    pass

class EFILE(Error):
    """ error reading the file. """
    pass

class EARGUMENT(Error):
    """ argument given results in an error. """
    pass

class ETYPE(Error):
    """ argument is of the wrong type. """
    pass

class EOWNER(Error):
    """ origin is not an owner. """
    pass

class EFUNC(Error):
    """ error occured during execution of the function. """
    pass

class ENOFUNC(Error):
    """ function is not provided. """
    pass

class EREGISTER(Error):
    """ error during registration, """
    pass

