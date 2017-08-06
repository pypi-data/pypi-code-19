
import re
import weakref
import boto3
import json
import os
import time
import datetime
from dateutil import tz

utc = tz.gettz('UTC')		# define utc



class SmartFileSystemObject(object):

  """SmartFileSystem provides unified object-oriented access to filesystems of various protocols.
  It draws a number of parallels to the Windows FileSystemObject.
  
  Methods:
    copyFile(source, dest, overwrite=True) 
                          - Copy file from one location to another.  (Create parent folders as required)
    deleteFile(url)       - Delete a specified file.
    fileExists(url)       - Return True if the specified file exists.
    folderExists(url)     - Return True if the specified folder exists.
    getFile(url)          - Return a SmartFile object.
    getFileMd5(url)       - Return file md5 checksum hash.
    getFileSecs(url)      - Return file media length in seconds  (only applies to media files).
    getFileSize(url)      - Return file size in bytes.
    getFileTimestamp(url) - Return file last modified timestamp.
    getFiles(folderUrl)   - Return a list of files (SmartFile objects) contained in the specified folder.
    getFolder(url)        - Return a SmartFolder object.
    getSubFolders(folderUrl) - Return a list of sub-folders (SmartFolder objects) contained in the specified folder.
    moveFile(source, dest, overwrite=True)
                          - Move file from one location to another.  (Create parent folders as required)
##    copyFolder(source, dest, overwrite=True) - Copy folder from one location to another.  (Create parent folders as required)
##    deleteFolder(url)       - Delete a specified folder including all files and sub-folders.
##    moveFolder(source, dest, overwrite=True) - Move file from one location to another.  (Create parent folders as required)
  
  Internal Instance Variables:
    s3                    - boto3 s3 resource object
    s3creds               - username/password for current s3 connection (if specified)
  
  Internal Methods:
    connectS3             - establish s3 connection (if required)
    validateUrl(url)      - Raise exception if url is invalid format
    splitUrl(url)         - Split url and return protocol,path (as tuple)
    splitS3Url(url)       - Split s3 format url and return protocol,bucket,key (as tuple)


  """
  
  # constructors & instance variables
  def __init__(self):
    self.s3 = None
    self.s3creds = ""

  # methods
  def copyFile(source, dest, overwrite=True):
    """Copy file from one location to another.  (Create parent folders as required)"""
    raise NotImplementedError("Not Implemented Yet")


  def deleteFile(url):
    """Delete a specified file."""
    raise NotImplementedError("Not Implemented Yet")


  def fileExists(url):
    """Return True if the specified file exists."""
    raise NotImplementedError("Not Implemented Yet")


  def folderExists(url):
    """Return True if the specified folder exists."""
    raise NotImplementedError("Not Implemented Yet")


  def getFile(url):
    """Return a SmartFile object."""
    raise NotImplementedError("Not Implemented Yet")


  def getFileMd5(url):
    """Return file md5 checksum hash."""
    raise NotImplementedError("Not Implemented Yet")


  def getFileSecs(url):
    """Return file media length in seconds  (only applies to media files)."""
    raise NotImplementedError("Not Implemented Yet")


  def getFileSize(url):
    """Return file size in bytes."""
    raise NotImplementedError("Not Implemented Yet")


  def getFileTimestamp(url):
    """Return file last modified timestamp."""
    raise NotImplementedError("Not Implemented Yet")


  def getFiles(folderUrl):
    """Return a list of files (SmartFile objects) contained in the specified folder."""
    raise NotImplementedError("Not Implemented Yet")


  def getFolder(url):
    """Return a SmartFolder object."""
    raise NotImplementedError("Not Implemented Yet")


  def getSubFolders(folderUrl):
    """Return a list of sub-folders (SmartFolder objects) contained in the specified folder."""
    raise NotImplementedError("Not Implemented Yet")


  def moveFile(source, dest, overwrite=True):
    """Move file from one location to another.  (Create parent folders as required)"""
    raise NotImplementedError("Not Implemented Yet")
  
  
  # internal methods
  def connectS3():
    if s3creds <> "":
      raise NotImplementedError("Specific s3 credentials not implemented yet")
    
    s3 = boto3.resource('s3')
    raise NotImplementedError("Not Implemented Yet")



class SmartBase(object):

  """SmartBase represents the base path used by SmartFile & SmartFolder classes.  
  
  SmartFile & SmartFolder classes provide a consistent, object-oriented means for accessing 
  files & folders accessible by a wide variety of protocols (ie: http/ftp/sftp/file/s3).
  These classes draw a number of parallels to the Windows "FileSystemObject" "File" and "Folder" objects.
  
  Class Attributes:
    _instances    - used for tracking all instances of this class
  
  Constructors:
    SmartBase("s3://mybucket/mybase/", ["mybase", "myusername", "mypassword"])

  Instance Variables:
    name          - used 
    fso           - SmartFileSystem object used for unified file operations.
    connectors    - list of SmartConnector objects
    url           - ie: "s3://mybucket/mybase/"     # standard format includes a trailing slash if not provided
  
  Properties:
    protocol      - ie: "s3"                        # can be "file", "s3", "ftp", "http", "sftp")
    path          - ie:      "mybucket/mybase/"     # for "file:///mybase/" would be absolute folder "/mybase/"
    s3bucket      - ie:      "mybucket"             # first part of basepath before first "/"   (only relavent if protocol - ie: 's3')
    s3path        - ie:               "mybase/"     # remainder of basepath after first "/"     (only relavent if protocol = 's3')
    rootFolder    - SmartFolder object for the root/base folder.

  Methods:
    getFolder(somepath)          - Return a SmartFolder object.  Accepts relative paths or urls.
    getFile(somepath)            - Return a SmartFile object.  Accepts relative paths or urls.
  
  Class Methods:
    getInstances()               - Return a list of SmartBase instances.  
    getNextDefaultInstanceName() - Return the next default instance name - ie: "base04" (assuming three defaults already exist).
    getInstance(name)            - Return the specified SmartBase instance (if it exists).
    instanceNameExists(name)     - Return True if the specified instance name exists.
  """

  # class attributes
  _instances = set()
  

  # constructors & instance variables
  def __init__(self, url, name=None, user=None, password=None):
    self.url = url
    self.connectors = []
    
    if name is None:
      name = SmartBase.getNextDefaultInstanceName()
    else:
      if SmartBase.instanceNameExists(name):
        raise Exception("SmartBase name '{}' already exists.".format(name))
    self.name = name
    
    self._instances.add(weakref.ref(self))


  # properties
  @property
  def url(self):
    return self._url
  

  @url.setter
  def url(self, value):
    # check for "protocol://path" format
    protocol,sep,path = value.partition("://")
    if (protocol == "") or (path == ""):
      raise Exception("Invalid url '{}' - expecting 'protocol://path'".format(value))
    
    # check that protocol has been implemented
    implemented_protocols = ["s3", "file", "ftp", "http"]
    if protocol not in implemented_protocols:
      raise NotImplementedError("The '{}' protocol has not been implemented yet.  (Implemented protocols are: {}://)".format(protocol, "://, ".join(implemented_protocols)))
    
    # standardise base urls with trailing slash
    self._url = value.strip("/") + "/"


  @property
  def protocol(self):  # = "s3"                        # can be "file", "s3", "ftp", "http", "sftp")
    protocol,sep,path = self.url.partition("://")
    return protocol


  @property
  def path(self):
    """Return 'mybucket/mybase/'.  For url='s3://mybucket/mybase/' """
    protocol,sep,path = self.url.partition("://")
    return path


  @property
  def s3bucket(self):
    """Return "mybucket".  For url='s3://mybucket/mybase/'.  (Only relavent if protocol = 's3') """
    if self.protocol <> "s3":
      raise Exception("SmartBase.s3bucket property is only valid for the s3:// protocol.")
    
    pathparts = self.path.split("/")
    return pathparts[0]
  
  
  @property
  def s3path(self):
    """Return "mybase/".  For url='s3://mybucket/mybase/'.  (Only relavent if protocol = 's3') """
    if self.protocol <> "s3":
      raise Exception("SmartBase.s3bucket property is only valid for the s3:// protocol.")
    
    pathparts = self.path.split("/")
    return "/".join(pathparts[1:])
  

  @property
  def rootFolder(self):
    """Return a SmartFolder object for the root/base folder."""
    return getFolder("/")


  # methods
  def getFolder(self, somepath):
    """Return a SmartFolder object.  Accepts relative paths or urls. """
    return SmartFolder(self, somepath)


  def getFile(self, somepath):
    """Return a SmartFile object.  Accepts relative paths or urls. """
    return SmartFile(self, somepath)
  

  # class methods
  @classmethod
  def getInstances(cls):    # http://effbot.org/pyfaq/how-do-i-get-a-list-of-all-instances-of-a-given-class.htm
    """Return a list of SmartBase instances."""
    dead = set()
    for ref in cls._instances:
      obj = ref()
      if obj is not None:
        yield obj
      else:
        dead.add(ref)
    cls._instances -= dead  
  

  @classmethod
  def getNextDefaultInstanceName(cls):
    """Return the next default instance name - ie: "base04" (assuming three defaults already exist)."""

    # find the largest existing default base - ie: "baseXX"
    lastDefaultInstanceNum = 0
    for b in SmartBase.getInstances():
      if b.name.startswith("base") and (len(b.name) == 6):
        n = b.name[-2:]
        if n.isdigit:
          n = int(n)
          lastDefaultInstanceNum = max(lastDefaultInstanceNum, n)

    # return the next default instance name
    return "base{:02}".format(lastDefaultInstanceNum+1)
    

  @classmethod
  def getInstance(cls, name):
    """Return the specified SmartBase instance (if it exists)."""

    for b in SmartBase.getInstances():
      if b.name == name:
        return b

    return None
    

  @classmethod
  def instanceNameExists(cls, name):
    """Return True if the specified instance name exists."""

    for b in SmartBase.getInstances():
      if b.name == name:
        return True

    return False
    





