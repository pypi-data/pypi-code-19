r"""
This is a port of zend-config to Python

Some idioms of PHP are still employed, but where possible I have Pythonized it

IGNORE:
    Author: Asher Wolfstein Copyright 2017
    Blog: http://wunk.me/
    E-Mail: asherwunk@gmail.com
    Twitter: https://twitter.com/asherwolfstein Send Me Some Love!
    Package Homepage: http://wunk.me/programming-projects/objconfig-python/
    GitHub: http://github.com/asherwunk/objconfig for the source repository
    DevPost: https://devpost.com/software/objconfig
    Buy Me A Coffee: https://ko-fi.com/A18224XC
    Support Me On Patreon: https://www.patreon.com/asherwolfstein
IGNORE

Following is the header as given in zend-config::

    /**
     * Zend Framework (http://framework.zend.com/)
     *
     * @link      http://github.com/zendframework/zf2 for the
     *            canonical source repository
     * @copyright Copyright (c) 2005-2015 Zend Technologies USA Inc.
     *            (http://www.zend.com)
     * @license   http://framework.zend.com/license/new-bsd New BSD License
     */
"""

from objconfig.writer import AbstractWriter
from objconfig.exception import InvalidArgumentException
from objconfig.exception import RuntimeException
import inspect
import xml.etree.ElementTree as ElementTree
import portalocker


class Xml(AbstractWriter):
    r"""
    Following is the class documentation as given in zend-config:
    
    There is no documentation
    """
    
    def __init__(self):
        """Initializes tree member."""
        
        self.tree = None
    
    def toFile(self, filename, config, exclusive=True):
        r"""
        CHANGELOG:
        objconfig v1.2: use portalocker to establish an exclusive lock if given
        
        Following is the header as given in zend-config::
        
            /**
             * toFile(): defined by Writer interface.
             *
             * @see    WriterInterface::toFile()
             * @param  string  $filename
             * @param  mixed   $config
             * @param  bool $exclusiveLock
             * @return void
             * @throws Exception\InvalidArgumentException
             * @throws Exception\RuntimeException
             */
        """
        
        if not ('toArray' in dir(config) and inspect.ismethod(config.toArray)) and not isinstance(config, dict):
            raise InvalidArgumentException("AbstractWriter: toFile() expects a dictionary or implementing toArray")
        
        if not filename:
            raise InvalidArgumentException("AbstractWriter: No Filename Specified")
        
        self.processConfig(config)
        
        try:
            with open(filename, "w") as file:
                if exclusive:
                    portalocker.lock(file, portalocker.LOCK_EX)
                self.tree.write(file, xml_declaration=True, encoding='unicode')
        except Exception as e:
            raise RuntimeException("AbstractWriter: Error Writing to \"%s\": %s" % (filename, e))
    
    def toString(self, config):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * fromString(): defined by Reader interface.
             *
             * @param  string $string
             * @return array|bool
             * @throws Exception\RuntimeException
             */
        """
        
        if not ('toArray' in dir(config) and inspect.ismethod(config.toArray)) and not isinstance(config, dict):
            raise InvalidArgumentException("AbstractWriter: toString() expects a dictionary or implementing toArray")
        
        self.processConfig(config)
        
        return ElementTree.tostring(self.tree.getroot()).decode()
    
    def processConfig(self, config):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * processConfig(): defined by AbstractWriter.
             *
             * @param  array $config
             * @return string
             */
        """
        
        config = config.toArray() if 'toArray' in dir(config) and inspect.ismethod(config.toArray) else config
        root = ElementTree.Element("zend-config")
        for sectionName, data in config.items():
            element = ElementTree.Element(sectionName)
            if not isinstance(data, dict):
                element.text = data
            else:
                self.addBranch(sectionName, data, element)
            root.append(element)
        
        self.tree = ElementTree.ElementTree(root)
    
    def addBranch(self, branchName, config, root):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Add a branch to an XML object recursively.
             *
             * @param  string    $branchName
             * @param  array     $config
             * @param  XMLWriter $writer
             * @return void
             * @throws Exception\RuntimeException
             */
        """
        
        for key, value in config.items():
            element = ElementTree.Element(key)
            if not isinstance(value, dict):
                element.text = value
            else:
                self.addBranch(key, value, element)
            root.append(element)
