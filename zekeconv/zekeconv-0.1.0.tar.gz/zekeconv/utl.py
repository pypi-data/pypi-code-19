import base64
import errno
import json
import os
import re
import sys


# fs -> zeke is "pack" operation
# zeke -> fs is "unpack"

BASE64_PREFIX = "base64:"

#def pack_value(value):
#    """convert single value from filesystem representation to zeke dump format"""
#    if not value:
#        return ""
#    # TODO: strip newline before? no
#    try:
#        return value.decode('utf-8')[:-1] # strip newline added during unpack
#    except UnicodeDecodeError:
#        return BASE64_PREFIX + base64.b64encode(value).decode('utf-8')

def pack_value(value):
    """convert single value from directory representation to zeke dump format"""
    if not value:
        return ""
    
    try:
        # decode and strip newline added during unpack
        #print("HERE1 " + value.decode('utf-8'))
        #print("HERE2 " + strip_trailing_once(value.decode('utf-8'), "\n"))
        return strip_trailing_once(value.decode('utf-8'), "\n")
    except UnicodeDecodeError:
        return BASE64_PREFIX + base64.b64encode(value).decode('utf-8')

def unpack_value(value):
    """convert single value from zeke dump format to directory representation"""
    prefix = BASE64_PREFIX
    if (value.startswith(prefix)):
        # binary data
        return base64.b64decode(value[len(prefix):])
    else:
        # assume text data
        return value + "\n";

def unpack_key(root, dir, source):
    """restore key from directory representation"""
    # os.path.relpath does not access filesystem
    key = os.path.relpath(dir, root)
    if key == ".":
        # this is a root of our directory structure
        if source == None:
            # and the origin is not known
            # ignore this key to prevent overwriting zookeeper root
            return None
        elif source == "/":
            # origin is explicitly set to be the root of Zookeeper tree
            # it is perfectly fine to overwrite root node in this case
            return source
        else:
            # origin is known and is not root
            # that means that origin IS the key
            # (but trailing slashes must be removed)
            return strip_trailing(source, "/")
    else:
        # somewhere deeper inside
        if source == None:
            return "/" + key
        else:
            return source + key
    
    
    ##key = os.path.relpath(dir, root)
    ##if key == ".":
    ##    if source == "/":
    ##        return source
    ##    else:
    ##        # strip trailing slash
    ##        # (source must end with it, client must ensure that)
    ##        # TODO: ?
    ##        return source[:-1]
    ##else:
    ##    return source + key

def pack_pairs(pairs):
    separator = "\n"
    return separator.join(map(json.dumps, pairs)) + separator

def unpack_pair(line):
    lst = json.loads(line)
    # TODO: validate logical correctness
    if type(lst) != list:
        raise ValueError("expected a list, got {0} "
                         "while loading '{1}'".format(type(lst), line.rstrip()))
    if len(lst) != 2:
        raise ValueError("expected list of 2 elements, got {0} "
                         "while loading '{1}'".format(len(lst), line.rstrip()))
    return (lst[0], lst[1])

def key_filename(key, source):
    """convert key name into file name"""
    suffix = ".txt"
    flat = re.sub(r'/', '-', key) + suffix
    if flat == suffix:
        # top; old scheme would yield ".txt"
        # try to employ some information from source
        if not source or source == "/":
            # nothing meaningfull can be derived, 
            return "root" + suffix
        else:
            return os.path.basename(strip_trailing(source, "/")) + suffix
    else:
        return flat
    
    
    # replace slashes with dashes
    #return re.sub(r'/', '-', key) + ".txt"

def strip_source_subpath(key, source):
    """remove subpath prefix from the key"""
    prefix = source if source else "/"
    return key[len(prefix):]

def preprocess_source_subpath(source):
    if not source:
        return None
    else:
        return strip_trailing(source, "/") + "/"
    #if not source:
    #    return "/"
    #if not source.endswith("/"):
    #    return source + "/"

def strip_trailing_once(line, what):
    if (not line) or (not what):
        return line
    
    if line.endswith(what):
        return line[:-len(what)]
    else:
        return line

def strip_trailing(line, what):
    if not line or not what:
        return line
    
    count = 1
    while line.endswith(count * what):
        count = count + 1
        
    if count > 1:
        cut = len(what) * (count - 1)
        return line[:-cut]
    else:
        return line
    
    

