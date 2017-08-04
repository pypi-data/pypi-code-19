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

from configparser import ConfigParser
import configparser
from objconfig.reader import ReaderInterface
from objconfig.exception import RuntimeException
from objconfig.util import array_merge_recursive
import os
import collections


class Ini(ReaderInterface):
    r"""
    Following is the class documentation as given in zend-config::
    
        /**
         * INI config reader.
         */
    """
    
    @staticmethod
    def configParserToDict(config):
        """
        Transform a configparser object into a dictionary.
        """
        
        ret = {}
        
        for section in config.items():
            ret[section[0]] = {}
            for key in config[section[0]]:
                ret[section[0]][key] = config[section[0]][key]
        
        return ret
    
    def __init__(self, nestSeparator='.'):
        """
        Initialize nestSeparator and directory
        """
        
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Separator for nesting levels of configuration data identifiers.
             *
             * @var string
             */
        """
        self.nestSeparator = nestSeparator
        
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Directory of the file to process.
             *
             * @var string
             */
        """
        self.directory = ''
    
    def setNestSeparator(self, separator):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Set nest separator.
             *
             * @param  string $separator
             * @return self
             */
        """
        
        self.nestSeparator = separator
        return self
    
    def getNestSeparator(self):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Get nest separator.
             *
             * @return string
             */
        """
        
        return self.nestSeparator
    
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
        
        if not os.path.isfile(filename) or not os.access(filename, os.R_OK):
            raise RuntimeException("Ini: File %s Doesn't Exist or Not Readable" % filename)
        
        self.directory = os.path.dirname(filename.rstrip(os.sep)) or '.'
        
        ini = ConfigParser()
        
        try:
            inicontent = ''
            with open(filename, "r") as file:
                for line in file:
                    if "@include" in line:
                        include = line.split("=")[1]
                        if include[0] != '/':
                            include = os.path.join(self.directory, include)
                        if (not os.path.isfile(os.path.join(self.directory, include))
                                or not os.access(os.path.join(self.directory, include), os.R_OK)):
                            raise RuntimeException("Ini: File %s Doesn't Exist or Not Readable" % os.path.join(self.directory, include))
                        with open(include, "r") as includedfile:
                            for includedline in includedfile:
                                inicontent += includedline
                    else:
                        inicontent += line
            
            ini.read_string(inicontent)
        except configparser.Error as e:
            raise RuntimeException("Ini: Error Reading INI file \"%s\": %s" % (filename, e))
        
        ret = Ini.configParserToDict(ini)
        
        return self.process(ret)
    
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
        
        ini = ConfigParser()
        
        if "@include" in string:
            raise RuntimeException("Ini: Cannot Process @include When Reading From String")
        
        try:
            ini.read_string(string)
        except configparser.Error as e:
            raise RuntimeException("Ini: Error Reading INI string: %s" % e)
        
        ret = Ini.configParserToDict(ini)
        
        return self.process(ret)
    
    def process(self, data):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Process data from the parsed ini file.
             *
             * @param  array $data
             * @return array
             */
        """
        
        ret = {}
        
        for section, value in data.items():
            if isinstance(value, dict):
                if self.nestSeparator in section:
                    sections = section.split(self.nestSeparator)
                    ret = array_merge_recursive(ret, self.buildNestedSection(sections, value))
                else:
                    ret[section] = self.processSection(value)
            else:
                self.processKey(section, value, ret)
        
        return ret
    
    def buildNestedSection(self, sections, value):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Process a nested section
             *
             * @param array $sections
             * @param mixed $value
             * @return array
             */
        """
        
        if not len(sections):
            return self.processSection(value)
        
        sections = collections.deque(sections)
        
        nestedSection = {}
        
        first = sections.popleft()
        nestedSection[first] = self.buildNestedSection(sections, value)
        return nestedSection
    
    def processSection(self, section):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Process a section.
             *
             * @param  array $section
             * @return array
             */
        """
        
        ret = {}
        for key, value in section.items():
            self.processKey(key, value, ret)
        
        return ret
    
    def processKey(self, key, value, ret):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Process a key.
             *
             * @param  string $key
             * @param  string $value
             * @param  array  $config
             * @return array
             * @throws Exception\RuntimeException
             */
        """
        
        if self.nestSeparator in key:
            pieces = key.split(self.nestSeparator, 1)
            if not len(pieces[0]) or not len(pieces[1]):
                raise RuntimeException("Ini: Invalid Key \"%s\"" % key)
            elif not pieces[0] in ret:
                if pieces[0] == '0' and ret:
                    ret = {pieces[0]: ret}
                else:
                    ret[pieces[0]] = {}
            elif ((isinstance(ret[pieces[0]], dict) and pieces[1] in ret[pieces[0]])
                    or (not isinstance(ret[pieces[0]], dict) and ret[pieces[0]])):
                raise RuntimeException("Ini: Cannot Create Sub-Key for \"%s\" : \"%s\", as key already exists" % (pieces[0], pieces[1]))
            
            self.processKey(pieces[1], value, ret[pieces[0]])
        else:
            ret[key] = value