class SmartPath(object):

  """SmartPath is the base class for SmartFile & SmartFolder classes.
  
  SmartFile & SmartFolder classes provide a consistent, object-oriented means for accessing 
  files & folders accessible by a wide variety of protocols (ie: http/ftp/sftp/file/s3).
  These classes draw a number of parallels to the Windows "FileSystemObject" "File" and "Folder" objects.
  
  Constructors:
    Minimal forms:
      SmartPath(musicbase, "folder1/sub2/my file.mp3")                       # base+path form.
      SmartPath(musicbase, "file:///home/myuser/folder1/sub2/my file.mp3")   # base+url form.   An exception is thrown if specified url doesn't match the base url.
      SmartPath("music:folder1/sub2/my file.mp3")                            # smartpath form.  An exception is thrown if basename doesn't match an existing SmartBase name.
      SmartPath("file:///home/myuser/folder1/sub2/my file.mp3")              # url form.        Will try to match existing bases, but will create a new base if none found.

    Preferred "keyword argument" forms:  (provides greater clarity)
      SmartPath(base=musicbase, path="folder1/sub2/my file.mp3")
      SmartPath(base=musicbase, url="file:///home/myuser/folder1/sub2/my file.mp3")
      SmartPath(base=musicbase, url="file:///home/myuser/folder1/sub2/my file.mp3")
      SmartPath(smartpath="music:folder1/sub2/my file.mp3")
      SmartPath(url="file:///home/myuser/folder1/sub2/my file.mp3")
  
  Instance Variables:
    base          - the SmartBase object.  In examples below, base.url is:
                        "file:///home/myuser/"
    _path         - ie:                     "folder1/sub2/my file.mp3"     # path relative to the base
  
  Properties:
    path          - ie:                     "folder1/sub2/my file.mp3"     # path relative to the base
    name          - ie:                                  "my file.mp3"
    fullPath      - ie:        "/home/myuser/folder1/sub2/my file.mp3"     # full path, including the base path, excluding the protocol
    url           - ie: "file:///home/myuser/folder1/sub2/my file.mp3"
    urlQuoted     - ie: "file:///home/myuser/folder1/sub2/my%20file.mp3"
    s3key         - ie:                     "folder1/sub2/my file.mp3"     # AWS S3 key name is the full path excluding the bucket name (only relavent if protocol = 's3')  (example assumes url="s3://cdn.mydomain.com/folder1/sub2/my file.mp3")
    exists        - True/False
    parentFolder  - SmartFolder object for parent                                       # won't go past the base path
    
  """

  # constructors & instance variables
  def __init__(self, arg1=None, arg2=None, base=None, path=None, smartpath=None, url=None):
    """
    Minimal forms:
      SmartPath(musicbase, "folder1/sub2/my file.mp3")                       # base+path form.
      SmartPath(musicbase, "file:///home/myuser/folder1/sub2/my file.mp3")   # base+url form.   An exception is thrown if specified url doesn't match the base url.
      SmartPath("music:folder1/sub2/my file.mp3")                            # smartpath form.  An exception is thrown if basename doesn't match an existing SmartBase name.
      SmartPath("file:///home/myuser/folder1/sub2/my file.mp3")              # url form.        Will try to match existing bases, but will create a new base if none found.

    Preferred "keyword argument" forms:  (provides greater clarity)
      SmartPath(base=musicbase, path="folder1/sub2/my file.mp3")
      SmartPath(base=musicbase, url="file:///home/myuser/folder1/sub2/my file.mp3")
      SmartPath(base=musicbase, url="file:///home/myuser/folder1/sub2/my file.mp3")
      SmartPath(smartpath="music:folder1/sub2/my file.mp3")
      SmartPath(url="file:///home/myuser/folder1/sub2/my file.mp3")
    """
    
    positionalArgsUsed = (arg1 is not None) or (arg2 is not None)
    keywordArgsUsed = (base is not None) or (path is not None) or (smartpath is not None) or (url is not None)
    if positionalArgsUsed and keywordArgsUsed:
      raise Exception("Error: Can't mix positional and keyword arguments in SmartPath constructor.")
    
    # decode positional arguments
    if positionalArgsUsed:
      # arg1 is not optional
      if arg1 is None:
        raise Exception("Error: arg1 is not optional if positional arguments are used in SmartPath constructor.")
      
      # decode based on arg2's existence
      if arg2 is None:
        somepath = arg1
      else:
        base = arg1
        somepath = arg2
      
      # determine whether somepath is a url, smartpath, or path
      if "://" in somepath:
        url = somepath
      elif ":" in somepath:
        smartpath = somepath
      else:
        path = somepath
    
    # if specified, base must be a SmartBase object
    if base is not None:
      if not isinstance(base, SmartBase):
        raise Exception("Error: base must be a SmartBase object.")
    
    # initialise base+path form:
    if ((base is not None) and (path is not None))  and  ((smartpath is None) and (url is None)):
      self.base = base
      self.path = path
      return

    # initialise smartpath form:
    if ((smartpath is not None))  and  ((base is None) and (path is None) and (url is None)):
      basename,sep,path = smartpath.partition(":")
      base = SmartBase.getInstance(basename)
      if base is None:
        raise Exception("Error: The '{}' SmartBase was not found in SmartPath('{}') constructor".format(basename, smartpath))
      
      self.base = base
      self.path = path
      return
    
    # initialise base+url form:
    if ((base is not None) and (url is not None))  and  ((path is None) and (smartpath is None)):
      # ensure the url matches the base
      if not url.startswith(base.url.strip("/")):
        raise Exception("Error: The '{}' url does not match the SmartBase '{}' url.".format(url, base.url))
      
      path = url[len(base.url):]
      self.base = base
      self.path = path
      return
    
    # initialise url form:
    if ((url is not None))  and  ((base is None) and (path is None) and (smartpath is None)):
      # try to find a matching base
      base = None
      for b in SmartBase.getInstances():
        if url.startswith(b.url):
          base = b
          break
      
      # create a new base if not found
      if base is None:
        raise NotImplementedError("The '{}' url did not match any existing SmartBases, and auto-creation of SmartBases is not yet implemented - mainly due to difficulty in guessing the most appropriate base to use.".format(url))
      
      path = url[len(base.url):]
      self.base = base
      self.path = path
      return
    
    raise Exception("Error: Valid SmartPath constructor forms are: base+path, base+url, smartpath, and url.  You tried to specify some other combination of arguments.")
    

  # properties
  @property
  def path(self):
    return self._path
  

  @path.setter
  def path(self, value):
    # special case for root / base path
    if value == "":
      value = "/"
    self._path = value
  
  
  @property
  def name(self):
    """Return name of Folder or File without the path.  Return 'my file.mp3'.  For path='folder1/sub2/my file.mp3'. """
    pathparts = self.path.strip("/").split("/")
    return pathparts[-1]
  

  @name.setter
  def name(self, value):
    raise NotImplementedError("Not yet implemented - unsure whether to use for renaming or referencing a different object")
  
  
  @property
  def fullPath(self):
    """Return the full path, including the base path, excluding the protocol.  
    Return '/home/myuser/folder1/sub2/my file.mp3'.  For path='folder1/sub2/my file.mp3' (url='file:///home/myuser/folder1/sub2/my file.mp3'). 
    """
    protocol,sep,path = self.url.partition("://")
    return path
  
  
  @property
  def url(self):
    """Return 'file:///home/myuser/folder1/sub2/my file.mp3'.  For path='folder1/sub2/my file.mp3' (and base.url='file:///home/myuser/'). """
    return self.base.url + self.path.lstrip("/")
  
  
  @property
  def urlQuoted(self):
    """Return 'file:///home/myuser/folder1/sub2/my%20file.mp3'.  For path='folder1/sub2/my file.mp3' (and base.url='file:///home/myuser/'). """
    import urllib2
    protocol,sep,path = self.url.partition("://")
    return protocol + "://" + urllib2.quote(path)
  
  
  @property
  def s3key(self):
    """Return 'folder1/sub2/my file.mp3'.  For url='s3://cdn.mydomain.com/folder1/sub2/my file.mp3'.  (Only relavent if protocol = 's3'.) """
    return self.base.s3path + self.path.lstrip("/")
  
  
