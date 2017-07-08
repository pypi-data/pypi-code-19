import json
import os


##############################################################################################################
# constants
##############################################################################################################


PATH_PREFIX = '/collab'
INPUT_FILE_LOCATION = os.path.join(PATH_PREFIX, 'in.txt')
OUTPUT_FILE_LOCATION = os.path.join(PATH_PREFIX, 'out.txt')

_SOURCE_OF_TRUTH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TRUTH.txt')
_truth = None
def _get_truth():
    """
    load constants from a file that is autogenerated from the outside when this module is compiled.
    This is a convenient way to share constants between different applications during development.
    Uses a cache.
    """
    if _truth is None:
        for fi in os.listdir(os.path.dirname(__file__)):
            print(fi)
        print("-----")
        for fi in os.listdir(os.path.dirname(os.path.dirname(__file__))):
            print(fi)
        print("-----")
        with open(_SOURCE_OF_TRUTH, 'r') as f:
            _input = json.load(f)
    return _truth

def _get_valid_identifier_types():
    """
    returns a list of strings that are all the valid types of identifiers.
    """
    return _get_truth()['valid_identifier_types']

def _get_valid_event_request_names():
    """
    returns a list of strings that are all the valid types of event requests.
    """
    return _get_truth()['valid_event_request_types']


##############################################################################################################
# helpers
##############################################################################################################


class Identifier:
    """
    a token by which objects of different types can be compared.
    All objects that are read from the input have an identifier.
    All objects generated during the output have a preliminary identifier, because the output will be interpreted by the Execution Environment.
    (preliminary identifiers can be used like any other)
    """
    def __init__(self, identifier, type, preliminary=False):
        if type not in _get_valid_identifier_types():
            raise ValueError("'%s' is not a valid type of identifier" % (type,))
        self.id = identifier
        self.type = type
        self.preliminary = preliminary
    def __str__(self):
        return "%s Identifier %s%s" % (self.type, self.id, " (preliminary)" if self.preliminry else "")
    def __eq__(self, other):
        """
        Override the default Equals behavior
        """
        return (self.type == other.type) and (self.id == other.id) and (self.preliminary == other.preliminary)
    def __ne__(self, other):
        """
        Define a non-equality test
        """
        return not self.__eq__(other)
    def to_json(self):
        """
        gives a JSON dictionary representation of this identifier.
        Counterpart to _parse_identifier().
        """
        res = { 'id' : self.id, 'type' : self.type }
        if self.preliminary:
            res['preliminary'] = True
        return res


def _parse_identifier(dictionary):
        """
        creates an Identifier from a JSON dictionary structure
        Counterpart to Identifier.to_json().
        """
        id = dictionary['id']
        type = dictionary['type']
        preliminary = dictionary.get('preliminar', False)
        return Identifier(id, type, preliminary)


_preliminary_dentifier_counter = 0
def _create_preliminary_identifier(type):
    """
    creates a preliminary Identifier, for use by output objects.
    """
    global _preliminary_dentifier_counter
    res = Identifier(_preliminary_dentifier_counter, type, preliminary=True)
    _preliminary_dentifier_counter += 1
    return res


class Tag:
    """
    a Tag consists of a Symbol, defined here as a string, and a number of identifiers.
    It also has an identifier of its own.
    """
    def __init__(self, own_identifier, symbol, *arguments):
        if not isinstance(own_identifier, Identifier):
            raise ValueError("a Tag must get an Identifier as its identifier")
        if not isinstance(symbol, str):
            raise ValueError("the Symbol of a Tag must be given as a string")
        arguments = [_get_identifier(a) for a in arguments]
        self.identifier = own_identifier
        self.symbol = symbol
        self.arguments = arguments
    def __str__(self):
        return "Tag %s: symbol=%s, arguments=(%s)" % (self.identifier, self.symbol, ', '.join(['%s' % a for a in identifiers]))
    def to_json(self):
        """
        gives a JSON dictionary representation of this Tag.
        Counterpart to _parse_tag().
        """
        res = {'id' : self.identifier, 'sym' : self.symbol, 'args' : [self._get_identifier(a).to_json() for a in self.arguments]}
        return res
    def _get_identifier(self, arg):
        if isinstance(arg, Identifier):
            return arg
        if hasattr(arg, 'identifier') and isinstance(arg.identifier, Identifier):
            return arg.identifier
        raise ValueError("each argument of a Tag must either be an Identifier or have an identifier field of that type")


