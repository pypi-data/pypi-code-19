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

from objconfig.exception import InvalidArgumentException
from objconfig.processor import ProcessorInterface
from objconfig import Config
import inspect


class Token(ProcessorInterface):
    r"""
    Following is the class documentation as given in zend-config:
    
    No class documentation was given.
    """
    
    def __init__(self, tokens=None, prefix='', suffix=''):
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * Token Processor walks through a Config structure and replaces all
             * occurrences of tokens with supplied values.
             *
             * @param  array|Config|Traversable   $tokens  Associative array of TOKEN => value
             *                                             to replace it with
             * @param    string $prefix
             * @param    string $suffix
             * @return   Token
             */
        """
    
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * Token prefix.
             *
             * @var string
             */
        """
        self.setPrefix(prefix)
        
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * Token suffix.
             *
             * @var string
             */
        """
        self.setSuffix(suffix)
        
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * The registry of tokens
             *
             * @var array
             */
        """
        self.setTokens(tokens)
        
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * Replacement map
             *
             * @var array
             */
        """
        self.map = None
    
    def setPrefix(self, prefix):
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * @param  string $prefix
             * @return Token
             */
        """
        
        self.map = None
        self.prefix = prefix
        return self
    
    def getPrefix(self):
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * @return string
             */
        """
        
        return self.prefix
    
    def setSuffix(self, suffix):
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * @param  string $suffix
             * @return Token
             */
        """
        
        self.map = None
        self.suffix = suffix
        return self
    
    def getSuffix(self):
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * @return string
             */
        """
        
        return self.suffix
    
    def setTokens(self, tokens):
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * Set token registry.
             *
             * @param  array|Config|Traversable  $tokens  Associative array of TOKEN => value
             *                                            to replace it with
             * @return Token
             * @throws Exception\InvalidArgumentException
             */
        """
        
        if tokens is not None:
            self.tokens = tokens.toArray() if 'toArray' in dir(tokens) and inspect.ismethod(tokens.toArray) else tokens
        else:
            self.tokens = {}
        
        if not isinstance(self.tokens, dict):
            self.tokens = {}
            try:
                for key, val in tokens.items():
                    self.tokens[key] = val
            except Exception:
                raise InvalidArgumentException("Token: Cannot Use %s As Token Registry" % type(tokens))
    
        self.map = None
        return self
    
    def getTokens(self):
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * Get current token registry.
             *
             * @return array
             */
        """
        
        return self.tokens
    
    def addToken(self, token, value):
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * Add new token.
             *
             * @param  string $token
             * @param  mixed $value
             * @return Token
             * @throws Exception\InvalidArgumentException
             */
        """
        
        if not isinstance(str(token), str):
            raise InvalidArgumentException("Token: Cannot Use %s As Token Name" % type(token))
        
        self.tokens[str(token)] = value
        self.map = None
        return self
    
    def setToken(self, token, value):
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * Add new token.
             *
             * @param string $token
             * @param mixed $value
             * @return Token
             */
        """
        
        return self.addToken(token, value)
    
    def buildMap(self):
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * Build replacement map
             *
             * @return array
             */
        """
        
        if self.map is None:
            if not self.suffix and not self.prefix:
                self.map = self.tokens
            else:
                self.map = {}
                for token, value in self.tokens.items():
                    self.map[self.prefix + token + self.suffix] = value
            
            r"""
            foreach (array_keys($this->map) as $key) {
                if (empty($key)) {
                    unset($this->map[$key]);
                }
            }
            """   # -- ?
            
        return self.map
    
    def process(self, config):
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * Process
             *
             * @param  Config $config
             * @return Config
             * @throws Exception\InvalidArgumentException
             */
        """
        
        return self.doProcess(config, self.buildMap())
    
    def processValue(self, value):
        r"""
        Following is the class documentation as given in zend-config::
        
            /**
             * Process a single value
             *
             * @param $value
             * @return mixed
             */
        """
        
        return self.doProcess(value, self.buildMap())
    
    def doProcess(self, value, replacements):
        r"""
        CHANGELOG:
        objconfig v1.1: edit value in place rather than return copy - 3/2/2017
        
        Following is the class documentation as given in zend-config::
        
            /**
             * Applies replacement map to the given value by modifying the value itself
             *
             * @param mixed $value
             * @param array $replacements
             *
             * @return mixed
             *
             * @throws Exception\InvalidArgumentException if the provided value is a read-only {@see Config}
             */
        """
        
        if isinstance(value, Config):
            if value.isReadOnly():
                raise InvalidArgumentException("Token: Cannot Process Config Because It Is Read-Only")
            for key, val in value:
                value.__dict__[key] = self.doProcess(val, replacements)
            return value
        elif isinstance(value, dict):
            for key, val in value.items():
                value[key] = self.doProcess(val, replacements)
            return value
        else:
            stringval = str(value)
            for fr, to in self.map.items():
                stringval = stringval.replace(fr, to)
            r"""
            if ($changedVal !== $stringVal) {
                return $changedVal;
            }
            """  # -- ?
            
            return stringval