#  @property
#  def exists(self):
#    """Return True if the object exists. """
#    # not implemented in base class, but message is generic
#    raise NotImplementedError("{}.exists not implemented.".format(type(self).__name__))
#  
#  
  @property
  def exists(self):
    """Return True if the object exists. """
    for connector in self.base.connectors:
      try:
        return connector.exists(self)
      except NotImplementedError:
        pass
    raise NotImplementedError("No connectors found to check existence of '{}'.".format(self.url))
  
  
  @property
  def parentFolder(self):
    """SmartFolder object for parent.  (Won't go past the base path). """
    pathparts = self.path.strip("/").split("/")
    parentpath = "/".join(pathparts[:-1])
    return SmartFolder(self.base, parentpath)
  


class SmartFile(SmartPath):

  """SmartFile & SmartFolder classes provide a consistent, object-oriented means for accessing 
  files & folders accessible by a wide variety of protocols (ie: http/ftp/sftp/file/s3).
  These classes draw a number of parallels to the Windows "FileSystemObject" "File" and "Folder" objects.
  
  Constructors:
    (See SmartPath)
  
  Derived Instance Variables:  (from SmartPath)
    base, _path
  
  Derived Properties:          (from SmartPath)
    path, name, fullPath, url, exists, parentFolder
  
  New Instance Variables:
    attribs     - cached attributes obtained from SmartConnectors
  
  New Properties:
    size      - size in bytes
    md5       - md5 checksum hash
    secs      - media length in seconds  (only applies to media files)
    timestamp - last modified timestamp  (datetime object)
  
  Methods:
    copy(destSmartFile, [overwrite=False])  - Copy the file to the specified destination.
    move(destSmartFile, [overwrite=False])  - Move the file to the specified destination.
    delete()                                - Delete the file.
    read([size])                            - Read the file contents.  (Optional argument specifies the maximum size that will be read)
    write(contents)                         - Write contents to the file.  (Overwriting file if it exists)
    append(contents)                        - Append contents to the file.
    open([options])                         - 'Open' the file, and return an iterable 'file'-type object.
    __getattr__(attribName)                 - Return extra attributes obtained from SmartConnectors.
    updateAttributes(attribs, notify=True)  - Update internal attribute data and optionally notify LIVECACHE connectors.  
  """
  
  
  # constructors & instance variables
  def __init__(self, arg1=None, arg2=None, base=None, path=None, smartpath=None, url=None):
    # use parent constructor
    super(SmartFile,self).__init__(arg1, arg2, base, path, smartpath, url)
    
    # initiliase the attribs dictionary
    self.attribs = {}
  
  
  # properties
  
  
  # methods
  def copy(self, destSmartFile, overwrite=False):
    """ Copy the file to the specified destination. """
    # confirm source exists
    if not self.exists:
      raise Exception("Copy cancelled.  (Source does not exist '{}')".format(self.url))
    
    # confirm destination exists/overwrite
    if not overwrite:                  # check if overwrite prohibited first - since exists() method is slower
      if destSmartFile.exists:
        raise Exception("Copy cancelled.  (Destination already exists and overwrite=False for '{}')".format(destSmartFile.url))
    
    # use direct-copy if possible
    if self.base.protocol == destSmartFile.base.protocol:
      for connector in self.base.connectors:
        try:
          connector.directCopyFile(self, destSmartFile)
          return  # copied successfully
        except NotImplementedError:
          pass
    
    # use direct-download if appropriate
    if (self.base.protocol <> "file") and (destSmartFile.base.protocol == "file"):
      for connector in self.base.connectors:
        try:
          connector.downloadFile(self, destSmartFile)
          return  # copied successfully
        except NotImplementedError:
          pass
        raise NotImplementedError("No connectors found to download file from '{}'.".format(self.url))
    
    # use direct-upload if appropriate
    if (self.base.protocol == "file") and (destSmartFile.base.protocol <> "file"):
      for connector in destSmartFile.base.connectors:
        try:
          connector.uploadFile(self, destSmartFile)
          return  # copied successfully
        except NotImplementedError:
          pass
        raise NotImplementedError("No connectors found to upload file to '{}'.".format(destSmartFile.url))
    
    # use copy via temp-file as a last resort
    tempSmartFile = GetSmartTempFile()
    # download to temp-file
    for connector in self.base.connectors:
      try:
        connector.downloadFile(self, tempSmartFile)
        break  # copied successfully
      except NotImplementedError:
        pass
      except:
        if tempSmartFile.exists:
          tempSmartFile.delete()  # delete the temp-file (ie: on partial download / uncaught error)
        raise                     # re-raise the exception
      raise NotImplementedError("No connectors found to download TEMP file from '{}'.".format(self.url))
    # upload from temp-file
    for connector in destSmartFile.base.connectors:
      try:
        connector.uploadFile(tempSmartFile, destSmartFile)
        return  # copied successfully
      except NotImplementedError:
        pass
      finally:
        tempSmartFile.delete()  # delete the temp-file (always)
      raise NotImplementedError("No connectors found to upload TEMP file to '{}'.".format(destSmartFile.url))
    
  
  def move(self, destSmartFile, overwrite=False):
    """ Move the file to the specified destination. 
    Note: Current implementation uses copy+delete.  May want to add SmartConnector methods for direct move at a later date?
    """
    # move using copy+delete 
    self.copy(destSmartFile, overwrite)
    if destSmartFile.exists:
      self.delete()
  
    
  def delete(self):
    """ Delete the file. """
    for connector in self.base.connectors:
      try:
        connector.deleteFile(self)
        return  # success
      except NotImplementedError:
        pass
    raise NotImplementedError("No connectors found to delete '{}'.".format(self.url))
  
  
  def read(self, size=-1):
    """ Read the file contents.  (Optional argument specifies the maximum size that will be read) """
    for connector in self.base.connectors:
      try:
        return connector.readFile(self, size)  # success
      except NotImplementedError:
        pass
    raise NotImplementedError("No connectors found to read '{}'.".format(self.url))


  def write(self, contents):
    """ Write contents to the file.  (Overwriting file if it exists) """
    for connector in self.base.connectors:
      try:
        connector.writeFile(self, contents)
        return  # success
      except NotImplementedError:
        pass
    raise NotImplementedError("No connectors found to write '{}'.".format(self.url))


  def append(self, contents):
    """ Append contents to the file. """
    for connector in self.base.connectors:
      try:
        connector.appendFile(self, contents)
        return  # success
      except NotImplementedError:
        pass
    raise NotImplementedError("No connectors found to append '{}'.".format(self.url))


  def open(self, options=None):
    """ 'Open' the file, and return an iterable 'file'-type object. """
    for connector in self.base.connectors:
      try:
        return connector.openFile(self, options)  # success
      except NotImplementedError:
        pass
    raise NotImplementedError("No connectors found to open '{}'.".format(self.url))



  def __getattr__(self, attribName):
    """Return extra attributes obtained from SmartConnectors."""
    # return cached attribute if already available
    if attribName in self.attribs:
      return self.attribs[attribName]
      
    # lookup attribute using connectors   (assumes they are "appropriately" organised)
    for c in self.base.connectors:
      result = c.getAttribute(self, attribName)  # valid result is a dictionary containing the requested (and other optional) attributes
      try:
        self.updateAttributes(result)
        return self.attribs[attribName]
      except KeyError:
        pass    # attribute not returned by this connector - try next one
    
    # not found
    raise NotImplementedError("The SmartFile.{} attribute has not been implemented by any available connector for '{}'.".format(attribName, self.url))
  
  
  def updateAttributes(self, attribs, notify=True):
    """Update internal attribute data and optionally notify LIVECACHE connectors.  
    This is called by SmartFile.__getattr__() and SmartFolder.files whenever connectors return new attribute data.
    Attribs should be a dictionary of attribute name/value pairs.
    """
    # real updates exist?
    if attribs is None:
      return
      
    # update internal attribute data
    for attribName,attribValue in attribs.iteritems():
        self.attribs[attribName] = attribValue
    
    # notify all LIVECACHE connectors
    if notify:
      for connector in self.base.connectors:
        if connector.type == ConnTypes.LIVECACHE:
          connector.notifyAttributes(self, attribs)
    



