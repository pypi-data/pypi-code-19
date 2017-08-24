# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A module to maintain a tool.

Exported classes:

* Tool -- A class encapsulating a tool.
* ParameterDescription -- The base class containing the shared description of
  a parameter (both input and ouput).
* InputParameterDescription -- A class containing the description of an input
  parameter.
* Output ParameterDescription -- A class containing the description of an
  output parameter.
"""

import itertools
import os
import platform
import re
from collections import namedtuple, OrderedDict

import jsonschema

import fastr
from fastr.core.baseplugin import PluginState
import fastr.core.target
import fastr.exceptions as exceptions
from fastr.core.serializable import Serializable
from fastr.core.version import Version
from fastr.utils.checksum import hashsum

try:
    from fastr.execution.environmentmodules import EnvironmentModules
    ENVIRONMENT_MODULES = EnvironmentModules(fastr.config.protected_modules)
    ENVIRONMENT_MODULES_LOADED = True
except exceptions.FastrValueError:
    ENVIRONMENT_MODULES_LOADED = False

from fastr.utils.dicteq import diffdict


class Tool(Serializable):
    """
    The class encapsulating a tool.
    """

    __dataschemafile__ = 'Tool.schema.json'

    test_spec = namedtuple('TestSpecification', ['input', 'command', 'output'])

    def __init__(self, doc=None):
        """
        Create a new Tool
        :param doc: path of toolfile or a dict containing the tool data
        :type doc: str or dict
        """

        # Cache value for target binary
        self._target = None

        if doc is None:
            return

        filename = None
        if not isinstance(doc, dict):
            fastr.log.debug('Trying to load file: {}'.format(doc))
            filename = os.path.expanduser(doc)
            filename = os.path.abspath(filename)
            doc = self._loadf(filename)

        # Check if the doc is a valid Tool structure
        try:
            # __unserializer__ is supplied by the serializable meta-class
            # pylint: disable=no-member
            doc = Tool.get_serializer().instantiate(doc)
        except jsonschema.ValidationError:
            fastr.log.error('Could not validate Tool data again the schema!')
            raise
        else:
            fastr.log.debug('Tool schema validated!')

        # Get attributes from root node
        self.filename = filename

        #: Identifier for the tool
        regex = r'^[A-Z][\w\d_]*$'
        if re.match(regex, doc['id']) is None:
            message = 'A tool id in Fastr should be UpperCamelCase as enforced' \
                      ' by regular expression {} (found {})'.format(regex, doc['id'])
            fastr.log.warning(message)

        self.id = doc['id']

        #: The namespace this tools lives in, this will be set by the ToolManager on load
        self.namespace = None

        #: Name of the tool, this should be a descriptive, human readable name.
        self.name = doc.get('name', self.id)

        #: Version of the tool, not of the underlying software
        self.version = Version(str(doc.get('version')))

        #: Class for of the Node to use
        self.node_class = doc.get('class', 'Node')

        if self.id is None or self.name is None or self.version is None:
            raise exceptions.FastrValueError('Tool should contain an id, name and version!')

        #: URL to website where this tool can be downloaded from
        self.url = doc.get('url', '')

        #: Description of the tool and it's functionality
        self.description = doc.get('description', '')

        #: List of authors of the tool. These people wrapped the executable but
        #: are not responsible for executable itself.
        self.authors = doc['authors']

        #: List of tags for this tool
        self.tags = doc.get('tags', [])

        # Parse references field and format them into a dictionary
        #: A list of documents and in depth reading about the methods used in this tool
        self.references = doc.get('references', [])

        #: Requirements for this Tool
        #:
        #: .. warning:: Not yet implemented
        self.requirements = None

        #: Test for this tool. A test should be a collection of inputs, parameters
        #: and outputs to verify the proper functioning of the Tool.
        #:
        #: The format of the tests is a list of namedtuples, that have 3 fields:
        #: - input: a dict of the input data
        #: - command: a list given the expected command-line arguments
        #: - output: a dict of the output data to validate
        #:
        #: .. warning:: Not yet implemented

        self.tests = [self.test_spec(**x) for x in doc['tests']]

        command = doc['command']

        # Find commands
        #: Command is a dictionary contain information about the command which is
        #: called by this Tool:
        #: command['interpreter'] holds the (possible) interpreter to use
        #: command['targets'] holds a per os/arch dictionary of files that should be executed
        #: command['url'] is the webpage of the command to be called
        #: command['version'] is the version of the command used
        #: command['description'] can help a description of the command
        #: command['authors'] lists the original authors of the command
        self.command = {
            'targets': command['targets'],
            'license': command.get('license', ''),
            'url': command.get('url', ''),
            'version': Version(str(command.get('version'))),
            'description': command.get('description', ''),
            'authors': command.get('authors', [])
        }

        if len(self.command['targets']) == 0:
            raise exceptions.FastrValueError("No targets defined in tool description.")

        #: This holds the citation you should use when publishing something based on this Tool
        self.cite = doc['cite']

        #: Man page for the Tool. Here usage and examples can be described in detail
        self.help = doc['help']

        #: Create the Interface based on the class specified in the tool file
        interface_class = fastr.interfaces[doc['interface'].get('class', 'FastrInterface')]

        if interface_class.status != PluginState.loaded:
            raise exceptions.FastrPluginNotLoaded('Required InterfacePlugin {} was not loaded properly (status {})'.format(interface_class.id,
                                                                                                                           interface_class.status))

        self.interface = interface_class(id_='{}_{}_interface'.format(self.id, self.command['version']), document=doc['interface'])

    @property
    def hash(self):
        return hashsum(self.__getstate__())

    @property
    def ns_id(self):
        """
        The namespace and id of the Tool
        """
        if self.namespace is None:
            return self.id
        else:
            return '{}.{}'.format(self.namespace, self.id)
    @property
    def fullid(self):
        """
        The full id of this tool
        """
        return 'fastr:///tools/{}/{}'.format(self.ns_id, self.version)

    @property
    def inputs(self):
        return self.interface.inputs

    @property
    def outputs(self):
        return self.interface.outputs

    @property
    def target(self):
        """
        The OS and arch matched target definition.
        """
        if self._target is not None:
            return self._target

        # Get platform and os
        arch = platform.architecture()[0].lower()
        os_ = platform.system().lower()

        matching_targets = [x for x in self.command['targets'] if x['os'] in [os_, '*'] and x['arch'] in [arch, '*']]

        if len(matching_targets) == 0:
            return None
        elif len(matching_targets) == 1:
            target = matching_targets[0]
        else:
            # This should give the optimal match
            for match in matching_targets:
                match['score'] = 0

                if match['os'] == os_:
                    match['score'] += 2

                if match['arch'] == arch:
                    match['score'] += 1

            matching_targets = sorted(matching_targets, reverse=True, key=lambda x: x['score'])
            fastr.log.debug('Sorted matches: {}'.format(matching_targets))
            target = matching_targets[0]

        cls = target.get('class', 'LocalBinaryTarget')
        if hasattr(fastr.core.target, cls):
            cls = getattr(fastr.core.target, cls)
        else:
            raise exceptions.FastrValueError('Cannot find target {}'.format(cls))

        # Create target from curdir
        old_curdir = os.path.abspath(os.curdir)
        os.chdir(self.path)

        # Check if the argument binary exists
        if 'binary' not in target:
            if 'bin' in target:
                target['binary'] = target['bin']
                del target['bin']
            else:
                fastr.exceptions.FastrValueError('Target does not contain required "binary" (or "bin") argument')

        self._target = cls(**target)
        os.chdir(old_curdir)

        return self._target

    def execute(self, payload=None, **kwargs):
        """
        Execute a Tool given the payload for a single run

        :param payload: the data to execute the Tool with
        :returns: The result of the execution
        :rtype: InterFaceResult
        """
        # Allow kwargs to be used instead of payload
        if payload is None:
            payload = {'inputs': {}, 'outputs': {}}
            for key, value in kwargs.items():
                if key in self.inputs and key in self.outputs:
                    raise exceptions.FastrValueError('Cannot figure out if "{}" is an input or output, please prefix with input_/output_ as needed')
                elif key in self.inputs:
                    payload['inputs'][key] = value
                elif key in self.outputs:
                    payload['outputs'][key] = value
                elif key.startswith('input_') and key[6:] in self.inputs:
                    payload['inputs'][key[6:]] = value
                elif key.startswith('output_') and key[7:] in self.outputs:
                    payload['outputs'][key[7:]] = value
                else:
                    raise exceptions.FastrValueError('Cannot match key "{}" to any input/output!'.format(key))

        # Make sure all values are wrapped in a tuple (for single values)
        for key, value in payload['inputs'].items():
            if not isinstance(value, (tuple, OrderedDict)):
                payload['inputs'][key] = (value,)
        for key, value in payload['outputs'].items():
            if not isinstance(value, (tuple, OrderedDict)):
                payload['outputs'][key] = (value,)

        target = self.target
        fastr.log.info('Target is {}'.format(target))

        if target is None:
            arch = platform.architecture()[0].lower()
            os_ = platform.system().lower()
            raise exceptions.FastrValueError('Cannot find a viable target for {}/{} on {} ({} bit)'.format(self.id, self.version, os_, arch))

        fastr.log.info('Using payload: {}'.format(payload))
        with target:
            result = self.interface.execute(target, payload)

        return result

    def __str__(self):
        """
        Get a string version for the Tool

        :return: the string version
        :rtype: str
        """
        return '<Tool: {} version: {}>'.format(self.id, self.version)

    def __repr__(self):
        """
        Get a string representation for the Tool. This will show the inputs
        and output defined in a table-like structure.

        :return: the string representation
        :rtype: str
        """
        if self.name is not None and len(self.name) > 0:
            name_part = ' ({})'.format(self.name)
        else:
            name_part = ''

        return_list = ["Tool {} v{}{}".format(self.id, str(self.command['version']), name_part)]

        # The "+ [8]" guarantees a minimum of 8 width and avoids empty lists
        width_input_keys = max([len(x.id) for x in self.inputs.values()] + [8])
        width_input_types = max([len(x.datatype) for x in self.inputs.values()] + [8]) + 2
        width_output_keys = max([len(x.id) for x in self.outputs.values()] + [8])
        width_output_types = max([len(x.datatype) for x in self.outputs.values()] + [8]) + 2

        return_list.append('{:^{}}  | {:^{}}'.format('Inputs', width_input_types + width_input_keys + 1,
                                                     'Outputs', width_output_types + width_output_keys + 1))
        return_list.append('-' * (width_input_keys + width_input_types + width_output_keys + width_output_types + 7))
        for input_, output in itertools.izip_longest(self.inputs.values(), self.outputs.values()):
            if input_ is None:
                input_id = ''
                input_type = ''
            else:
                input_id = input_.id
                input_type = '({})'.format(input_.datatype)

            if output is None:
                output_id = ''
                output_type = ''
            else:
                output_id = output.id
                output_type = '({})'.format(output.datatype)

            return_list.append('{:{}} {:{}}  |  {:{}} {:{}}'.format(input_id, width_input_keys,
                                                                    input_type, width_input_types,
                                                                    output_id, width_output_keys,
                                                                    output_type, width_output_types))

        return '\n'.join(return_list)

    def __eq__(self, other):
        """Compare two Tool instances with each other.

        :param other: the other instances to compare to
        :type other: Tool
        :returns: True if equal, False otherwise
        """
        if not isinstance(other, Tool):
            return NotImplemented

        dict_self = dict(self.__dict__)
        del dict_self['_target']

        dict_other = dict(other.__dict__)
        del dict_other['_target']

        return dict_self == dict_other

    def __getstate__(self):
        """
        Retrieve the state of the Tool

        :return: the state of the object
        :rtype dict:
        """
        state = {k: v for k, v in self.__dict__.items()}
        state['command'] = {k: v for k, v in self.command.items()}

        state['tests'] = [dict(vars(x)) for x in state['tests']]
        state['class'] = state['node_class']
        state['interface'] = self.interface.__getstate__()
        state['command']['version'] = str(self.command['version'])
        state['version'] = str(self.version)
        del state['node_class']
        del state['_target']

        return state

    def __setstate__(self, state):
        """
        Set the state of the Tool by the given state.

        :param dict state: The state to populate the object with
        """
        if 'filename' not in state:
            state['filename'] = None

        state['version'] = Version(state['version'])
        state['command']['version'] = Version(str(state['command']['version']))

        state['tests'] = [self.test_spec(**x) for x in state['tests']]
        state['node_class'] = state['class']
        del state['class']

        interface_class = fastr.interfaces[state['interface'].get('class', 'FastrInterface')]
        if 'id' not in state['interface']:
            state['interface']['id'] = '{}_{}_interface'.format(state['id'], state['command']['version'])

        if interface_class.status != PluginState.loaded:
            raise exceptions.FastrPluginNotLoaded('Required InterfacePlugin {} was not loaded properly (status {})'.format(interface_class.id,
                                                                                                                           interface_class.status))

        state['interface'] = interface_class.createobj(state['interface'])
        self.__dict__.update(state)
        self._target = None

        # TODO: set interface link

    @property
    def path(self):
        """
        The path of the directory in which the tool definition file was
        located.
        """
        return os.path.dirname(self.filename)

    @property
    def command_version(self):
        return self.command['version']

    def test(self):
        """
        Run the tests for this tool
        """
        for test in self.tests:
            self._test(test)

    def _test(self, test):
        """
        Run a single test for this tool

        :param test: the test to run
        """
        # Get data for the test
        print('Self filename: {}'.format(self.filename))
        print('Self path: {}'.format(self.path))
        test_input = {k: tuple(os.path.join(self.path, 'testdata', 'input', x) for x in v) for k, v in test.input.items()}
        test_command = test.command
        test_output = {k: tuple(os.path.join(self.path, 'testdata', 'output', x) for x in v) for k, v in test.output.items()}

        fastr.log.info("Test Input: {}".format(test_input))
        fastr.log.info("Test Command: {}".format(test_command))
        fastr.log.info("Test Input: {}".format(test_output))

