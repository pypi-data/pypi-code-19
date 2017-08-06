# coding=utf-8
"""PyClockPro is Python CLOCK-Pro cache"""

#
# PyClockPro
#
# Copyright 2013 Sami Lehtinen
# http://www.sami-lehtinen.net/
#
# This file is part of PyClockPro project, see:
# https://bitbucket.org/SamiLehtinen/pyclockpro
#
# See: README, TODO and LICENSE files for more information.

# Warning:
# This is basic implementation and first released version.
# This is supposed to work as example, but please note:
# Feedback & pull requests are very welcome, as well as patches, questions,
# suggestions, etc. This code hasn't been reviewed and therefore can contain
# serious errors.

# MIT LICENSE
#
# Copyright (C) 2013 Sami Lehtinen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from collections import namedtuple
from functools import wraps
try:
    from _thread import allocate_lock as Lock
except:
    from _dummy_thread import allocate_lock as Lock

class PyClockPro(object):
    """Python CLOCK-Pro caching implementation.
    Init parameter maximum cache size.
    See: https://bitbucket.org/SamiLehtinen/pyclockpro"""

    def __init__(self, size: "Set maximum cache size"):
        """Init PyClockPro instance with user defined size."""

        self._check_size(size) # Check that cache size is large enough

        # Memory allocation

        self._mem_max = size  # Maximum number or resident pages (cold+hot)
        self._mem_cold = size # Maximum number of cold pages
                              # Value increases when test page gets a hit
                              # Value decreases when test page is removed

        # Handlers

        self._handler_read = None  # Read handler for misses
        self._handler_write = None # Write handler for evicted items
                                   # (write-back cache mode)

        self.clear() # Set up rest of internal state

    def clear(self):
        """Clear cache, set initial internal state.
        Does not clear handlers and size."""
        self._data = {}     # Data is dictionary, which contains
                            # key and value, in value there is list containing
                            # reference boolean and value of the key.
                            # If the value is None it means that this is entry
                            # for a test page.
                            # Example:
                            # {'key': [False, 'Value'],
                            #  ['Key2, None], ...}

        self._meta = []     # Meta is list which contains page index for
                            # maintaining data order in clock, and each entry
                            # in list is list, which contains page type and key.
                            # Example:
                            # [[2, 'key'],[1, 'OtherKey'],[0, 'ThirdKey'], ...]
                            # Page types: int = Name (CLOCK-Pro paper
                            # terminology)
                            # 2 = hot page  (hot page)
                            # 1 = cold page (resident cold page)
                            # 0 = test page (non-resident cold page)

        self._hand_pos_cold = 0 # Cold hand position
        self._hand_pos_test = 0 # Test hand position
        self._hand_pos_hot = 0  # Hot hand position

        # Internal counters

        self._count_cold = 0    # Count of cold pages
        self._count_test = 0    # Count of test pages
        self._count_hot = 0     # Count of hot pages

        # Statistics

        self._stat_get_hits = 0   # Number of cache get hits
        self._stat_get_misses = 0 # Number of cache get misses
        self._stat_set_hits = 0   # Number of cache set hits
        self._stat_set_misses = 0 # Number of cache set misses

    def get(self,
            key: "A key for data to be retrieved from cache",
            default: "Default value to be returned instead of a KeyError"=None):
        """Get data based on key from cache. Read handler can be utilized to
        get data for cache miss, return default value given as parameter can be
        returned, or as last resort KeyError is raised."""
        if key in self._data: # Check if the key is in data dictionary
            data = self._data[key] # Get key's value list from dictionary
            if data is not None: # Is value a cold page?
                data[0] = True # Update reference boolean
                self._stat_get_hits += 1 # Update get cache statistics
                return data[1] # Return value from data list
        self._stat_get_misses += 1 # Update get statistics
        if self._handler_read is not None: # A read handler has been specified
            value=self._handler_read(key) # Read data from the handler
            self.set(key, value) # Store results
            return value # Return data
        if default is not None: # Is default value defined?
            return default # Return default data
        else:
            raise KeyError() # No default, no data, cache lookup failure

    def set(self,
            key: "A key for data to be stored",
            value: "Value for key"):
        """Store / update key and value in cache"""
        if key in self._data: # Check if key is in data dictionary
            if self._data[key] is None: # If page is a test page
                if self._mem_cold < self._mem_max: # Cold count not maxed out?
                    self._mem_cold += 1 # Assign more memory for cold pages
                self._data[key] = [False, value] # Set ref False and store value
                # Move meta data to the end of meta list. Behind hand hot.
                self._meta_del([0, key]) # Remove old test meta data
                self._count_test -= 1 # Update test count
                self._meta_add([2, key]) # Add new hot page to meta data
                self._count_hot += 1 # Update hot count
                self._stat_set_misses += 1 # Update set cache statistics
            else: # Key is already in cache as cold or hot page
                self._data[key] = [True, value] # Set ref True, store value
                self._stat_set_hits += 1 # Update set statistics
                return
        else: # Key key is not in cache
            self._data[key] = [False, value] # Set ref False store value
            self._meta_add([1, key]) # Add cold page meta data to meta list
            self._count_cold += 1 # Update cold page count
            self._stat_set_misses += 1 # Update set cache statistics

    def is_cached(self, key):
        """Check if cache contains value for a key, do not update reference
        boolean"""
        if key in self._data: # Is key in cache?
            if self._data[key] is not None: # Not a test page
                return True # Data is cached (cold or hot page)
        return False # Value is not cached

    # You should get the picture by now, less comments further.

    def set_size(self,
                 size: "New maximum size for cache"):
        """Set new cache size and run eviction"""
        self._check_size(size)
        self._mem_max = size
        self._evict()

    def cache_clear(self):
        """See clear(), this is here only for lru_cache compatibility reasons"""
        self.clear()

    def flush(self):
      """Call writeback handler once for every page in cache.
      Please note, data is still kept in cache, flush does not affect caches
      internal state in anyway. So it doesn't flush only modified since last
      flush data. It flushes all cached data, everytime.
      Application should be aware about what data needs to be actually be
      written out and what shouldn't. Especially if mixed read & write caching
      is being used."""
      if self._handler_write is not None: # Is write handler assigned?
          for k in self._data:
              data = self._data[k]
              if data is not None:
                  self._handler_write(k,data[1]) # Call with key, value

    def cache_info(self):
        """LRU cache_info compatible get (read) cache statistics"""
        return namedtuple('CacheInfo','hits misses maxsize currsize')\
                         (self._stat_get_hits,self._stat_get_misses,
                          self._mem_max,\
                          self._count_hot+self._count_cold
                         )

    def cache_stats(self):
        """PyClockPro full internal counter status"""
        return namedtuple('CacheStats','gethits getmisses sethits setmisses '+\
                          'memmax memcold size counthot countcold counttest'\
                         )\
                         (self._stat_get_hits,self._stat_get_misses,\
                          self._stat_set_hits,self._stat_set_misses,\
                          self._mem_max,self._mem_cold,\
                          self._count_hot+self._count_cold,\
                          self._count_hot,self._count_cold,self._count_test\
                         )

    def set_default(self, key, default=None):
        """If key found, return value, else set default and return it"""
        if key in self._data:
              data = self._data[k]
              if data is not None:
                  return data[1]
        self.set(key, default)
        return default

    def setdefault(self, key, default):
        """Only here for compability reasons see set_default"""
        self.set_default(key, default)

    def set_handler_read(self, fn):
        """Set data source handler and enable data source mode.

        When cache is operating in data source mode, source handler
        is called with key as only parameter, whenever cache miss happens.
        Data source must return value for this key.
        """
        self._handler_read = fn

    def set_handler_write(self, fn):
        """Set write-back handler and enable write-back mode.

        When cache is operating in write-back mode write-back handler
        is called when ever changed data is evicted from cache."""

        self._handler_write = fn

    def dump_status(self):
        """Return memory allocation information as a string.
        Used for debugging."""
        return 'Allocation 3:'+\
              str(self._count_hot+self._count_cold).rjust(3)+\
              '/'+str(self._mem_max).rjust(3)+' 2:'+\
              str(self._count_hot).rjust(3)+\
              '/'+str(self._mem_max-self._mem_cold)+' 1:'+\
              str(self._count_cold).rjust(3)+\
              '/'+str(self._mem_cold).rjust(3)+' 0:'+\
              str(self._count_test).rjust(3)+\
              '/'+str(self._mem_max).rjust(3)

    def dump_state(self,
                   hot_pos: "Place hand hot always at string beginning"=False,
                   color: "Use HTML font color codes in dump"=False):
        """Return internal state as a string for debugging."""
        dump = []

        def hand_data(self, index):
            """If hands point at these entries, place hand symbol in front of
            entry"""
            # Order is meaningful, in case all hands point to the same location
            # 201 should be printed out. Even if hand positions are the same,
            # there's still logical hand order.
            entry = ''
            if index == self._hand_pos_hot:
                if color:
                    entry += '<font color="#04B404">2</font>'
                else:
                    entry += '2'
            if index == self._hand_pos_test:
                if color:
                    entry += '<font color="#04B404">0</font>'
                else:
                    entry += '0'
            if index == self._hand_pos_cold:
                if color:
                    entry += '<font color="#04B404">1</font>'
                else:
                    entry += '1'
            return entry

        def key_data(self, key):
            """Return internal key & _meta information in user friendly
            format"""
            if key[0] == 2: # Hot
                if self._data[key[1]][0]: # Is reference set
                    if color:
                        return '<font color="#FF0000">H</font>'
                    else:
                        return 'H'
                else: # Reference not set
                    if color:
                        return '<font color="#8A0808">h</font>'
                    else:
                        return 'h'
            elif key[0] == 1: # Cold
                if self._data[key[1]][0]: # Is reference set
                    if color:
                        return '<font color="#0000FF">C</font>'
                    else:
                        return 'C'
                else:
                    if color:
                        return '<font color="#08088A">c</font>'
                    else:
                        return 'c'
            else: # Test
                if color:
                    return '<font color="#2E2E2E">n</font>'
                else:
                    return 'n'
        if hot_pos: # Always start from hand hot position
            meta_hot_start = self._meta[self._hand_pos_hot:] + \
                             self._meta[:self._hand_pos_hot]
        else:
            meta_hot_start = self._meta
        for index,key in enumerate(meta_hot_start):
            if hot_pos:
                if index < len(meta_hot_start) - self._hand_pos_hot:
                    index += self._hand_pos_hot
                else:
                    index -= len(meta_hot_start) - self._hand_pos_hot
            dump += hand_data(self,index)
            dump += key_data(self,key)
        if color:
            dump += '<br />'
        return ''.join(dump)

    def __del__(self):
        """Destructor, if write-back mode is used, flush cache content"""
        if self._handler_write is not None:
            self.flush()

    def __delitem_(self, key):
        """Dictionary style access del method, del"""
        # Could be implemented later
        raise NotImplementedError

    def __setitem__(self, key, value):
        """Dictionary style access set method, see set"""
        return self.set(key, value)

    def __getitem__(self, key):
        """Dictionary style access get method, see get"""
        return self.get(key)

    def __contains__(self, key):
        """Disctionary style access contains method, see is_cached"""
        return self.is_cached(key)

    def _hand_hot(self):
        """Hot hand handles hot pages, and moves itself forward"""
        if self._hand_pos_hot == self._hand_pos_test: # Same position?
            self._hand_test() # Maintain hand order
        meta = self._meta[self._hand_pos_hot] # Get meta from hand pos
        if meta[0] == 2: # If page is a hot page
            data=self._data[meta[1]] # Fetch data for key
            if data[0]: # If page is referenced
                data[0] = False # Reset reference boolean
            else: # Page has not been referenced
                meta[0] = 1 # Turn page into cold page
                data[0] = False # Reset reference boolean
                self._count_hot -= 1 # Update hot count
                self._count_cold += 1 # Update cold count
        self._hand_pos_hot += 1 # Move hot hand forward
        if self._hand_pos_hot >= len(self._meta):
            self._hand_pos_hot = 0

    def _hand_cold(self):
        """Cold hand handles cold pages, and moves itself forward"""
        meta = self._meta[self._hand_pos_cold]
        if meta[0] == 1: # Test for resident cold page
            data = self._data[meta[1]] # Fetch value for key from dictionary
            if data[0]: # Test if page has been referenced
                meta[0] = 2 # Turn page into hot page
                data[0] = False # Reset reference boolean
                self._count_cold -= 1 # Update cold count
                self._count_hot += 1 # Update hot count
            else: # Page has not been referenced
                if self._handler_write is not None: # Is write handler assigned?
                    self._handler_write(meta[1], data[1]) # Write data out
                meta[0] = 0 # Turn page into test page
                self._data[meta[1]] = None # Discard cached data
                self._count_cold -= 1 # Update cold count
                self._count_test += 1 # Update hot count
                while self._mem_max < self._count_test: # Too many test pages?
                    self._hand_test() # Test hand removes test pages
        self._hand_pos_cold += 1 # Move cold hand forward
        if self._hand_pos_cold >= len(self._meta):
            self._hand_pos_cold = 0
        while self._mem_max - self._mem_cold < self._count_hot: # Purge hot
            self._hand_hot()

    def _hand_test(self):
        """Test hand handles test pages, and moves itself forward"""
        if self._hand_pos_test == self._hand_pos_cold: # Pointing to same pos?
            self._hand_cold() # Maintain hand order
        meta=self._meta[self._hand_pos_test] # Get meta data
        if meta[0] == 0: # If test page
            del self._data[meta[1]] # Delete data from dictionary
            self._meta_del(meta) # Delete meta information
            self._count_test -= 1 # Update test page count
            if self._mem_cold > 1: # Cold page memory can be decreased?
                self._mem_cold -= 1 # Decrease memory allocation for cold pages
        self._hand_pos_test += 1 # Move test hand forward
        if self._hand_pos_test >= len(self._meta):
            self._hand_pos_test = 0

    def _evict(self):
        """Evict pages from cache by calling _hand_cold, while required"""
        while self._mem_max <= self._count_hot+self._count_cold:
            self._hand_cold()

    def _check_size(self,size):
        """Check new cache size, for acceptable minimum cache size"""
        if size < 3:
            raise ValueError('Cache size too small, minimum size is 3.')

    def _meta_add(self,meta):
        """Add meta data after hand hot, evict data if required from cache,
        update hands accordingly"""
        self._evict()
        self._meta.insert(self._hand_pos_hot,meta)
        max_pos = len(self._meta)
        if self._hand_pos_cold > self._hand_pos_hot:
            self._hand_pos_cold += 1
            if self._hand_pos_cold >= max_pos:
                self._hand_pos_cold = 0
        if self._hand_pos_test >= self._hand_pos_hot:
            self._hand_pos_test += 1
            if self._hand_pos_test >= max_pos:
                self._hand_pos_test = 0
        self._hand_pos_hot += 1
        if self._hand_pos_hot >= max_pos:
           self._hand_pos_hot = 0

    def _meta_del(self,meta):
        """Delete meta data data, update hands accordingly"""
        index=self._meta.index(meta)
        del self._meta[index]
        max_pos = len(self._meta) - 1
        if self._hand_pos_hot >= index:
            self._hand_pos_hot -= 1
            if self._hand_pos_hot < 0:
                self._hand_pos_hot = max_pos
        if self._hand_pos_cold >= index:
            self._hand_pos_cold -= 1
            if self._hand_pos_cold < 0:
                self._hand_pos_cold = max_pos
        if self._hand_pos_test >= index:
            self._hand_pos_test -= 1
            if self._hand_pos_test < 0:
                self._hand_pos_test = max_pos

    def _count_type(self,pagetype):
        """Count meta pages by type, slow debug stuff, was used to confirm
        correct counter functionality."""
        count=0
        for d in self._meta:
            status = d[0]
            if status == pagetype:
              count += 1
            elif pagetype == 3 and status in (1,2): # hot+resident cold pages
              count += 1
        return count

# Decorator code

def cp_cache(maxsize=128):
    """CLOCK-Pro cache decorator.
    Arguments to the cached function must be hashable."""
    # Decorator related parts are more or less directly borrowed from:
    # functools.lru_tools, it helped a lot. - Thanks
    if maxsize is None: # Unlimited size is not an option, use lru_cache as dict
        maxsize = 128

    def decorating_function(user_function,
                tuple=tuple, sorted=sorted, len=len, KeyError=KeyError):
        lock = Lock()
        cache = PyClockPro(maxsize)

        @wraps(user_function)
        def wrapper(*args, **kwds):
            key = args
            if kwds:
                key += kwd_mark + tuple(sorted(kwds.items()))
            with lock:
                try:
                    result = cache[key]
                    return result
                except KeyError:
                    pass
            result = user_function(*args, **kwds)
            with lock:
                cache[key] = result
            return result

        def cache_info():
            """Report cache statistics"""
            with lock:
                return cache.cache_info()

        def cache_clear():
            """Clear the cache and cache statistics"""
            with lock:
                cache.clear()

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return wrapper
    return decorating_function

# Stand alone

if __name__ == '__main__':
    print("""This file is part of PyClockPro project and is not a standalone
program. Please check out project documentation and or README file.""")