class SmartFolder(SmartPath):

  """SmartFile & SmartFolder classes provide a consistent, object-oriented means for accessing 
  files & folders accessible by a wide variety of protocols (ie: http/ftp/sftp/file/s3).
  These classes draw a number of parallels to the Windows "FileSystemObject" "File" and "Folder" objects.
  
  Constructors:
    (See SmartPath)
  
  Derived Instance Variables:  (from SmartPath)
    base, _path
  
  New Instance Variables:
    _files, _filenames      - List of all files in this SmartFolder (SmartFile objects and names respectively)
    _subFolders, _subFoldernames - List of all subfolders in this SmartFolder (SmartFile objects and names respectively)
  
  Derived Properties:          (from SmartPath)
    path, name, fullPath, url, exists, parentFolder
  
  New Properties:
    path                    - (OVERRIDDEN) Adds a trailing slash for folder name consistency.
    files                   - Return list of SmartFiles for all files in this SmartFolder.
    subFolders              - Return list of SmartFolders for all subfolders in this SmartFolder.
  
#    filesRecursive          - list of all files in SmartFolder and all subFolders
#    filesMatching(filespec) - list of files in SmartFolder that match filespec
#    filesMatchingRecursive(filespec) - list of files in SmartFolder and al subFolders that match filespec
  
  New Methods:
    fileExists(name)        - Return true if the file exists.  (Using cached _filenames list)
    folderExists(name)      - Return true if the folder exists.  (Using cached _foldernames list)
    _getFiles(self)         - Internal method - loads _files & _filenames using (& notifying) connectors.
    _getFolders(self)       - Internal method - loads _folders & _foldernames using (& notifying) connectors.
    
  """
  
  # properties
  @SmartPath.path.setter
  def path(self, value):
    """ (OVERRIDDEN) Adds a trailing slash for folder name consistency. """
    # standardise all folder paths with trailing slash
    self._path = value.strip("/") + "/"
    # side-note, if we wanted to call our inherited setter we would use: SmartPath.path.fset(self, newvalue)
  
  
  @property
  def files(self):
    """ Return list of SmartFiles for all files in this SmartFolder. """
    # Load files if necessary
    if getattr(self, "_files", None) is None:
      self._getFiles()
    
    # return the files list
    return self._files
    
  
  @property
  def subFolders(self):
    """ Return list of SmartFolders for all subfolders in this SmartFolder. """
    # Load subFolders if necessary
    if getattr(self, "_subFolders", None) is None:
      self._getSubFolders()
    
    # return the subFolders list
    return self._subFolders
    
  
  # methods
  def fileExists(self, name):
    """ Return true if the file exists.  (Using cached _filenames list) """
    # Load filenames if necessary
    if getattr(self, "_filenames", None) is None:
      self._getFiles()
    
    # return true if file exists
    return name in self._filenames
  
  
  def folderExists(self, name):
    """ Return true if the folder exists.  (Using cached _foldernames list) """
    # Load subFoldernames if necessary
    if getattr(self, "_subFoldernames", None) is None:
      self._getSubFolders()
    
    # return true if sub-folder exists
    return name in self._subFoldernames
  
  
  def _getFiles(self):
    """ Internal method - load _files & _filenames using (& notifying) connectors. """
    # lookup files list using available connectors   (assumes they are "appropriately" organised)
    files = None
    for connector in self.base.connectors:
      files = connector.getFiles(self)
      if isinstance(files,dict):
        break
    
    # confirm that valid list was returned
    if not isinstance(files,dict):
      raise NotImplementedError("No connectors found to list files for '{}'.".format(self.url))
    
    # create the SmartFiles list
    self._files = []
    self._filenames = []
    for fname,fattribs in sorted(files.iteritems()):
      path = (self.path + fname).lstrip('/')    # construct path from self and fname - left-strip '/' required for root folders
      f = SmartFile(base=self.base, path=path)
      f.updateAttributes(fattribs, False)
      self._files.append(f)
      self._filenames.append(fname)
    
    # notify all LIVECACHE connectors
    for connector in self.base.connectors:
      if connector.type == ConnTypes.LIVECACHE:
        connector.notifyFiles(self, files)
  
  
  def _getSubFolders(self):
    """ Internal method - load _folders & _foldernames using (& notifying) connectors. """
    # lookup subFolders list using available connectors   (assumes they are "appropriately" organised)
    subFolders = None
    for connector in self.base.connectors:
      subFolders = connector.getSubFolders(self)
      if isinstance(subFolders,dict):
        break
    
    # confirm that valid list was returned
    if not isinstance(subFolders,dict):
      raise NotImplementedError("No connectors found to list sub-folders for '{}'.".format(self.url))
    
    # create the SmartFolders list
    self._subFolders = []
    self._subFoldernames = []
    for fldname,unused in sorted(subFolders.iteritems()):
      path = (self.path + fldname).lstrip('/')    # construct path from self and fldname - left-strip '/' required for root folders
      fld = SmartFolder(base=self.base, path=path)
      self._subFolders.append(fld)
      self._subFoldernames.append(fldname)
    
    # notify all LIVECACHE connectors
    for connector in self.base.connectors:
      if connector.type == ConnTypes.LIVECACHE:
        connector.notifySubFolders(self, subFolders)
  
  


# Flattens paths using double-underscores - ie: pathFlatten("my/path/file.txt") --> "my__path__file.txt"
def pathFlatten(path):
  return path.replace('/', '__')

# Un-flattens paths containing double-underscores - ie: pathUnflatten("my__path__file.txt") --> "my/path/file.txt"
def pathUnflatten(path):
  return path.replace('__', '/')

# Returns a file's extension.  (Correctly handles files without extensions and names leading dots like '.htaccess')
def pathExtension(path):
  pathparts = path.split("/")
  nameparts = pathparts[-1].split(".")
  if (len(nameparts) > 1) and (len(nameparts[0]) > 0):
    return nameparts[-1]
  else:
    return ""

# Returns a pathname without it's extension.  (Correctly handles files without extensions and names leading dots like '.htaccess')
def pathWithoutExtension(path):
  pathparts = path.split("/")
  nameparts = pathparts[-1].split(".")
  if (len(nameparts) > 1) and (len(nameparts[0]) > 0):
    del nameparts[-1]
  pathparts[-1] = ".".join(nameparts)
  return "/".join(pathparts)

# Returns a pathname, replacing the extension as specified
def pathReplaceExtension(path, newExtension):
  newExtension = newExtension.strip(".")        # standardise extension format without the leading dot
  return pathWithoutExtension(path) + "." + newExtension





class ConnTiers:
  """ Enumeration of SmartConnector Speed Tiers """
  MEMORY = 0         # In-memory
  LOCAL = 1          # Direct local-operating-system information
  LOCALDECODE = 2    # Decoded from local information (ie: local xml file)
  LAN = 3            # Local area network
  WAN = 4            # From the internet
  CALC = 5           # Calculation based on local file - ie: file MD5 hash, ID3 tags, etc
  COPYCALC = 6       # Same as CALC, but file has to be copied/downloaded locally before calc can be performed.
  UNKNOWN = 7        # Unknown / undefined
  all = range(UNKNOWN)  # List of all SmartConnector speed tiers - used for iteration.



class ConnTypes:
  """ Enumeration of SmartConnector Types """
  AUTHORITATIVE = 1  # Original, authoritative information about the underlying filesystem.
  LIVECACHE = 2      # Cached information about the filesystem - updateable.
  DEADCACHE = 3      # Cached information about the filesystem - read-only.