def _parse_tag(dictionary):
    """
    creates a Tag from a JSON dictionary structure
    Counterpart to Tag.to_json().
    """
    identifier = _parse_identifier(dictionary['identifier'])
    symbol = dictionary['symbol']
    args = [_parse_identifier(a) for a in dictionary['args']]
    return Tag(identifier, symbol, args)


##############################################################################################################
# input
##############################################################################################################


_input = None
def _get_input():
    """
    parse the input file. This uses a cache, so it only has to be done once.
    """
    global _input
    if _input is None:
        with open(INPUT_FILE_LOCATION, 'r') as f:
            _input = json.load(f)
    return _input


def get_current_step():
    """
    returns an integer indicating the number of the current step in the execution environment.
    """
    return _get_input()['current_step']


class InputObject:
    """
    represents a file that was given as an input argument, along with information about it.
    """
    def __init__(self, file_name, identifier):
        self.file = os.path.join(PATH_PREFIX, file_name)
        self.identifier = identifier
    def __str__(self):
        return self.identifier


def get_inputs():
    """
    returns a list of inputs that were given to this program.
    """
    inputs = _get_input()['inputs']
    res = [InputObject(a['file'], _parse_identifier(a['identifier'])) for a in inputs]
    return res


class ProgramTrigger:
    """
    describes why this program was triggered
    """
    def __init__(self, event_type, reason):
        self.event_type = event_type
        self.reason = reason


def get_trigger():
    """
    returns a ProgramTrigger that describes why this program was called
    """
    trigger = _get_input()['trigger']
    res = ProgramTrigger(trigger['event_type'], trigger['reason'])
    return res


_all_earlier_tags = None
def get_tags():
    """
    returns a list of tags that were created earlier and given to this program as input.
    """
    global _all_earlier_tags
    if _all_earlier_tags is None:
        tags = _get_input()['tags']
        _all_earlier_tags = [_parse_tag(a) for a in tags]
    return _all_earlier_tags


##############################################################################################################
# output
##############################################################################################################


_output_files = []
_output_tags = []
_output_event_requests = []


class OutputObject:
    """
    represents a file that was created as an output, along with information about it.
    """
    def __init__(self, file_name, identifier):
        self.file = os.path.join(PATH_PREFIX, file_name)
        self.identifier = identifier
    def __str__(self):
        return self.identifier


_output_counter = 0
def add_output_file():
    """
    create an output, to make the results of this program available to other programs and to the Execution Environment.
    you can create multiple outputs, and they will be added in the order in which they were created with this function.
    """
    identifier = _create_preliminary_identifier('file')
    res = OutputObject("%d" % _output_counter, identifier)
    _output_counter += 1
    _output_files.append(res)
    return res


def createTag(symbol, *arguments):
    """
    creates a new Tag using a preexisting Collab Symbol and an arbitrary number of identifiers.
    Note that this Tag is preliminary and will be rejected by the Execution Environment if the Symbol does not actually exist,
    or is not accessible for this program, or if anything else is wrong.
    For any arguments, you may use either an Identifier or any class that has an identifier as a field of the same name,
    which is all of the classes used here.
    """
    identifier = _create_preliminary_identifier('tag')
    res = Tag(identifier, symbol, *arguments)
    _output_tags.append(res)
    return res


class EventRequest:
    """
    represents a request of this program to the Execution Environment.
    """
    def __init__(self, request_type, *args):
        if not request_type in _get_valid_event_request_names():
            raise ValueError("'%s' is not a valid type of event request" % (request_type,))
        for arg in args:
            if not isinstance(arg, str) and not isinstance(arg, Identifier):
                raise ValueError("each argument of an event request must be a string or an Identifier")
        self.request_type
        self.args = args
    def to_json(self):
        """
        gives a JSON dictionary representation of this EventRequest.
        """
        args = [self._argument_to_json(a) for a in self.arguments]
        res = {'request_type' : self.request_type, 'args' : args}
        return res
    def _argument_to_json(self, arg):
        if isinstance(arg, Identifier):
            return arg.to_json()
        if isinstance(arg, str):
            return arg
        raise ValueError("each argument of an event request must be a string or an Identifier")


def add_event_request(request_type, *args):
    """
    add a request to the Execution Environment.
    Note that this function works differently depending on the type of the request.
    """
    res = EventRequest(request_type, *args)
    _output_event_requests.append(res)
    return res


def finalize_output():
    """
    create the output file and write all previously added messages to the execution environemnt into it.
    """
    res = {
        'output_files' : [a.to_json for a in _output_files],
        'output_tags' : [a.to_json for a in _output_tags],
        'event_requests' : [a.to_json for a in _output_event_requests],
    }
    with open(OUTPUT_FILE_LOCATION, 'w') as f:
        json.dump(res, f)



