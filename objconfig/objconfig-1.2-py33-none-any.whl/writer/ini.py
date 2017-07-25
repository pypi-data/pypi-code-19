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
from objconfig.exception import RuntimeException
import inspect


class Ini(AbstractWriter):
    r"""
    Following is the class documentation as given in zend-config:
    
    There is no documentation
    """
    
    def __init__(self, nestSeparator='.', renderWithoutSections=False):
        """Initializes nestSeparator and renderWithoutSections."""
        
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
             * If true the INI string is rendered in the global namespace without
             * sections.
             *
             * @var bool
             */
        """
        self.renderWithoutSections = renderWithoutSections
    
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
    
    def setRenderWithoutSectionsFlags(self, withoutSections):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Set if rendering should occur without sections or not.
             *
             * If set to true, the INI file is rendered without sections completely
             * into the global namespace of the INI file.
             *
             * @param  bool $withoutSections
             * @return Ini
             */
        """
        
        self.renderWithoutSections = withoutSections
        return self
    
    def shouldRenderWithoutSections(self):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Return whether the writer should render without sections.
             *
             * @return bool
             */
        """
        
        return self.renderWithoutSections
    
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
        iniContents = ''
        if self.shouldRenderWithoutSections():
            iniContents = "[DEFAULT]\n" + self.addBranch(config)
        else:
            config = self.sortRootElements(config)
            if not config["DEFAULT"]:
                del config["DEFAULT"]
            for sectionName, data in config.items():
                if not isinstance(data, dict):
                    iniContents += sectionName + " = " + self.prepareValue(data) + "\n"
                else:
                    iniContents += "[" + sectionName + "]\n" + self.addBranch(data) + "\n"
        return iniContents
    
    def addBranch(self, config, parents=None):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Add a branch to an INI string recursively.
             *
             * @param  array $config
             * @param  array $parents
             * @return string
             */
        """
        
        if parents is None:
            parents = []
        iniContents = ''
        for key, value in config.items():
            group = parents + [key]
            if isinstance(value, dict):
                iniContents += self.addBranch(value, group)
            else:
                iniContents += self.nestSeparator.join(group) + " = " + self.prepareValue(value) + "\n"
        return iniContents
    
    def prepareValue(self, value):
        r"""
        NOTE:
            Just converts to string (minus double-quotes)
        
        Following is the header as given in zend-config::
        
            /**
             * Prepare a value for INI.
             *
             * @param  mixed $value
             * @return string
             * @throws Exception\RuntimeException
             */
        """
        
        if '"' in str(value):
            raise RuntimeException("Ini: Value Cannot Contain Double Quotes")
        else:
            return str(value)
    
    def sortRootElements(self, config):
        r"""
        NOTE:
            Default section replaces empty section, as Ini reader won't read without sections
        
        Following is the header as given in zend-config::
        
            /**
             * Root elements that are not assigned to any section needs to be on the
             * top of config.
             *
             * @param  array $config
             * @return array
             */
        """
        
        ret = {"DEFAULT": {}}
        for key, value in config.items():
            if not isinstance(value, dict):
                # v1.1.1 fixed error of two arguments into one dict
                ret["DEFAULT"].update({key: value})
            else:
                ret[key] = value
        return ret