class SmartConnector(object):

  """The SmartConnector class is a base class.  Connector classes derived from this class provide the 
  means of querying different filesystems (with different protocols).
  Connectors are called to enumerate filesystems, and to query their attributes.
  Connectors are instantiatted by ???, and are added to smartbase objects to allow them to access
  
  Child classes will contain a statement of what they support - ie: 
  SUPPORTS:  lists = [files,folders],  attributes = [size,timestamp],  optional attributes = [md5]
  
  # Instance Variables:
  protocol             - SmartConnector supported protocol(s)
  tier                 - SmartConnector speed tier - as defined in the ConnTiers 'enumeration' class
  type                 - SmartConnector type - as defined in the ConnTypes 'enumeration' class
  
  # Methods:
  exists(smartPath)                - Query connector if the specified SmartFile/SmartFolder exists
  getFiles(smartFolder)            - Query connector for list of all files in the specified SmartFolder
  getSubFolders(smartFolder)       - Query connector for list of all sub-folders in the specified SmartFolder
  getAttribute(smartFile, attrib)  - Query connector for the specified SmartFile attribute
  notifyFiles(smartFolder, data)   - Notify LIVECACHE connector of updated files list data.
  notifySubFolders(smartFolder, data) - Notify LIVECACHE connector of updated folders list data.
  notifyAttributes(smartFile, data)- Notify LIVECACHE connector of updated file attribute data.
  protocolMatches(smartPath)       - Return True if the specified SmartPath's protocol is supported.
  protocolValidate(smartPath)      - Raise exception if the specified SmartPath's protocol is not supported.
  
  directCopyFile(sourceSmartFile, destSmartFile) - Perform a direct-copy of the file if possible.
  downloadFile(remoteSmartFile, localSmartFile)  - Download the specified remote file.
  uploadFile(localSmartFile, remoteSmartFile)    - Upload the specified remote file.
  deleteFile(smartFile)                          - Delete the specified file.
  readFile(smartFile, [size])                    - Read the specified file's contents.  (Optional argument specifies the maximum size that will be read)
  writeFile(smartFile, contents)                 - Write contents to the specified file.  (Overwriting file if it exists)
  appendFile(smartFile, contents)                - Append contents to the specified file.
  openFile(smartFile, [options])                 - 'Open' the specified file, and return an iterable 'file'-type object.
  
  """
  
  # constructors & instance variables
  def __init__(self):
    self.protocol = ""
    self.tier = ConnTiers.UNKNOWN        # Default - will be overridden by chid classes.
    self.type = ConnTypes.AUTHORITATIVE  # Default - will be overridden by chid classes.
  
  # methods
  def exists(self, smartPath):
    """ Query connector if the specified SmartFile/SmartFolder exists 
       - Unlike other methods which rely on memory caching, this method should re-query the underlying filesystem wherever possible.
    """
    return False                         # Nothing supported in Base class.


  def getFiles(self, smartFolder):
    """Query connector for list of all files in the specified SmartFolder 
       - Connectors return None if the operation is not supported or the information is not obtainable.
       - Connectors return a list of names, as keys of a dictionary object.
       - For non-AUTHORITATIVE connectors, the dictionary values should be set to 'None'
       - For AUTHORITATIVE connectors, the dictionary values may contain sub-dictionaries of additional 
         child attributes that inherently became available as a result of enumerating the contents of 
         the folder.  (ie: directory listings usually return file sizes and timestamps)
       - Results from AUTHORITATIVE connectors are then published to all LIVECACHE connectors.
    """
    return None                          # Nothing supported in Base class.


  def getSubFolders(self, smartFolder):
    """ Query connector for list of all sub-folders in the specified SmartFolder 
       - Connectors return None if the operation is not supported or the information is not obtainable.
       - Connectors return a list of names, as keys of a dictionary object.   NAMES SHOULD HAVE TRAILING SLASHES.
       - Dictionary keys are used only for compatibility with the getFiles function.  Dictionary values should always be set to 'None'
       - Results from AUTHORITATIVE connectors are then published to all LIVECACHE connectors.
    """
    return None                          # Nothing supported in Base class.


  def getAttribute(self, smartFile, attrib):
    """ Query connector for the specified SmartFile attribute 
       - Connectors return None if the operation is not supported or the information is not obtainable.
       - Connectors return a dictionary object of attributes and values.
       - For non-AUTHORITATIVE connectors, the only attribute/value pair returned should be one requested.
       - For AUTHORITATIVE connectors, additional attribute/value pairs may be returned for attributes 
         that inherently became available as a result of querying the requested attribute.  (ie: file 
         size and timestamp may become simultaneously available.)
       - Results from AUTHORITATIVE connectors are then published to all LIVECACHE connectors.
       - Connectors may (carefully) query other attributes from the calling SmartFile that are needed to 
         validate their own data - taking care to avoid recursion.  (ie: cached md5 values may need to 
         be matched against actual size and timestamp data to ensure validity).
    """
    return None                          # Nothing supported in Base class.
  
  
  def notifyFiles(self, smartFolder, data):
    """ Notify LIVECACHE connector of updated files list data. """
    pass                                   # No updates in Base class.
  
  
  def notifySubFolders(self, smartFolder, data):
    """ Notify LIVECACHE connector of updated folders list data. """
    pass                                   # No updates in Base class.
  
  
  def notifyAttributes(self, smartFile, data):
    """ Notify LIVECACHE connector of updated file attribute data. """
    pass                                   # No updates in Base class.
  
  
  def protocolMatches(self, smartPath):
    """ Return True if the specified SmartPath's protocol is supported. """
    return smartPath.base.protocol in self.protocol
  
  
  def protocolValidate(self, smartPath):
    """Raise exception if the specified SmartPath's protocol is not supported. """
    if not self.protocolMatches(smartPath):
      raise Exception("The '{}' protocol is not supported by the '{}' SmartConnector ({})".format(self.protocol, smartPath.base.protocol, smartPath.url))
  
  
  def directCopyFile(self, sourceSmartFile, destSmartFile, overwrite=False):
    """ Perform a direct-copy of the file if possible. """
    raise NotImplementedError("directCopyFile() not implemented in {} class".format(type(self).__name__))
  
  
  def downloadFile(self, remoteSmartFile, localSmartFile, overwrite=False):
    """ Download the specified remote file. """
    raise NotImplementedError("downloadFile() not implemented in {} class".format(type(self).__name__))
  
  
  def uploadFile(self, localSmartFile, remoteSmartFile, overwrite=False):
    """ Upload the specified remote file. """
    raise NotImplementedError("uploadFile() not implemented in {} class".format(type(self).__name__))
  
  
  def deleteFile(self, smartFile):
    """ Delete the specified file. """
    raise NotImplementedError("deleteFile() not implemented in {} class".format(type(self).__name__))
    
    
  def readFile(self, smartFile, size=-1):
    """ Read the specified file's contents.  (Optional argument specifies the maximum size that will be read) """
    raise NotImplementedError("readFile() not implemented in {} class".format(type(self).__name__))
  
  
  def writeFile(self, smartFile, contents):
    """ Write contents to the specified file.  (Overwriting file if it exists) """
    raise NotImplementedError("writeFile() not implemented in {} class".format(type(self).__name__))
  
  
  def appendFile(self, smartFile, contents):
    """ Append contents to the specified file. """
    raise NotImplementedError("appendFile() not implemented in {} class".format(type(self).__name__))
  
  
  def openFile(self, smartFile, options=None):
    """ 'Open' the specified file, and return an iterable 'file'-type object. """
    raise NotImplementedError("openFile() not implemented in {} class".format(type(self).__name__))
  








class LocalFileSystemConnector(SmartConnector):

  """The LocalFileSystemConnector class is a connector for a local file system.
  
  PROTOCOL:    file://
  SUPPORTS:    lists = [files,folders],  attributes = [size,timestamp],  optional attributes = []
  SPEED TIER:  LOCAL
  TYPE:        AUTHORITATIVE
  NOTES:       Folder list returns size+timestamp attributes for child files.

  """
  
  # constructors & instance variables
  def __init__(self):
    self.protocol = "file"
    self.tier = ConnTiers.LOCAL
    self.type = ConnTypes.AUTHORITATIVE
  
  
  # methods
  def getFiles(self, smartFolder):
    self.protocolValidate(smartFolder)    # raise exception if protocol is not valid
    
    # get list of all files and folders
    path = smartFolder.fullPath
    names = os.listdir(path)
    
    # filter files and return
    files = {}
    for name in names:
       if os.path.isfile(os.path.join(path, name)):
         files[name] = None
    return files
  
  
  def getSubFolders(self, smartFolder):
    self.protocolValidate(smartFolder)    # raise exception if protocol is not valid
    
    # get list of all files and folders
    path = smartFolder.fullPath
    names = os.listdir(path)
    
    # filter folders and return
    folders = {}
    for name in names:
       if os.path.isdir(os.path.join(path, name)):
         folders[name + '/'] = None
    return folders
  
  
  def getAttribute(self, smartFile, attrib):
    self.protocolValidate(smartFile)    # raise exception if protocol is not valid
    
    # size attribute
    if attrib == "size":
      return { attrib: os.path.getsize(smartFile.fullPath) }
    
    # timestamp attribute
    if attrib == "timestamp":
      return { attrib: datetime.datetime.utcfromtimestamp(os.path.getmtime(smartFile.fullPath)).replace(tzinfo=utc) }
    
    # unsupported attribute
    return None
  
  
  def exists(self, smartPath):
    self.protocolValidate(smartPath)    # raise exception if protocol is not valid
    
    # check existence
    return os.path.exists(smartPath.fullPath)
  
  
  def directCopyFile(self, sourceSmartFile, destSmartFile):
    """ Perform a direct-copy of the file if possible. """
    self.protocolValidate(destSmartFile)      # raise exception if protocol is not valid
    
    # perform the local file copy
    import shutil
    shutil.copyfile(sourceSmartFile.fullPath, destSmartFile.fullPath)
  
  
  def deleteFile(self, smartFile):
    """ Delete the specified file. """
    self.protocolValidate(smartFile)    # raise exception if protocol is not valid
    
    # delete the file
    os.remove(smartFile.fullPath)
  
  
  def readFile(self, smartFile, size=-1):
    """ Read the specified file's contents.  (Optional argument specifies the maximum size that will be read) """
    self.protocolValidate(smartFile)    # raise exception if protocol is not valid
    
    # read the file
    with open(smartFile.fullPath, 'rb') as f:
      contents = f.read(size)
    return contents
  
  
  def writeFile(self, smartFile, contents):
    """ Write contents to the specified file.  (Overwriting file if it exists) """
    self.protocolValidate(smartFile)    # raise exception if protocol is not valid
    
    # write contents to the file
    with open(smartFile.fullPath, 'wb') as f:
      f.write(contents)
  
  
  def appendFile(self, smartFile, contents):
    """ Append contents to the specified file. """
    self.protocolValidate(smartFile)    # raise exception if protocol is not valid
    
    # append contents to the file
    with open(smartFile.fullPath, 'ab') as f:
      f.write(contents)
  
  
  def openFile(self, smartFile, mode='r'):
    """ 'Open' the specified file, and return an iterable 'file'-type object. """
    self.protocolValidate(smartFile)    # raise exception if protocol is not valid
    
    # mode should default to 'r' (in case None is passed from higher-levels)
    if mode is None:
      mode = 'r'        
    
    # open the file and return the iterable 'file' object
    return open(smartFile.fullPath, mode)
    




