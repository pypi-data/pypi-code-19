from __future__ import division
from random import choice, shuffle
from copy import deepcopy
from Operations import *
from utils import *
from PlayString import PlayString

"""

    metaPattern: Abstract Base Class for Pattern behaviour

"""

class metaPattern(object):
    """ Abstract base class for Patterns """

    data = None
    bracket_style = "[]"
    debugging = False

    def __init__(self, data=[]):

        if self.__class__ not in PATTERN_WEIGHTS:
            PATTERN_WEIGHTS.insert(-1, self.__class__)
        
        if type(data) is str:
            
            self.fromString(data)

        elif type(data) is tuple:

            self.data = PGroup(data)
            self.make()

        elif isinstance(data, self.__class__):

            self.data = data.data
            
        else:
            
            self.data = data
            self.make()
            
    def __len__(self):
        lengths = [1] + [len(p) for p in self.data if isinstance(p, Pattern)]
        return LCM(*lengths) * len([item for item in self.data if not isinstance(item, EmptyItem)])
    
    def __str__(self):
        try:
            if len(self.data) > 20:
                val = self.data[:8] + [dots()] + self.data[-8:]
            else:
                val = self.data
        except AttributeError:
            val = self.data
        return "P" + self.bracket_style[:-1] + ( repr(val)[1:-1] ) + self.bracket_style[-1]

    def __repr__(self):
        return str(self)

    def string(self):
        """ Returns a PlayString in string format from the Patterns values """
        string = ""
        for item in self.data:
            if isinstance(item, (PGroup, GeneratorPattern)):
                string += item.string()
            elif isinstance(item, Pattern):
                string += "(" + "".join([(s.string() if hasattr(s, "string") else str(s)) for s in item.data]) + ")"
            else:
                string += str(item)
        return string

    def asGroup(self):
        return PGroup(self.data)

    def convert_data(self, dtype=float):
        """ Makes a true copy and converts the data to a given data type """
        return self.true_copy([(item.convert_data(dtype) if isinstance(item, metaPattern) else dtype(item)) for item in self.data])

    def map(self, func):
        return self.__class__([(item.map(func) if isinstance(item, metaPattern) else func(item)) for item in self.data])
    
    """

        Pattern container methods
        -------------------------

    """

    # this is replaced in FoxDot.TimeVar
    def __getitem__(self, key):
        return self.getitem(key)

    def getitem(self, key):
        """ Is called by __getitem__ """
        if isinstance(key, (metaPattern, tuple)):
            val = self.__class__([self.getitem(n) for n in key])
        elif isinstance(key, slice):
            val = self.__getslice__(key.start,  key.stop, key.step)
        else:
            i = key % len(self.data)
            val = self.data[i]
            if isinstance(val, Pattern):
                j = key // len(self.data)
                val = val.getitem(j)
            elif isinstance(val, GeneratorPattern):
                val = val.getitem()
        return val
    
    def __setitem__(self, key, value):
        i = key % len(self.data)
        if isinstance(self.data[i], metaPattern):
            j = key // len(self.data)
            self.data[i][j] = value
        else:
            if key >= len(self.data):
                self.data[i] = Pattern([self.data[i], Format(value)]).stutter([key // len(self.data) , 1])
            else:
                self.data[i] = Format(value)

    def setitem(self, key, value):
        self.data[key] = Format(value)
            
    def __iter__(self):
        for i in range(len(self)):
            yield self.getitem(i)

    def items(self):
        for i, value in enumerate(self):
            yield i, value

    def __getslice__(self, start, stop, step=1):

        start = start if start is not None else 0
        stop  = min(stop, len(self)) if stop is not None else len(self)
        step  = step if step is not None else 1

        if stop < start:

            stop = (len(self.data) + start)

        return Pattern([self[i] for i in range(start, stop, step) ])
            
    def __setslice__(self, i, j, item):
        self.data[i:j] = Format(item)

    # count all values that occur?
    def count(self, item):
        return self.data.count(item)

    """

        Pattern operators (i.e. magic methods)
        --------------------------------------

    """
    def __add__(self, other):  return PAdd(self, other)
    def __radd__(self, other): return PAdd(self, other)
    def __sub__(self, other):  return PSub(self, other)
    def __rsub__(self, other): return PSub2(self, other)
    def __mul__(self, other):  return PMul(self, other)
    def __rmul__(self, other): return PMul(self, other)
    def __div__(self, other):  return PDiv(self, other)
    def __rdiv__(self, other): return PDiv2(self, other)
    def __mod__(self, other):  return PMod(self, other)
    def __rmod__(self, other): return PMod2(self, other)
    def __pow__(self, other):  return PPow(self, other)
    def __rpow__(self, other): return PPow2(self, other)
    def __xor__(self, other):  return PPow(self, other)
    def __rxor__(self, other): return PPow2(self, other)
    def __truediv__(self, other):  return PDiv(self, other)
    def __rtruediv__(self, other): return PDiv2(self, other)

    def __abs__(self):
        return self.__class__([abs(item) for item in self])
    def abs(self):
        return abs(self)

    """

        Piping patterns together using the '|' operator

    """
    
    def __or__(self, other):
        """ Use the '|' symbol to 'pipe' Patterns into on another """
        return self.pipe(other)
    def __ror__(self, other):
        """ Use the '|' symbol to 'pipe' Patterns into on another """
        return asStream(other).pipe(self)

    """

        Zipping patterns together using the '&' operator

    """

    def __and__(self, other):
        return self.zip(other)
    def __rand__(self, other):
        return asStream(other).zip(self)
    
    #: Comparisons
    def __eq__(self, other):
        return PEq(self, other)
    def __ne__(self, other):
        return PNe(self, other)
    
    def __gt__(self, other):
        return Pattern([int(value > modi(asStream(other), i)) for i, value in enumerate(self)])
    def __ge__(self, other):
        return Pattern([int(value >= modi(asStream(other), i)) for i, value in enumerate(self)])
    def __lt__(self, other):
        return Pattern([int(value < modi(asStream(other), i)) for i, value in enumerate(self)])
    def __le__(self, other):
        return Pattern([int(value <= modi(asStream(other), i)) for i, value in enumerate(self)])

    # Methods for strings as pattern

    def fromString(self, string):
        import Parse
        self.data = Parse.Parse(string)
        self.make()
        return self

    def flat(self):
        """ P.flat() -> un-nested pattern """
        new = []
        for item in self.data:
            try:
                item = item.flat()
                new += [i for i in item]
            except:
                new.append(item)
        return Pattern(new)
    
    def coeff(self):
        """ Returns a duration value relative to the type of pattern. Most patterns return val unchanged """
        return 1.0

    # Methods that return augmented versions of original

    def copy(self):
        return self.__class__(self.data[:])

    def true_copy(self, new_data=None):
        new = self.__class__()
        new.__dict__ = {key: value for key, value in self.__dict__.items()}
        if new_data is not None:
            new.data = new_data
        return new

    def shuffle(self):
        new = self.__class__(self.data[:])
        shuffle(new.data)
        return new

    def reverse(self):
        new = self.__class__(self.data[:])
        new.data.reverse()
        return new

    @loop_pattern_method
    def pivot(self, i):
        """ Mirrors and rotates the Pattern such that the item at index 'i'
            is in the same place """
        if len(self) > 0:
            mid = len(self) / 2
            if i > mid:
                i = len(self) - i - 1
                new = self.mirror().rotate((2*(i % len(self)))+1)
            else:
                new = self.rotate((2*(i % len(self)))+1).mirror()
        else:
            new = self.copy()
        return new

    @loop_pattern_method
    def stretch(self, size):
        """ Stretches (repeats) the contents until len(Pattern) == size """
        new = []
        for n in range(size):
            new.append( modi(self.data, n) )
        new = self.__class__(new)
        return new

    @loop_pattern_method
    def loop(self, n):
        """ Repeats this pattern n times """
        new = []
        for i in range(n):
            new += list(self)
        return self.__class__(new)

    def sort(self):
        """ Used in place of sorted(pattern) to force type """
        return self.__class__(sorted(self.data))

    def __invert__(self):
        return self.mirror()

    def mirror(self):
        """ Reverses the pattern. Differs to `Pattern.reverse()` in that
            all nested patters are also reversed. """
        new = []
        for i in range(len(self.data), 0, -1):

            value = self.data[i-1]

            if hasattr(value, 'mirror'):

                value = value.mirror()
            
            new.append(value)
            
        return self.__class__(new)

    @loop_pattern_method
    def swap(self, n=2):
        new = []
        for pair in [list(val) for val in [reversed(self[i:i+n]) for i in range(0, len(self), n)]]:
            for item in pair:
                new.append(item)
        return self.__class__(new)

    def splice(self, seq, *seqs):
        sequences = (self, seq) + seqs
        size = LCM(*[len(s) for s in sequences])
        new = []
        for i in range(size):
            for seq in sequences:
                new.append(modi(seq, i))
        return self.__class__(new)

    def invert(self):
        new = []
        lrg = float(max(self.data))
        for item in self.data:
            try:
                new.append(item.invert())
            except:
                new.append((((item / lrg) * -1) + 1) * lrg)
        return self.__class__(new)

    @loop_pattern_method
    def rotate(self, n=1):
        n = int(n)
        new = self.data[n:] + self.data[0:n]
        return self.__class__(new)

    # @loop_pattern_method
    def stutter(self, n=2):
        n = asStream(n)
        lrg = max(len(self.data), len(n))
        new = []
        for i in range(lrg):
            for j in range(modi(n,i)):
                new.append(modi(self.data,i))
        return self.__class__(new)

    def shufflets(self, n):
        """ Returns a Pattern of 'n' number of PGroups made from shuffled
            versions of the original Pattern """
        new = self.data[:]
        return Pattern([Pattern(new).shuffle().asGroup() for i in range(n)])

    def layer(self, method, *args, **kwargs):
        """ Zips a pattern with a modified version of itself. Method argument
            can be a function that takes this pattern as its first argument,
            or the name of a Pattern method as a string. """
        
        if callable(method):
            func = method
            args = [self.data] + list(args)
        else:
            func = getattr(self, method)
            assert callable(func)

        return self.zip(func(*args, **kwargs))

    @loop_pattern_method
    def palindrome(self, a=0, b=None):
        """ Returns the original pattern with mirrored version of itself appended.
            a removes values from the middle of the pattern, if positive.
            b removes values from the end of the pattern, should be negative.

            e.g.

            >>> P[:4].palindrome()
            P[0, 1, 2, 3, 3, 2, 1, 0]
            >>> P[:4].palindrome(1)
            P[0, 1, 2, 3, 2, 1, 0]
            >>> P[:4].palindrome(-1)
            P[0, 1, 2, 3, 3, 2, 1]
            >>> P[:4].palindrome(1,-1)
            P[0, 1, 2, 3, 2, 1]

        """
        a = int(a)

        if a < 0:

            a, b = 0, a
        
        return self | self.mirror()[a:b]

    def normalise(self):
        """ Returns the pattern with all values between 0 and 1 """
        pos = self - min(self)
        return pos / max(pos)

    def unduplicate(self):
        """ Removes any consecutive duplicate numbers from a Pattern """
        new = []
        last_val = None
        for value in self:
            if value != last_val:
                new.append(value)
            last_val = value                
        return self.__class__(new)

    @loop_pattern_method
    def limit(self, func, value):
        new = []
        i = 0
        while func(new) < value:
            new.append(self[i])
            i+=1
        return self.__class__(new)

    def amen(self, size=2):
        """ Merges and laces the first and last two items such that a drum pattern "x-o-" would become "(x[xo])-o([-o]-)" """
##        bd = self[0]
##        h1 = self[1]
##        sn = self[0-i]
##        h2 = self[1-i]
##
##        new = [ [bd, PGroupStar(bd, sn)] ] + list(self[1:-i]) + [[sn, sn, sn, h1]] + [ [PGroupStar(h2, sn), [h2, sn]] ]

        new = []

        for n in range(len(self.data)):

            if  n % 4 == 0:

                new.append([self.data[n], PGroupStar(self.data[n], modi(self.data, n + size))])

            elif n % 4 == 2:

                new.append( [self.data[n]]*3+[self.data[n-1]] )

            elif n % 4 == 3:

                new.append( [PGroupStar(self.data[n], self.data[n-1]), [self.data[n], self.data[n-1]] ] )

            else:

                new.append(self.data[n])
        
        return self.__class__(new)

    # Changing the pattern in place
    
    def append(self, item):
        self[len(self):] = [item]
        return self
    
    def i_rotate(self, n=1):
        self.data = self.data[n:] + self.data[0:n]
        return self

    def i_reverse(self):
        self.data.reverse()
        return self

    def i_sort(self):
        self.data = Pattern(sorted(self.data))
        return self

    def i_shuf(self):
        shuffle(self.data)
        return self

    def set(self, index, value):
        self.data[index] = asStream(value)
        return self

    # Boolean tests

    def contains_nest(self):
        """ Returns true if the pattern contains a nest """
        pass

    def startswith(self, prefix):
        return self.data[0] == prefix
    
    def all(self, func=(lambda x: bool(x))):
        """ Returns true if all of the patterns contents satisfies func(x) - default is nonzero """
        if len(self.data) is 0:
            return False
        
        for item in self.data:
            if not func(item):
                return False
        return True
        
    def pipe(self, pattern):
        """ Concatonates this patterns stream with another """
        return Pattern(self.data + asStream(pattern).data)

    def zip(self, other):
        new = []
        other = asStream(other)
        for i in range(LCM(len(self), len(other))):
            new.append((self[i], other[i]))
        return self.__class__(new)
    
    def deepzip(self, other):
        new = []
        other = asStream(other)
        for i in range(LCM(len(self), len(other))):
            p1 = self[i]
            p2 = other[i]
            if isinstance(p1, metaPattern):
                value = p1.deepzip(p2)
            elif isinstance(p2, metaPattern):
                value = p2.deeprzip(p1)
            else:
                value = (p1, p2)
            new.append(value)
        return self.__class__(new)

    def deeprzip(self, other):
        new = []
        other = asStream(other)
        for i in range(LCM(len(self), len(other))):
            p1 = self[i]
            p2 = other[i]
            if isinstance(p1, metaPattern):
                value = p1.deeprzip(p2)
            elif isinstance(p2, metaPattern):
                value = p2.deepzip(p1)
            else:
                value = (p2, p1)
            new.append(value)
        return self.__class__(new)

    # Returns individual elements / slices

    def choose(self):
        """ Returns one randomly selected item """
        return choice(self.data)

    def trim(self, size):
        return self[:size]

    def ltrim(self, size):
        return self[-size:]

    def get_behaviour(self):
        return None

    # Automatic expansion of nested patterns

    def make(self):
        """ This method automatically laces and groups the data """

        if self.debugging:

            print self.data, type(self.data)

        #: Force data into an iterable form
        if isinstance(self.data, str):

            self.data = list(self.data)
            
        if not isinstance(self.data, (PatternType, PlayString)): # not sure about PlayString data
    
            self.data = [self.data]

        #: Put any data in a tuple into a PGroup
        for i, data in enumerate(self.data):
            if type(data) is tuple:
                self.data[i] = PGroup(data)
            elif type(data) is list:
                self.data[i] = Pattern(data)
            elif type(data) is str and len(data) > 1:
                self.data[i] = Pattern(data)

        self.data = list(self.data)
                
        return self

class Pattern(metaPattern):
    """ Base type pattern """
    debug = False

class GeneratorPattern(object):
    """
        Used for when a Pattern does not generate a set length pattern,
        e.g. random patterns
    """
    MAX_SIZE = 2048
    def __init__(self):
        self.mod = Pattern()
        self.mod_functions = []
        self.name  = self.__class__.__name__
        self.data  = []

        self.index   = 0
        self.history = {}

    def __repr__(self):
        return "{}({})".format(self.name, self.data)
        
    def getitem(self, index=None):
        """ Calls self.func(index) to get an item, and also calculates
            performs any arithmetic operation assigned """
        if index is None:
            index, self.index = self.index, self.index + 1
        if index in self.history:
            return self.history[index]
        # Calculate value
        value = self.func(index)
        for i, func in enumerate(self.mod_functions):
            value = func(value, modi(modi(self.mod, i), index))
        # Store if we refer to the same index
        self.history[index] = value
        return value

    def func(self, index):
        return index

    def __len__(self):
        return 1

    def __int__(self):  
        return int(self.getitem())
    def __float__(self):
        return  float(self.getitem())
    
    # Arithmetic operations create new GeneratorPatterns
    def __add__(self, other):
        return self.new(other, Add)
    def __radd__(self, other):
        return self.new(other, Add)
    def __sub__(self, other):
        return self.new(other, Sub)
    def __rsub__(self, other):
        return self.new(other, rSub)
    def __mul__(self, other):
        return self.new(other, Mul)
    def __rmul__(self, other):
        return self.new(other, Mul)
    def __div__(self, other):
        return self.new(other, Div)
    def __truediv__(self, other):
        return self.new(other, Div)
    def __rdiv__(self, other):
        return self.new(other, rDiv)
    def __rtruediv__(self, other):
        return self.new(other, rDiv)

    def new(self, other, func=Nil):
        # Create and empty GeneratorPattern
        new = GeneratorPattern()
        # Give it a list of previous mod_functions
        new.mod_functions = self.mod_functions + [func]
        # Update the base function to be the same
        new.func = self.func
        # Update it's list of modifying values
        new.mod  = Pattern([item for item in self.mod])
        new.mod.append(tuple(asStream(other)))
        return new
        
    # Container methods
    def __iter__(self):
        for i in range(self.MAX_SIZE):
            yield self[i]
    def __getitem__(self, key):
        if type(key) is int:
            return self.getitem(key)
        elif type(key) is slice:
            a = key.start if key.start else 0
            b = key.stop
            c = key.step if key.step else 1
            return Pattern([self[i] for i in range(a, b, c)])

class PatternContainer(metaPattern):
    def getitem(self, key):
        key = key % len(self)
        return self.data[key]
    def __len__(self):
        return len(self.data)
    def __str__(self):
        return str(self.data)
    def __repr__(self):
        return str(self)


class PGroup(metaPattern):
    """
        Class to represent any groupings of notes as denoted by brackets.
        PGroups should only be found within a Pattern object.
        
    """
    
    bracket_style = "()"

    def __init__(self, data=[], *args):
        if not args:
            if isinstance(data, (PGroup, tuple)):
                data = list(data)
        else:
            data = [data] + list(args)

        metaPattern.__init__(self, data)

        # If the PGroup contains patterns, invert it to a Pattern of PGroups
        
        l = [len(p) for p in self.data if isinstance(p, Pattern)]

        if len(l) > 0:

            new_data = []

            for key in range(LCM(*l)):

                new_data.append(self.__class__([item.getitem(key) if isinstance(item, Pattern) else item for item in self.data]))

            self.__class__ = Pattern

            self.data = new_data

    def force_values(self):
        """ Recursively (in place) forces changeable values into non-changeable """
        data = []
        for item in self:
            if isinstance(item, GeneratorPattern):
                new_item = item[0]
            elif isinstance(item, PGroup):
                new_item = item.force_values()
            else:
                new_item = item
            data.append(new_item)
        self.data = data
        return self

    def scale_dur(self, n):
        """ Scales the dur values for all the items in self.data by n """
        for item in self.data:
            item.scale_dur(n)
        return

    def fromString(self, string):
        metaPattern.fromString(self, string)
        self.scale_dur(self.coeff())
        return self

    def merge(self, value):
        """ Merge values into one PGroup """
        if hasattr(value, "__len__"):
            new_data = list(value)
        else:
            new_data = [value]
        return self.__class__(list(self.data) + new_data)

    def calculate_step(self, dur):
        return dur

    def calculate_delay(self, delay):
        return 0

    def calculate_time(self, dur):
        values = []
        step  = self.calculate_step(dur)
        for i, item in enumerate(self):
            delay = self.calculate_delay( i * step )
            if hasattr(item, "calculate_time"):
                delay += item.calculate_time( step )
            values.append( delay )
        return PGroup(values)

    def get_behaviour(self):
        def action(event, key):
            event['delay'] += self.calculate_time(float(event['dur']))
            return event
        return action

    def has_behaviour(self):
        for value in self:
            if isinstance(value, PGroup):
                if value.has_behaviour():
                    return True
        else:
            return False

class PGroupPrime(PGroup):
    def change_state(self):
        """ To be overridden by any PGroupPrime that changes state after access by a Player """
        return
    def convert_data(self, *args, **kwargs):
        self.change_state()
        return PGroup.convert_data(self, *args, **kwargs)
    def has_behaviour(self):
        return True
    def calculate_step(self, dur):
        return float(dur) / len(self)
    def calculate_delay(self, delay):
        return delay

class PGroupStar(PGroupPrime):
    """ Stutters the values over the length of and event's 'dur' """    
    bracket_style="*()"
    def string(self):
        """ Used for SamplePlayerStrings """
        return "[" + PGroupPrime.string(self) + "]"

# Empty items

class EmptyItem(object):
    """ Can be used in a pattern and and is essentially not there """
    def __init__(self):
        pass
    def __repr__(self):
        return "_"

# Used to force any non-pattern data into a Pattern

PATTERN_WEIGHTS = [Pattern, PGroupPrime, PGroup]

PatternType = (Pattern, list)

def asStream(data):
    """ Forces any data into a [pattern] form """
    return data if isinstance(data, Pattern) else Pattern(data)

def Format(data):
    if isinstance(data, list):
        return Pattern(data)
    if isinstance(data, tuple):
        return PGroup(data)
    return data

def Dominant(*patterns):
    classes =  [p.__class__ for p in patterns]
    for i, cls in enumerate(PATTERN_WEIGHTS):
        if cls in classes: break
    return cls, patterns[classes.index(cls)]

def patternclass(a, b):
    return PGroup if isinstance(a, PGroup) and isinstance(b, PGroup) else Pattern

def Convert(*args):
    """ Returns tuples/PGroups as PGroups, and anything else as Patterns """
    PatternTypes = []
    for val in args:
        if isinstance(val, (Pattern, PGroup)):
            PatternTypes.append(val)
        elif isinstance(val, tuple):
            PatternTypes.append(PGroup(val))
        else:
            PatternTypes.append(Pattern(val))
    return PatternTypes if len(PatternTypes) > 0 else PatternTypes[0]

class dots:        
    """ Class for representing long Patterns in strings """
    def __repr__(self):
        return '...'
