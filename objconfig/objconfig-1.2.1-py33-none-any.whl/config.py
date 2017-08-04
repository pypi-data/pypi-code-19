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

from objconfig.util import ArrayAccess
from objconfig.util import Countable
from objconfig.util import Iterator
from objconfig.exception import InvalidArgumentException
from objconfig.exception import RuntimeException
import inspect
import copy


class Config(Countable, Iterator, ArrayAccess):
    r"""
    Following is the class documentation as given in zend-config::
    
        /**
         * Provides a property based interface to an array.
         * The data are read-only unless $allowModifications is set to true
         * on construction.
         *
         * Implements Countable, Iterator and ArrayAccess
         * to facilitate easy access to the data.
         */
    """
    
    def __len__(self):
        r"""
        Notes:
            __len__ is inherited from Countable
        """
        
        return len(self.__data)
    
    def __iter__(self):
        r"""
        Notes:
            __iter__ is inherited from Iterator
        """
        
        def ConfigIterator(self):
            for key, value in self.__data.items():
                yield key, value
        return ConfigIterator(self)
    
    def __getitem__(self, key):
        r"""
        Notes:
            __getitem__ is inherited by ArrayAccess
        
        Following is the header as given in zend-config::
        
            /**
             * offsetGet(): defined by ArrayAccess interface.
             *
             * @see    ArrayAccess::offsetGet()
             * @param  mixed $offset
             * @return mixed
             */
        """
        
        return self.__data[key]
    
    def __setitem__(self, key, value):
        r"""
        Notes:
            __setitem_ is inherited by ArrayAccess
            
        Following is the header as given in zend-config::
        
            /**
             * offsetSet(): defined by ArrayAccess interface.
             *
             * @see    ArrayAccess::offsetSet()
             * @param  mixed $offset
             * @param  mixed $value
             * @return void
             */
        """
        
        self.__setattr__(key, value)
    
    def __delitem__(self, key):
        r"""
        Notes:
            __delitem__ is inherited by ArrayAccess
        
        Following is the header as given in zend-config::
        
            /**
             * offsetUnset(): defined by ArrayAccess interface.
             *
             * @see    ArrayAccess::offsetUnset()
             * @param  mixed $offset
             * @return void
             */
        """
        
        self.__delattr__(key)
    
    def __init__(self, array, allowModifications=False):
        r"""
        Notes:
            array is expected to be instance of dict
            OR implement toArray() method
        
        Following is the header as given in zend-config::
        
            /**
             * Constructor.
             *
             * Data is read-only unless $allowModifications is set to true
             * on construction.
             *
             * @param  array   $array
             * @param  bool $allowModifications
             */
        """
        
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Whether modifications to configuration data are allowed.
             *
             * @var bool
             */
        """
        self.__allowModifications = allowModifications
        
        r"""
        protected $skipNextIteration;
        
        Notes:
            Not necessary, items() is an up-to-date view
            
        Following is the header as given in zend-config::
        
            /**
             * Used when unsetting values during iteration to ensure we do not skip
             * the next element.
             *
             * @var bool
             */
        """  # -- unnecessary
        
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Data within the configuration.
             *
             * @var array
             */
        """
        self.__data = {}
        
        try:
            for key, value in array.items():
                if 'items' in dir(value):
                    self.__data[key] = Config(value, allowModifications=self.__allowModifications)
                elif 'toArray' in dir(value) and inspect.ismethod(value.toArray):
                    self.__data[key] = Config(value.toArray(), allowModifications=self.__allowModifications)
                else:
                    self.__data[key] = value
        except AttributeError:
            raise InvalidArgumentException("Config: __init__ passed array doesn't implement key, value : items()")
    
    def get(self, name, default=None):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Retrieve a value and return $default if there is no element set.
             *
             * @param  string $name
             * @param  mixed  $default
             * @return mixed
             */
        """
        
        if name in self.__data:
            return self.__data[name]
        return default
    
    def __getattr__(self, attribute):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Magic function so that $obj->value will work.
             *
             * @param  string $name
             * @return mixed
             */
        """
        
        return self.get(attribute)
    
    def __setattr__(self, attribute, value):
        r"""
        Notes:
            Makes a new Config object if value implements key, value : items()
        
        Following is the header as given in zend-config::
        
            /**
             * Set a value in the config.
             *
             * Only allow setting of a property if $allowModifications  was set to true
             * on construction. Otherwise, throw an exception.
             *
             * @param  string $name
             * @param  mixed  $value
             * @return void
             * @throws Exception\RuntimeException
             */
        """
        
        if attribute == '_Config__allowModifications':
            self.__dict__['_Config__allowModifications'] = value
            return
        elif attribute == '_Config__data':
            self.__dict__['_Config__data'] = value
            return
        if self.__allowModifications:
            if isinstance(value, dict):
                self.__data[attribute] = Config(value, allowModifications=True)
            elif attribute is None:
                raise RuntimeException("Config: __setattr__ attribute must have name")
            else:
                self.__data[attribute] = value
        else:
            raise RuntimeException("Config: __setattr__ config is read only")
    
    def __deepcopy__(self, memo):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Deep clone of this instance to ensure that nested Zend\Configs are also
             * cloned.
             *
             * @return void
             */
        """
        
        copyconf = Config({}, allowModifications=True)
        for key, value in self:
            setattr(copyconf, key, copy.deepcopy(value))
        if not self.__allowModifications:
            copyconf.isReadOnly()
        return copyconf
    
    def _clone(self):
        return copy.deepcopy(self)
    
    def copy(self):
        return self._clone()
    
    def toArray(self):
        r"""
        Notes:
            Returns a copy of the data dictionar(ies)
    
        Following is the header as given in zend-config::
        
            /**
             * Return an associative array of the stored data.
             *
             * @return array
             */
        """
        
        array = {}
        for key, value in self.__data.items():
            if 'toArray' in dir(value) and inspect.ismethod(value.toArray):
                array[key] = value.toArray()
            else:
                array[key] = value
        return array
    
    def _isset(self, attribute):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * isset() overloading
             *
             * @param  string $name
             * @return bool
             */
        """
        
        return attribute in self.__data
    
    def __delattr__(self, attribute):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * unset() overloading
             *
             * @param  string $name
             * @return void
             * @throws Exception\InvalidArgumentException
             */
        """
        
        if self.__allowModifications:
            del self.__data[attribute]
        else:
            raise InvalidArgumentException("Config: __delattr__ config is read only")
    
    def merge(self, merge):
        r"""
        Notes:
            Checks for existence of merge and toArray method
        
        Following is the header as given in zend-config::
        
            /**
             * Merge another Config with this one.
             *
             * For duplicate keys, the following will be performed:
             * - Nested Configs will be recursively merged.
             * - Items in $merge with INTEGER keys will be appended.
             * - Items in $merge with STRING keys will overwrite current values.
             *
             * @param  Config $merge
             * @return Config
             */
        """
        
        for key, value in merge:
            if key in self.__data:
                if (('toArray' in dir(value) and inspect.ismethod(value.toArray))
                        and ('merge' in dir(self) and inspect.ismethod(self.__data[key].merge))):
                    self.__data[key].merge(value)
                elif 'toArray' in dir(value) and inspect.ismethod(value.toArray):
                    self.__data[key] = Config(value.toArray(), allowModifications=self.__allowModifications)
                else:
                    self.__data[key] = value
            else:
                if 'toArray' in dir(value) and inspect.ismethod(value.toArray):
                    self.__data[key] = Config(value.toArray(), allowModifications=self.__allowModifications)
                else:
                    self.__data[key] = value
        return self
    
    def setReadOnly(self):
        r"""
        Note:
            Tests for setReadOnly method
        
        Following is the header as given in zend-config::
        
            /**
             * Prevent any more modifications being made to this instance.
             *
             * Useful after merge() has been used to merge multiple Config objects
             * into one object which should then not be modified again.
             *
             * @return void
             */
        """
        
        self.__allowModifications = False
        for value in self.__data.values():
            if 'setReadOnly' in dir(value) and inspect.ismethod(value.setReadOnly):
                value.setReadOnly()
    
    def isReadOnly(self):
        r"""
        Following is the header as given in zend-config::
        
            /**
             * Returns whether this Config object is read only or not.
             *
             * @return bool
             */
        """
        
        return not self.__allowModifications