class LocalMd5Connector(SmartConnector):

  """The LocalMd5Connector class is a local calculation connector for the md5 checksum.
  
  PROTOCOL:    file://
  SUPPORTS:    lists = [],  attributes = [md5],  optional attributes = []
  SPEED TIER:  CALC
  TYPE:        AUTHORITATIVE

  """
  
  # constructors & instance variables
  def __init__(self):
    self.protocol = "file"
    self.tier = ConnTiers.CALC
    self.type = ConnTypes.AUTHORITATIVE
  
  
  # methods
  def getAttribute(self, smartFile, attrib):
    self.protocolValidate(smartFile)    # raise exception if protocol is not valid
    
    # md5 attribute
    if attrib == "md5":
      # imports and defs
      import hashlib
      def hexify(s):
        return ("%02x"*len(s)) % tuple(map(ord, s))
      BLOCKSIZE = 1024*1024
      
      # start main function
      f = open(smartFile.fullPath, "rb")
      sum = hashlib.md5()
      while 1:
        block = f.read(BLOCKSIZE)
        if not block:
          break
        sum.update(block)
      f.close()
      return { attrib: hexify(sum.digest()) }
    
    # unsupported attribute
    return None
  


class LocalMediaLengthConnector(SmartConnector):

  """The LocalMediaLengthConnector class is a local calculation connector for the media file length (in seconds).
  
  PROTOCOL:    file://
  SUPPORTS:    lists = [],  attributes = [secs],  optional attributes = []
  SPEED TIER:  CALC
  TYPE:        AUTHORITATIVE
  
  Installation/dependencies:
    sudo apt-get install python-mysqldb
    pip install MySQL-python
  """
  
  # constructors & instance variables
  def __init__(self):
    self.protocol = "file"
    self.tier = ConnTiers.CALC
    self.type = ConnTypes.AUTHORITATIVE
  
  
  # methods
  def getAttribute(self, smartFile, attrib):
    self.protocolValidate(smartFile)    # raise exception if protocol is not valid
    
    # secs attribute
    if attrib == "secs":
      # imports and defs
      import os, sys, subprocess
      def shell_command(command):
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
        return proc.returncode, proc.stdout.read(), proc.stderr.read()
      
      # start main function - calculate media file length in seconds using php-getid3 via external PHP call
      module_path = os.path.dirname(os.path.realpath(__file__))
      cmd = "{MODPATH}/php/getsecs.php '{SMARTFILEPATH}'".format(MODPATH=module_path, SMARTFILEPATH=smartFile.fullPath)
      returncode,stdout,stderr = shell_command(cmd)
      
      assert len(stderr) == 0, "Error with PHP smartpath-getsecs.php call:\n{}".format(stderr)	# throw error on stderr output - fundamental problems with PHP call
      
      if len(stdout) == 0:
        secs = None  # return None if error
      else:
        secs = int(stdout)
      if secs < 0:
        secs = None  # return None if "-1" or "-2" error results returned
      return { attrib: secs }
    
    # unsupported attribute
    return None
  


class RemoteFileLocalCalcConnector(SmartConnector):

  """The RemoteFileLocalCalcConnector class is a connector that downloads remote files to perform calculation of properties using local calculation connectors.
  
  NOTE: Local calculation connectors must be added to the global tmpBase base - ie:  tmpBase.connectors.append(LocalMd5Connector())

  PROTOCOL:    [ANY]://
  SUPPORTS:    lists = [],  attributes = [<user-specified>],  optional attributes = []
  SPEED TIER:  CALC
  TYPE:        AUTHORITATIVE

  """
  
  # constructors & instance variables
  def __init__(self, parentBase, desiredAttribs):
    self.protocol = parentBase.protocol   # protocol based on parentBase's protocol  ?????? got to be a better way to do this?
    self.tier = ConnTiers.CALC
    self.type = ConnTypes.AUTHORITATIVE
    
    self.desiredAttribs = desiredAttribs  # attributes to be calculated using the locally-downloaded copy of the remote file
  
  
  # methods
  def getAttribute(self, smartFile, attrib):
    self.protocolValidate(smartFile)      # raise exception if protocol is not valid
    
    # try to fetch "desired" attributes using a local temp-file
    if attrib in self.desiredAttribs:
      # copy remote file to a local temp-file
      tempSmartFile = GetSmartTempFile()
      smartFile.copy(tempSmartFile)
      # get all desired attributes then delete the temp-file
      attribs = {}
      try:
        for attrib in self.desiredAttribs:
          attribs[attrib] = getattr(tempSmartFile, attrib)
      finally:
        tempSmartFile.delete()  # delete the temp-file (always)
      return attribs
    
    # unsupported attribute
    return None



