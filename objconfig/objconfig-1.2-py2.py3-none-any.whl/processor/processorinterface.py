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

from objconfig.exception import RuntimeException


class ProcessorInterface():
    r"""
    The following is an 'interface' (abstraction) to be implemented
    by all configuration processors
    """
    
    def process(self, value):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Process the whole Config structure and recursively parse all its values.
             *
             * @param  Config $value
             * @return Config
             */
        """
        
        raise RuntimeException("ProcessorInterface: process not implemented in child class")
    
    def processValue(self, value):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Process a single value
             *
             * @param  mixed $value
             * @return mixed
             */
        """
        
        raise RuntimeException("ProcessorInterface: processValue not implemented in child class")
