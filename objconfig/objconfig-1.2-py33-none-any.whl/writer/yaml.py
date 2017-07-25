"""
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
import yaml


class Yaml(AbstractWriter):
    """
    Following is the class documentation as given in zend-config:
    
    There is no documentation
    """
    
    def processConfig(self, config):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * processConfig(): defined by AbstractWriter.
             *
             * @param  array $config
             * @return string
             * @throws Exception\RuntimeException
             */
        """
        
        config = config.toArray() if 'toArray' in dir(config) and inspect.ismethod(config.toArray) else config
        ret = ''
        try:
            ret = yaml.dump(config, default_flow_style=False)
        except Exception as e:
            raise RuntimeException("Yaml: unable to process config: %s" % e)
        
        return ret