class S3Connector(SmartConnector):

  """The S3Connector class is a connector for an AWS S3 file system.
  
  PROTOCOL:    s3://
  SUPPORTS:    lists = [files,folders],  attributes = [size,timestamp],  optional attributes = []
  SPEED TIER:  WAN
  TYPE:        AUTHORITATIVE
  NOTES:       Folder list returns size+timestamp attributes for child files.
  
  Constructor:
    SmartBase(fixMD5=False)  - See instance variable description for effect of optional parameter.
  
  Instance Variables:
    fixMD5                - Set fixMD5=True to allow connector to try to auto-correct md5/etags of multipart uploads when found.  (WARNING: Affects file timestamps.)
  
  Methods:
    touchFile(smartFile)  - Touch the specified file by copying the file to itself.  The main purpose of this is to correct the md5/etag of multi-part upload files.  (WARNING: Affects the file's timestamp.)
  
  """
  
  # constructors & instance variables
  def __init__(self, fixMD5=False):
    """ Set fixMD5=True to allow connector to try to auto-correct md5/etags of multipart uploads when found.  (WARNING: Affects file timestamps.) """
    self.protocol = "s3"
    self.tier = ConnTiers.WAN
    self.type = ConnTypes.AUTHORITATIVE
    self.fixMD5 = fixMD5
    
    import boto3
    self.s3client = boto3.client('s3')      # low level client  (required unfortunately to get folder names)
    self.s3resource = boto3.resource('s3')  # high level resource
  
  
  # methods
  def getFiles(self, smartFolder):
    self.protocolValidate(smartFolder)    # raise exception if protocol is not valid
    
    # get list of all files and folders
    # concepts taken from https://github.com/aws/aws-cli/blob/develop/awscli/customizations/s3/subcommands.py
    # also reference - http://docs.aws.amazon.com/AmazonS3/latest/dev/ListingKeysHierarchy.html
    paginator = self.s3client.get_paginator('list_objects')
    iterator = paginator.paginate(Bucket=smartFolder.base.s3bucket, Prefix=smartFolder.s3key, Delimiter='/')

    # decode response and return
    files = {}
    for response_data in iterator:
      s3files = response_data.get('Contents', [])
      if s3files:
        for s3file in s3files:
          name = s3file['Key'].split('/')[-1]
          if name <> "":
            attribs = {}
            attribs["size"] = int(s3file['Size'])
            attribs["timestamp"] = s3file['LastModified'].replace(tzinfo=utc)
            attribs["md5"] = s3file['ETag'].strip('"')
            if "-" in attribs["md5"]:
              attribs["md5"] = None
              # try to auto-correct md5/etags of multipart uploads when found...  if fixMD5=True...
              if self.fixMD5 and (attribs["size"] < 5000000000):
                # getAttribute will try to auto-correct md5/etags and return refreshed attributes
                attribs = self.getAttribute(smartFolder.base.getFile(smartFolder.path + name), "md5")
            
            files[name] = attribs
    return files
  
  
  def getSubFolders(self, smartFolder):
    self.protocolValidate(smartFolder)    # raise exception if protocol is not valid
    
    # get list of all files and folders
    # concepts taken from https://github.com/aws/aws-cli/blob/develop/awscli/customizations/s3/subcommands.py
    # also reference - http://docs.aws.amazon.com/AmazonS3/latest/dev/ListingKeysHierarchy.html
    paginator = self.s3client.get_paginator('list_objects')
    iterator = paginator.paginate(Bucket=smartFolder.base.s3bucket, Prefix=smartFolder.s3key, Delimiter='/')

    # decode response and return
    folders = {}
    for response_data in iterator:
      s3folders = response_data.get('CommonPrefixes', [])
      if s3folders:
        for s3folder in s3folders:
          name = "/".join(s3folder['Prefix'].split('/')[-2:])
          folders[name] = None
    return folders
  
  
  def getAttribute(self, smartFile, attrib):
    self.protocolValidate(smartFile)    # raise exception if protocol is not valid
    
    def getAttributes(self, smartFile):
      """ Internal function - defined for code re-use """
      s3file = self.s3resource.Object(smartFile.base.s3bucket, smartFile.s3key)
      attribs = {}
      attribs["size"] = s3file.content_length
      attribs["timestamp"] = s3file.last_modified.replace(tzinfo=utc)
      attribs["md5"] = s3file.e_tag.strip('"')
      if "-" in attribs["md5"]:
        attribs["md5"] = None
      attribs["s3meta"] = s3file.metadata
      return attribs
    
    # the following attributes are supported and all of them are always returned
    if attrib in ["size", "timestamp", "md5", "s3meta"]:
      attribs = getAttributes(self, smartFile)
      
      # try to auto-correct md5/etags of multipart uploads when found...  if fixMD5=True
      if self.fixMD5 and (attribs["md5"] is None) and (attribs["size"] < 5000000000):
        self.touchFile(smartFile)
        attribs = getAttributes(self, smartFile)
        attribs["md5touched"] = True    # flag that the file has been touched as auto-correction was applied
      
      return attribs
    
    # unsupported attribute
    return None
  
  
  def exists(self, smartPath):
    self.protocolValidate(smartPath)    # raise exception if protocol is not valid
    
    # check file/folder existence (note: will this work for prefixes????????????????)
    import botocore
    try:
      t = self.s3client.head_object(Bucket=smartPath.base.s3bucket, Key=smartPath.s3key)
      return True     # exists
    except botocore.exceptions.ClientError as e:
      # adapted from http://boto3.readthedocs.org/en/latest/guide/migrations3.html
      error_code = int(e.response['Error']['Code'])
      if error_code == 404:
        return False  # does not exist
      else:
        raise  # some other error occurred - re-raise it
  
  
  def directCopyFile(self, sourceSmartFile, destSmartFile):
    """ Perform a direct-copy of the file if possible. """
    self.protocolValidate(sourceSmartFile)    # raise exception if protocol is not valid
    self.protocolValidate(destSmartFile)      # raise exception if protocol is not valid
    
    # perform the local file copy
    s3dest = self.s3resource.Object(destSmartFile.base.s3bucket, destSmartFile.s3key)
    s3dest.copy_from(CopySource=removePrefix(sourceSmartFile.url, "s3://"))
  
  
  def downloadFile(self, remoteSmartFile, localSmartFile):
    """ Download the specified remote file. """
    self.protocolValidate(remoteSmartFile)    # raise exception if protocol is not valid
    if localSmartFile.base.protocol <> "file":
      raise Exception("Download can only be performed to local 'file://' urls (attempted '{}')".format(localSmartFile.url))
    
    # download the file
    # adapted from: https://github.com/boto/boto3-sample/blob/master/transcoder.py
    streamingBody = self.s3resource.Object(remoteSmartFile.base.s3bucket, remoteSmartFile.s3key).get()['Body']
    with open(localSmartFile.fullPath, 'wb') as dest:
      # Here we write the file in chunks to prevent loading everything into memory at once.
      for chunk in iter(lambda: streamingBody.read(64*1024), b''):
        dest.write(chunk)
  
  
  def uploadFile(self, localSmartFile, remoteSmartFile):
    """ Upload the specified remote file. """
    self.protocolValidate(remoteSmartFile)    # raise exception if protocol is not valid
    if localSmartFile.base.protocol <> "file":
      raise Exception("Upload can only be performed from local 'file://' urls (attempted '{}')".format(localSmartFile.url))
    
    # upload the file
    self.s3resource.Object(remoteSmartFile.base.s3bucket, remoteSmartFile.s3key).put(Body=open(localSmartFile.fullPath, 'rb'))
  
  
  def deleteFile(self, smartFile):
    """ Delete the specified file. """
    self.protocolValidate(smartFile)    # raise exception if protocol is not valid
    
    # delete the file
    self.s3resource.Object(smartFile.base.s3bucket, smartFile.s3key).delete()
  
  
  def readFile(self, smartFile, size=-1):
    """ Read the specified file's contents.  (Optional argument specifies the maximum size that will be read) """
    self.protocolValidate(smartFile)    # raise exception if protocol is not valid
    
    # read the file
    streamingBody = self.s3resource.Object(smartFile.base.s3bucket, smartFile.s3key).get()['Body']
    if size > 0:
      contents = streamingBody.read(size)
    else:
      contents = streamingBody.read()      # Additional logic required, since this function is MUCH faster if size not specified!
    return contents
  
  
  def writeFile(self, smartFile, contents):
    """ Write contents to the specified file.  (Overwriting file if it exists) """
    self.protocolValidate(smartFile)    # raise exception if protocol is not valid
    
    # write the file
    self.s3resource.Object(smartFile.base.s3bucket, smartFile.s3key).put(Body=contents)
  
  
  def appendFile(self, smartFile, contents):
    """ Append contents to the specified file. WARNING: VERY SLOW AND MEMORY INTENSIVE FOR S3:// protocol.  REQUIRES FILE TO BE READ LOCALLY THEN WRITTEN TO. IF REQUIRED FOR LARGER FILES NEED TO REIMPLEMENT BY APPENDING TO LOCAL FILE. """
    self.protocolValidate(smartFile)    # raise exception if protocol is not valid
    
    # append contents to the file (currently implemented as INNEFICIENT in-memory read+append+write operation)
    sizelimit = 10*1024*1024            # impose a 10MB limit due to inneficiencies
    oldcontents = self.readFile(smartFile, sizelimit)
    assert len(oldcontents) < sizelimit, "S3Connector appendFile() is currently limited to {}MB.  See code.".format(int(sizelimit/1024/1024))
    newcontents = oldcontents + contents
    self.writeFile(smartFile, newcontents)
  
  
  def openFile(self, smartFile, mode='r'):
    """ 'Open' the specified file, and return an iterable 'file'-type object. """
    self.protocolValidate(smartFile)    # raise exception if protocol is not valid
    
    # open the file and return the iterable 'streamingBody' object
    streamingBody = self.s3resource.Object(smartFile.base.s3bucket, smartFile.s3key).get()['Body']
    return streamingBody
  
  
  def touchFile(self, smartFile):
    """ Touch the specified file by copying the file to itself.  The main purpose of this is to correct the md5/etag of multi-part upload files.  (WARNING: Affects the file's timestamp.) """
    self.protocolValidate(smartFile)      # raise exception if protocol is not valid
    
    # copy the file to itself - only allowed if we 'REPLACE' the metadata
    s3file = self.s3resource.Object(smartFile.base.s3bucket, smartFile.s3key)
    metadata = s3file.metadata
    s3file.copy_from(CopySource=removePrefix(smartFile.url, "s3://"), Metadata=metadata, MetadataDirective='REPLACE')
  
  



