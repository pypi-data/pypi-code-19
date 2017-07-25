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

from objconfig.reader import ReaderInterface
from objconfig.exception import RuntimeException
import xml.etree.ElementTree as ElementTree
import xml.etree.ElementInclude as ElementInclude
import os


class Xml(ReaderInterface):
    r"""
    Following is the class documentation as given in zend-config::
    
        /**
         * XML config reader.
         */
    """
    
    def loader(self, href, parse, encoding=None):
        """
        Load the XML file from a file location
        
        Args:
            href: absolute/relative location of the file
            parse: do we immediately parse the file
            encoding: useful if not parsing, decodes the file from this encoding
        
        Returns:
            The file decoded file data if not parsed, otherwise the the ElementTree.parsed() root
        """
        
        if href[0] != '/':
            href = os.path.join(self.directory, href)
        if not os.path.isfile(href) or not os.access(href, os.R_OK):
            raise RuntimeException("Xml: File %s Doesn't Exist or Not Readable (xi)" % href)
        
        file = open(href)
        if parse == "xml":
            data = ElementTree.parse(file).getroot()
        else:
            data = file.read()
            if encoding:
                data = data.decode(encoding)
        file.close()
        return data
    
    def __init__(self):
        """Initialize root and directory."""
        
        r"""
        Actually ElementTree root element
        
        Following is the header as given in zend-config::
        
            /**
             * XML Reader instance.
             *
             * @var XMLReader
             */
        """
        self.root = None
        
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Directory of the JSON file
             *
             * @var string
             */
        """
        self.directory = ''
    
    def fromFile(self, filename):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * fromFile(): defined by Reader interface.
             *
             * @see    ReaderInterface::fromFile()
             * @param  string $filename
             * @return array
             * @throws Exception\RuntimeException
             */
        """
        
        if not os.path.isfile(filename) and not os.access(filename, os.R_OK):
            raise RuntimeException("Xml: File %s Doesn't Exist or Not Readable" % filename)
        
        self.directory = os.path.dirname(filename.rstrip(os.sep)) or '.'
        
        try:
            xmlcontent = ''
            with open(filename, "r") as file:
                for line in file:
                    if "@include" in line:
                        include = line.split(":")[1].strip()
                        with open(os.path.join(self.directory, include), "r") as includedfile:
                            for includedline in includedfile:
                                xmlcontent += includedline
                    else:
                        xmlcontent += line
            
            self.root = ElementTree.fromstring(xmlcontent)
            ElementInclude.include(self.root, self.loader)
        except ElementTree.ParseError as e:
            raise RuntimeException("Xml: Error Reading XML file \"%s\": %s" % (filename, e))
        
        return self.process(self.root)
    
    def fromString(self, string):
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
        
        if not string:
            return {}
        
        self.directory = None
        
        if "@include" in string:
            raise RuntimeException("Xml: Cannot Process @include When Reading From String")
        
        try:
            self.root = ElementTree.fromstring(string)
        except ElementTree.ParseError as e:
            raise RuntimeException("Xml: Error Reading XML string: %s" % e)
        
        return self.process(self.root)
    
    def process(self, elem):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Process the next inner element.
             *
             * @return mixed
             */
        """
        
        ret = {}
        
        for child in elem:
            if not child.getchildren():
                if child.attrib and ("value" in child.attrib):
                    ret[child.tag] = child.attrib["value"]
                else:
                    ret[child.tag] = child.text
            else:
                ret[child.tag] = self.process(child)
        
        return ret