class FtpConnector(SmartConnector):

  """The FtpConnector class is a connector for an FTP file system.
  
  PROTOCOL:    ftp://
  SUPPORTS:    lists = [files,folders],  attributes = [size,timestamp],  optional attributes = []
  SPEED TIER:  WAN
  TYPE:        AUTHORITATIVE
  NOTES:       Folder list returns size+timestamp attributes for child files.
  
  Instance Variables:
    baseurl                      - "ftp://host/"
  
  Methods:
    urlMatches(smartPath)        - Return True if the specified SmartPath's url is supported.
    urlValidate(smartPath)       - Raise exception if the specified SmartPath's url is not valid.
  
  """
  
  # constructors & instance variables
  def __init__(self, host, user="", password="", timezone=utc):
    self.protocol = "ftp"
    self.baseurl = "ftp://" + host + "/"
    self.tier = ConnTiers.WAN
    self.type = ConnTypes.AUTHORITATIVE
    self.timezone = timezone
    
    import ftputil
    self.ftp = ftputil.FTPHost(host, user, password)
    self.ftp.stat_cache.resize(50000)    # default is 5000, but we are regularly using servers with >10,000 files
  
  
  # methods
  def urlMatches(self, smartPath):
    """ Return True if the specified SmartPath's url is supported. """
    return smartPath.url.startswith(self.baseurl)
  
  
  def urlValidate(self, smartPath):
    """ Raise exception if the specified SmartPath's url is not valid. """
    if not self.urlMatches(smartPath):
      raise Exception("The '{}' url does not match the base '{}' url for this connector.".format(smartPath.url, self.baseurl))
  
  
  def getFiles(self, smartFolder):
    self.protocolValidate(smartFolder)    # raise exception if protocol is not valid
    self.urlValidate(smartFolder)         # raise exception if url is not valid
    
    # get list of all files and folders
    path = removePrefix(smartFolder.url, self.baseurl)
    names = self.ftp.listdir(path)
    
    # filter files and return
    files = {}
    for name in names:
       if self.ftp.path.isfile(os.path.join(path, name)):
         files[name] = None
    return files
  
  
  def getSubFolders(self, smartFolder):
    self.protocolValidate(smartFolder)    # raise exception if protocol is not valid
    self.urlValidate(smartFolder)         # raise exception if url is not valid
    
    # get list of all files and folders
    path = removePrefix(smartFolder.url, self.baseurl)
    names = self.ftp.listdir(path)
    
    # filter folders and return
    folders = {}
    for name in names:
       if self.ftp.path.isdir(os.path.join(path, name)):
         folders[name + '/'] = None
    return folders
  
  
  def getAttribute(self, smartFile, attrib):
    self.protocolValidate(smartFile)      # raise exception if protocol is not valid
    self.urlValidate(smartFile)           # raise exception if url is not valid
    
    # size and timestamp attributes are supported and both are always returned
    if attrib in ["size", "timestamp"]:
      path = removePrefix(smartFile.url, self.baseurl)
      s = self.ftp.stat(path)
      attribs = {}
      attribs["size"] = s.st_size
      attribs["timestamp"]  = datetime.datetime.fromtimestamp(s.st_mtime).replace(tzinfo=self.timezone)
      return attribs
    
    # unsupported attribute
    return None
  
  
  def exists(self, smartPath):
    self.protocolValidate(smartPath)      # raise exception if protocol is not valid
    self.urlValidate(smartPath)           # raise exception if url is not valid
    
    path = removePrefix(smartPath.url, self.baseurl)
    return self.ftp.path.exists(path)
  
  
  def downloadFile(self, remoteSmartFile, localSmartFile):
    """ Download the specified remote file. """
    self.protocolValidate(remoteSmartFile)      # raise exception if protocol is not valid
    self.urlValidate(remoteSmartFile)           # raise exception if url is not valid
    if localSmartFile.base.protocol <> "file":
      raise Exception("Download can only be performed to local 'file://' urls (attempted '{}')".format(localSmartFile.url))
    
    import sys
    
    # define the progress callbacks
    def progressInit(name, size):
      self.progressName = name
      self.progressSize = size
      self.progress = 0
      progressUpdate("")
    
    def progressUpdate(chunk):
      self.progress += len(chunk)
      nw = datetime.datetime.now().strftime("%H:%M")
      if self.progressSize != 0:
        pct = 100.0*self.progress/self.progressSize
      else:
        pct = 100.0
      print ' {}  {}    ({:.1f}%)    \r'.format(nw, self.progressName, pct),
      sys.stdout.flush()    
    
    # download the file
    remotepath = removePrefix(remoteSmartFile.url, self.baseurl)
    localpath = localSmartFile.fullPath
    from pprint import pprint
    progressInit(remotepath, remoteSmartFile.size)
    try:
      self.ftp.download(remotepath, localpath, progressUpdate)
    except KeyboardInterrupt:
      print "\nKeyboard interrupt - stopped."
      sys.exit()
    print ""
  
  

class HttpConnector(SmartConnector):

  """The HtpConnector class is a connector for an HTTP file system.
  
  PROTOCOL:    http://
  SUPPORTS:    lists = [NOT SUPPORTED],  attributes = [size,timestamp],  optional attributes = []
  SPEED TIER:  WAN
  TYPE:        AUTHORITATIVE
  NOTES:       Only supports HTTP "files" - ie: file/folder listings not supported.
  
  Instance Variables:
    baseurl                      - "http://host/"
  
  Methods:
    urlMatches(smartPath)        - Return True if the specified SmartPath's url is supported.
    urlValidate(smartPath)       - Raise exception if the specified SmartPath's url is not valid.
  
  """
  
  # constructors & instance variables
  def __init__(self):
    self.protocol = "http"
    self.tier = ConnTiers.WAN
    self.type = ConnTypes.AUTHORITATIVE
    
  
  # methods
  def getAttribute(self, smartFile, attrib):
    self.protocolValidate(smartFile)      # raise exception if protocol is not valid
    
    # size and timestamp attributes are supported and both are always returned
    if attrib in ["size", "timestamp"]:
      import urllib2
      import email.utils
      req = urllib2.urlopen(smartFile.urlQuoted)
      
      attribs = {}
      attribs["size"] = int(req.headers['Content-Length'])
      attribs["timestamp"]  = datetime.datetime(*email.utils.parsedate(req.headers['Last-Modified'])[:6]).replace(tzinfo=utc)  #see http://stackoverflow.com/questions/1471987/how-do-i-parse-an-http-date-string-in-python
      return attribs
    
    # unsupported attribute
    return None
  
  
  def exists(self, smartPath):
    self.protocolValidate(smartPath)      # raise exception if protocol is not valid
    
    import urllib2
    try:
      req = urllib2.urlopen(smartPath.urlQuoted)
      return True
    except urllib2.HTTPError:
      return False
  
  
  def downloadFile(self, remoteSmartFile, localSmartFile):
    """ Download the specified remote file. """
    self.protocolValidate(remoteSmartFile)      # raise exception if protocol is not valid
    if localSmartFile.base.protocol <> "file":
      raise Exception("Download can only be performed to local 'file://' urls (attempted '{}')".format(localSmartFile.url))
    
    def copyfileobjprogress(fsrc, fdst, length=16*1024, callback = None):
      """ Same as shutil.copyfileob, but implements a progress callback.
        References:  http://stackoverflow.com/questions/29967487/get-progress-back-from-shutil-file-copy-thread  &  http://stackoverflow.com/questions/274493/how-to-copy-a-file-in-python-with-a-progress-bar
      """
      pos = 0
      while True:
        buf = fsrc.read(length)
        if not buf:
          break
        fdst.write(buf)
        pos += len(buf)
        if callback:
          callback(pos)
    
    # define the progress callbacks
    def progressInit(name, size):
      self.progressName = name
      self.progressSize = size
      progressUpdate(0)
    
    def progressUpdate(pos):
      import sys
      nw = datetime.datetime.now().strftime("%H:%M")
      pct = 100.0*pos/self.progressSize
      print ' {}  {}    ({:.1f}%)    \r'.format(nw, self.progressName, pct),
      sys.stdout.flush()
      
    # download the file
    remotepath = remoteSmartFile.urlQuoted
    localpath = localSmartFile.fullPath
    import urllib2
    import email.utils
    req = urllib2.urlopen(remotepath)
    progressInit(remotepath, int(req.headers['Content-Length']))
    try:
      with open(localpath, 'wb') as fp:
        copyfileobjprogress(req, fp, 64*1024, progressUpdate)
    except KeyboardInterrupt:
      print "\nKeyboard interrupt - stopped."
      sys.exit()
    print ""
  
  

    
    


##################################################################################################################  

def GetSmartTempFile():
  """ Return a SmartFile object for a randomly-named local file based on the global tmpBase base """
  import uuid
  tempName = str(uuid.uuid4())[:8] + ".tmp"
  return SmartFile(tmpBase, tempName)



tmpBase = SmartBase("file:///tmp/")
tmpBase.connectors.append(LocalFileSystemConnector())

def removePrefix(s, prefix):
  """ If the string starts with prefix, return the string with the prefix removed.  
    Note: str.lstrip() should work, but gobbles up too many characters.  
    See: http://stackoverflow.com/questions/4148974/is-this-a-bug-in-python-2-7
    See: https://mail.python.org/pipermail/python-dev/2015-March/138727.html
  """
  if s.startswith(prefix):
    return s[len(prefix):]
  else:
    return s

