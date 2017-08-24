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

"""
Network module containing Network facilitators and analysers.
"""
import datetime
import functools
import json
import os
import re
import subprocess
import sys
import time
import urlparse
import uuid
import pprint
import traceback
import shutil

from collections import OrderedDict
from tempfile import mkdtemp
from threading import Event, Lock, RLock

import requests

import fastr
from fastr.core.link import Link
from fastr.core.node import Node, ConstantNode, SourceNode, SinkNode, MacroNode
from fastr.core.inputoutput import Output
from fastr.core.samples import SampleItem
from fastr.core.serializable import Serializable
from fastr.core.version import Version
from fastr.data import url
import fastr.exceptions as exceptions
from fastr.execution.networkchunker import DefaultNetworkChunker
from fastr.execution.networkanalyzer import DefaultNetworkAnalyzer
from fastr.execution.job import JobState
from fastr.utils import iohelpers, pim_publisher


class Network(Serializable):
    """
    The Network class represents a workflow. This includes all Nodes (including ConstantNodes, SourceNodes and Sinks) and
    Links.
    """

    __dataschemafile__ = 'Network.schema.json'

    NETWORK_DUMP_FILE_NAME = '__fastr_network__.json'
    SOURCE_DUMP_FILE_NAME = '__source_data__.pickle.gz'
    SINK_DUMP_FILE_NAME = '__sink_data__.json'

    def __init__(self, id_='unnamed_network', version=None):
        """
        Create a new, empty Network

        :param str name: name of the Network
        :return: newly created Network
        :raises OSError: if the tmp mount in the config is not a writable directory
        """

        regex = r'^\w[\w\d_]*$'
        if re.match(regex, id_) is None:
            raise exceptions.FastrValueError('An id in Fastr should follow'
                                             ' the following pattern {}'
                                             ' (found {})'.format(regex, id_))

        if version is None:
            version = '0.0'

        #: The namespace this network lives in, this will be set by the NetworkManager on load
        self.namespace = None

        self._id = id_
        self.version = Version(version)
        self.description = ''
        self.toolnodelist = {}
        self.nodelist = {}
        self.sinklist = {}
        self.constantlist = {}
        self.sourcelist = {}
        self.macrolist = {}
        self.linklist = {}
        self.preferred_types = []
        self.stepids = {}
        self.nodegroups = {}
        self.link_number = 0
        self.node_number = 0
        self.callback_edit_lock = Lock()
        self.executing = False
        self.execution_lock = Event()
        self.execution_lock.set()
        self.edit_lock = RLock()

        self.job_finished_callback = None
        self.job_status_callback = None

        self.filename = None
        self.sink_results = {}

        # Info about the execution run (should be moved to NetworkRun in the future)
        self.timestamp = None
        self.uuid = None
        self.tmpdir = None
        self.tmpurl = None

        # Check if temp dir exists, if not try to create it
        if not os.path.exists(fastr.config.mounts['tmp']):
            fastr.log.info("fast temporary directory does not exists, creating it...")
            try:
                os.mkdir(fastr.config.mounts['tmp'])
            except OSError:
                message = "Could not create fastr temporary directory ({})".format(fastr.config.mounts['tmp'])
                fastr.log.critical(message)
                raise exceptions.FastrOSError(message)

        fastr.log.info('Changing fastr.current network to "{}"'.format(self.id))
        fastr.current_network = self

    def __repr__(self):
        return '<Network {} (v{})>'.format(self.id, self.version)

    def __eq__(self, other):
        """
        Compare two Networks and see if they are equal.

        :param other:
        :type other: :py:class:`Network <fastr.core.network.Network>`
        :return: flag indicating that the Networks are the same
        :rtype: bool
        """
        if not isinstance(other, Network):
            return NotImplemented

        dict_self = {k: v for k, v in self.__dict__.items()}
        del dict_self['callback_edit_lock']
        del dict_self['execution_lock']
        del dict_self['edit_lock']
        del dict_self['job_finished_callback']
        del dict_self['job_status_callback']
        del dict_self['tmpdir']
        del dict_self['tmpurl']
        del dict_self['nodelist']
        del dict_self['uuid']
        del dict_self['timestamp']
        del dict_self['filename']
        del dict_self['sink_results']

        dict_other = {k: v for k, v in other.__dict__.items()}
        del dict_other['callback_edit_lock']
        del dict_other['execution_lock']
        del dict_other['edit_lock']
        del dict_other['job_finished_callback']
        del dict_other['job_status_callback']
        del dict_other['tmpdir']
        del dict_other['tmpurl']
        del dict_other['nodelist']
        del dict_other['uuid']
        del dict_other['timestamp']
        del dict_other['filename']
        del dict_other['sink_results']

        return dict_self == dict_other

    def __ne__(self, other):
        """
        Tests for non-equality, this is the negated version __eq__
        """
        return not (self.__eq__(other))

    # Retrieve a Node/Link/Input/Output in the network based on the fullid
    def __getitem__(self, item):
        """
        Get an item by its fullid. The fullid can point to a link, node, input, output or even subinput/suboutput.

        :param str,unicode item: fullid of the item to retrieve
        :return: the requested item
        """
        if not isinstance(item, (str, unicode)):
            raise exceptions.FastrTypeError('Key should be a fullid string, found a {}'.format(type(item).__name__))

        parsed = urlparse.urlparse(item)
        if parsed.scheme != 'fastr':
            raise exceptions.FastrValueError('Item should be an URL with the fastr:// scheme (Found {} in {})'.format(parsed.scheme, item))

        path = parsed.path.split('/')[1:]

        if len(path) < 2 or path[0] != 'networks' or path[1] != self.id:
            raise exceptions.FastrValueError('URL {} does not point to anything in this network, {}'.format(item, path))

        value = self

        for part in path[2:]:
            if hasattr(value, '__getitem__'):
                try:
                    if isinstance(value, (list, tuple, Output)):
                        value = value[int(part)]
                    else:
                        value = value[part]
                except (KeyError, IndexError, TypeError, ValueError):
                    pass
                else:
                    continue

            if hasattr(value, part):
                value = getattr(value, part)
            else:
                raise exceptions.FastrLookupError('Could not find {} in {}'.format(part, value))

        return value

    def __getstate__(self):
        """
        Retrieve the state of the Network

        :return: the state of the object
        :rtype dict:
        """
        state = {
            'id': self.id,
            'version': str(self.version),
            'filename': self.filename,
            'description': self.description,
            'link_number': self.link_number,
            'node_number': self.node_number,
            'nodelist': [x.__getstate__() for x in self.nodelist.values()],
            'linklist': [x.__getstate__() for x in self.linklist.values()],
            'preferred_types': [x.id for x in self.preferred_types],
            'stepids': {k: [x.id for x in v] for k, v in self.stepids.items()},
            'nodegroups': self.nodegroups,
            'namespace': self.namespace
        }

        return state

    def __setstate__(self, state):
        """
        Set the state of the Network by the given state. This completely
        overwrites the old state!

        :param dict state: The state to populate the object with
        :return: None
        """
        # Initialize empty to avoid errors further on
        self._id = state['id']
        self.version = Version(state['version'])
        self.nodelist = {}
        self.linklist = {}
        self.macrolist = {}
        self.sourcelist = {}
        self.constantlist = {}
        self.sinklist = {}
        self.toolnodelist = {}
        self.preferred_types = []
        self.stepids = {}
        self.callback_edit_lock = Lock()
        self.execution_lock = Event()
        self.execution_lock.set()
        self.executing = False
        self.edit_lock = RLock()

        # There are run dependent, and can safely be lost during serialization
        self.job_finished_callback = None
        self.job_status_callback = None

        self.tmpdir = None
        self.tmpurl = None
        self.description = state['description']
        self.nodegroups = state['nodegroups']
        self.sink_results = {}

        # Info about the execution run (should be moved to NetworkRun in the future)
        self.timestamp = None
        self.uuid = None

        # Make proper version
        state['version'] = Version(state['version'])

        # Make sure the locks exist
        if not hasattr(self, 'callback_edit_lock'):
            self.callback_edit_lock = Lock()
        if not hasattr(self, 'execution_lock'):
            self.execution_lock = Event()
            self.execution_lock.set()
        if not hasattr(self, 'edit_lock'):
            self.edit_lock = RLock()

        # Set self as current network for links etc to be created properly
        fastr.current_network = self

        # Set ID, we need this for messages later on
        self._id = state['id']
        del state['id']

        # These should not be shared between Networks
        state.pop('callback_edit_lock', None)
        state.pop('execution_lock', None)
        state.pop('edit_lock', None)

        # Recreate nodes
        if 'nodelist' in state:
            for node_state in state['nodelist']:
                # Get the node class
                node_class = node_state.get('class', 'Node')
                node_class = getattr(fastr.core.node, node_class)

                node = node_class.createobj(node_state, self)
                fastr.log.debug('Adding node: {}'.format(node))
                self.add_node(node)
            del state['nodelist']

        # Add preferred types
        state['preferred_types'] = [fastr.typelist[x] for x in state['preferred_types']]

        # Insert empty link_list
        statelinklist = state['linklist']
        state['linklist'] = {}

        # Update the objects dict
        self.__dict__.update(state)

        # Create the link list, make sure all Nodes are in place first
        for link in statelinklist:
            self.linklist[link['id']] = Link.createobj(link, self)

        # Make the stepids reference the Node instead of using ids
        if self.stepids is None:
            self.stepids = {}
        self.stepids = {k: [self.nodelist[x] for x in v] for k, v in self.stepids.items()}

        self.node_number = state['node_number']
        self.link_number = state['link_number']

    @property
    def id(self):
        """
        The id of the Network. This is a read only property.
        """
        return self._id

    @property
    def fullid(self):
        """
        The fullid of the Network
        """
        return 'fastr:///networks/{}'.format(self.id)

    @property
    def run_id(self):
        """
        The run id of the network
        """
        return '{}_{}'.format(self.id, self.timestamp.strftime('%Y_%m_%d_%H_%M_%S_%f'))

    def add_node(self, node):
        """
        Add a Node to the Network. Make sure the node is in the node list and
        the node parent is set to this Network

        :param node: node to add
        :type node: :py:class:`Node <fastr.core.node.Node>`
        :raises FastrTypeError: if node is incorrectly typed
        """
        # Make sure we are not in the executing state
        if not self.execution_lock.wait(timeout=0):
            message = 'this network is being executed, cannot edit it during the execution'
            fastr.log.warning(message)
            return

        # Acquire the edit lock
        self.edit_lock.acquire()

        if node.id not in self.nodelist and isinstance(node, Node):
            self.nodelist[node.id] = node

            # Automatically sort Nodes in the right dict
            if isinstance(node, ConstantNode):
                self.constantlist[node.id] = node
            elif isinstance(node, SourceNode):
                self.sourcelist[node.id] = node
            elif isinstance(node, SinkNode):
                self.sinklist[node.id] = node
            elif isinstance(node, MacroNode):
                self.macrolist[node.id] = node
            elif isinstance(node, Node):
                self.toolnodelist[node.id] = node
            else:
                raise exceptions.FastrTypeError('Unknown Node type encountered! (type {})'.format(type(node).__name__))

            node.parent = self

        # Release the edit lock
        self.edit_lock.release()

    def add_link(self, link):
        """
        Add a Link to the Network. Make sure the link is in the link list and
        the link parent is set to this Network

        :param link: link to add
        :type link: :py:class:`Link <fastr.core.link.Link>`
        :raises FastrTypeError: if link is incorrectly typed
        :raises FastrNetworkMismatchError: if the link already belongs to another Network
        """

        if not isinstance(link, Link):
            raise exceptions.FastrTypeError('Link argument is not of Link class! (type {})'.format(type(link).__name__))

        # Make sure we are not in the executing state
        if not self.execution_lock.wait(timeout=0):
            message = 'this network is being executed, cannot edit it during the execution'
            fastr.log.warning(message)
            return

        # Acquire the edit lock
        self.edit_lock.acquire()

        if link.id not in self.linklist:
            if link.parent is None:
                # Make sure parent and network have mutual understanding of the arrangement
                link.parent = self
            elif link.parent is not self:
                self.edit_lock.release()  # Release lock  before raising exception
                raise exceptions.FastrNetworkMismatchError('Cannot add a Link that already belongs to another Network!')

            self.linklist[link.id] = link

        # Release the edit lock
        self.edit_lock.release()

    def remove(self, value):
        """
        Remove an item from the Network.

        :param value: the item to remove
        :type value: :py:class:`Node <fastr.core.node.Node>` or
                      :py:class:`Link <fastr.core.link.Link>`
        """
        # Make sure we are not in the executing state
        if not self.execution_lock.wait(timeout=0):
            message = 'this network is being executed, cannot edit it during the execution'
            fastr.log.warning(message)
            return

        # Acquire the edit lock
        self.edit_lock.acquire()

        if isinstance(value, Link):
            self.linklist.pop(value.id)

        if isinstance(value, Node):
            self.nodelist.pop(value.id)

        # Release the edit lock
        self.edit_lock.release()

    def add_stepid(self, stepid, node):
        """
        Add a Node to a specific step id

        :param str stepid: the stepid that the node will be added to
        :param node: the node to add to the stepid
        :type node: :py:class:`Node <fastr.core.node.Node>`
        """
        # Make sure we are not in the executing state
        if not self.execution_lock.wait(timeout=0):
            message = 'this network is being executed, cannot edit it during the execution'
            fastr.log.warning(message)
            return

        # Acquire the edit lock
        self.edit_lock.acquire()

        if stepid is not None:
            if stepid in self.stepids:
                self.stepids[stepid] += [node]
            else:
                self.stepids[stepid] = [node]

        # Release the edit lock
        self.edit_lock.release()

    def check_id(self, id_):
        """
        Check if an id for an object is valid and unused in the Network. The
        method will always returns True if it does not raise an exception.

        :param str id_: the id to check
        :return: True
        :raises FastrValueError: if the id is not correctly formatted
        :raises FastrValueError: if the id is already in use
        """

        regex = r'^\w[\w\d_]*$'
        if re.match(regex, id_) is None:
            raise exceptions.FastrValueError('An id in Fastr should follow'
                                             ' the following pattern {}'
                                             ' (found {})'.format(regex, id_))

        if id_ in self.nodelist or id_ in self.linklist:
            raise exceptions.FastrValueError('The id {} is already in use in {}!'.format(id_, self.id))

        return True

    def create_node(self, tool, id_=None, stepid=None, cores=None, memory=None, walltime=None, nodegroup=None):
        """
        Create a Node in this Network. The Node will be automatically added to
        the Network.

        :param tool: The Tool to base the Node on
        :type tool: :py:class:`Tool <fastr.core.tool.Tool>`
        :param str id_: The id of the node to be created
        :param str stepid: The stepid to add the created node to
        :param str nodegroup: The group the node belongs to, this can be
                              important for FlowNodes and such, as they
                              will have matching dimension names.
        :return: the newly created node
        :rtype: :py:class:`Node <fastr.core.node.Node>`
        """
        # Make sure we are not in the executing state
        if not self.execution_lock.wait(timeout=0):
            message = 'this network is being executed, cannot edit it during the execution'
            fastr.log.warning(message)
            return

        # Acquire the edit lock
        self.edit_lock.acquire()

        # Create a node in the network
        if isinstance(tool, (str, tuple)):
            tool = fastr.toollist[tool]

        try:
            NodeType = getattr(fastr.core.node, tool.node_class)
        except AttributeError:
            raise exceptions.FastrValueError('The indicated node class {} cannot be found for Tool {}/{}'.format(tool.node_class, tool.id, tool.version))

        node = NodeType(tool, id_, self, cores=cores, memory=memory, walltime=walltime)
        self.add_node(node)
        self.add_stepid(stepid, node)
        if nodegroup is None:
            nodegroup = node.id

        if nodegroup not in self.nodegroups:
            self.nodegroups[nodegroup] = []
        self.nodegroups[nodegroup].append(node.id)

        # Release the edit lock
        self.edit_lock.release()

        return node

    def create_macro(self, network, id_=None):
        if not self.execution_lock.wait(timeout=0):
            message = 'this network is being executed, cannot edit it during the execution'
            fastr.log.warning(message)
            return
        self.edit_lock.acquire()
        node = MacroNode(network, id_, self)

        self.add_node(node)
        self.edit_lock.release()
        return node

    def create_constant(self, datatype, data, id_=None, stepid=None, nodegroup=None, sourcegroup=None):
        """
        Create a ConstantNode in this Network. The Node will be automatically added to
        the Network.

        :param datatype: The DataType of the constant node
        :type datatype: :py:class:`BaseDataType <fastr.core.datatypemanager.BaseDataType>`
        :param data: The data to hold in the constant node
        :type data: datatype or list of datatype
        :param str id_: The id of the constant node to be created
        :param str stepid: The stepid to add the created constant node to
        :param str nodegroup: The group the node belongs to, this can be
                              important for FlowNodes and such, as they
                              will have matching dimension names.
        :return: the newly created constant node
        :rtype: :py:class:`ConstantNode <fastr.core.node.ConstantNode>`
        """
        # Make sure we are not in the executing state
        if not self.execution_lock.wait(timeout=0):
            message = 'this network is being executed, cannot edit it during the execution'
            fastr.log.warning(message)
            return

        # Acquire the edit lock
        self.edit_lock.acquire()

        if not isinstance(data, (list, dict, OrderedDict)):
            data = [data]
        const_node = ConstantNode(datatype, data, id_)
        self.add_node(const_node)
        self.add_stepid(stepid, const_node)
        if nodegroup is None:
            if sourcegroup is None:
                nodegroup = const_node.id
            else:
                fastr.log.warning('[DEPRECATED] The sourcegroup kwarg of the'
                                  ' Network.create_source is deprecated and'
                                  ' replaced by the nodegroup kwarg. Please'
                                  ' use that kwarg instead, it will have the'
                                  ' same function')
                nodegroup = sourcegroup

        if nodegroup not in self.nodegroups:
            self.nodegroups[nodegroup] = []
        self.nodegroups[nodegroup].append(const_node.id)

        # Release the edit lock
        self.edit_lock.release()

        return const_node

    def create_link(self, source, target, id_=None, collapse=None, expand=None):
        """
        Create a link between two Nodes and add it to the current Network.

        :param source: the output that is the source of the link
        :type source: :py:class:`BaseOutput <fastr.core.inputoutput.BaseOutput>`
        :param target: the input that is the target of the link
        :type target: :py:class:`BaseInput <fastr.core.inputoutput.BaseInput>`
        :param str id_: the id of the link
        :return: the created link
        :type: :py:class:`Link <fastr.core.link.Link>`
        """
        # Make sure we are not in the executing state
        if not self.execution_lock.wait(timeout=0):
            message = 'this network is being executed, cannot edit it during the execution'
            fastr.log.warning(message)
            return

        # Acquire the edit lock
        self.edit_lock.acquire()

        link = Link(source, target, id_=id_, parent=self, collapse=collapse, expand=expand)
        self.add_link(link)

        # Release the edit lock
        self.edit_lock.release()

        return link

    def create_source(self, datatype, id_=None, stepid=None, nodegroup=None, sourcegroup=None):
        """
        Create a SourceNode in this Network. The Node will be automatically added to
        the Network.

        :param datatype: The DataType of the source source_node
        :type datatype: :py:class:`BaseDataType <fastr.core.datatypemanager.BaseDataType>`
        :param str id_: The id of the source source_node to be created
        :param str stepid: The stepid to add the created source source_node to
        :param str nodegroup: The group the node belongs to, this can be
                              important for FlowNodes and such, as they
                              will have matching dimension names.
        :param str sourcegroup: *DEPRECATED!* The nodegroup this SourceNode will be added to
        :return: the newly created source source_node
        :rtype: :py:class:`SourceNode <fastr.core.source_node.SourceNode>`
        """
        # Make sure we are not in the executing state
        if not self.execution_lock.wait(timeout=0):
            message = 'this network is being executed, cannot edit it during the execution'
            fastr.log.warning(message)
            return

        # Acquire the edit lock
        self.edit_lock.acquire()

        # Set a source for the network.
        source_node = SourceNode(datatype=datatype, id_=id_)
        self.add_node(source_node)
        self.add_stepid(stepid, source_node)

        if nodegroup is None:
            if sourcegroup is None:
                nodegroup = source_node.id
            else:
                fastr.log.warning('[DEPRECATED] The sourcegroup kwarg of the'
                                  ' Network.create_source is deprecated and'
                                  ' replaced by the nodegroup kwarg. Please'
                                  ' use that kwarg instead, it will have the'
                                  ' same function')
                nodegroup = sourcegroup

        if nodegroup not in self.nodegroups:
            self.nodegroups[nodegroup] = []
        self.nodegroups[nodegroup].append(source_node.id)

        # Release the edit lock
        self.edit_lock.release()

        return source_node

    def create_sink(self, datatype, id_=None, stepid=None):
        """
        Create a SinkNode in this Network. The Node will be automatically added to
        the Network.

        :param datatype: The DataType of the sink node
        :type datatype: :py:class:`BaseDataType <fastr.core.datatypemanager.BaseDataType>`
        :param str id_: The id of the sink node to be created
        :param str stepid: The stepid to add the created sink node to
        :return: the newly created sink node
        :rtype: :py:class:`SinkNode <fastr.core.node.SinkNode>`
        """
        # Make sure we are not in the executing state
        if not self.execution_lock.wait(timeout=0):
            message = 'this network is being executed, cannot edit it during the execution'
            fastr.log.warning(message)
            return

        # Acquire the edit lock
        self.edit_lock.acquire()

        # Set a sink for the network
        node = SinkNode(datatype=datatype, id_=id_)
        self.add_node(node)
        self.add_stepid(stepid, node)

        # Release the edit lock
        self.edit_lock.release()

        return node

    def create_reference(self, source_data, output_directory):
        # Create temporary output directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        output_url = fastr.vfs.path_to_url(output_directory, scheme='ref')
        fastr.log.info('Created temp result directory {}'.format(output_directory))
        network_temp_dir = os.path.join(output_directory, '__fastr_run_tmp__')

        # Save source data to reference dir
        iohelpers.save_gpickle(os.path.join(output_directory, self.SOURCE_DUMP_FILE_NAME), source_data)

        # Save a dump of the network
        with open(os.path.join(output_directory, self.NETWORK_DUMP_FILE_NAME), 'w') as fh_out:
            self.dump(fh_out, method='json', indent=2)

        # Set the output sink data to temporary directory
        sink_data = {}
        for sink in self.sinklist.values():
            sink_data[sink.id] = '{}/{}/{{sample_id}}/{{cardinality}}/result.json'.format(
                output_url,
                sink.id
            )
        fastr.log.info('Set sink data to: {}'.format(sink_data))

        # Execute the network
        self.execute(sourcedata=source_data, sinkdata=sink_data, tmpdir=network_temp_dir)

    def test(self, reference_data_dir, source_data=None):
        """
        Execute the network with the source data specified and test the results
        against the refence data. This effectively tests the network execution.

        :param str reference_data_dir: The path or vfs url of reference data to compare with
        :param dict source_data: The source data to use
        """
        if not isinstance(reference_data_dir, basestring):
            raise exceptions.FastrTypeError('reference_data_dir should be a string!')

        if reference_data_dir.startswith('vfs://'):
            reference_data_dir = fastr.vfs.url_to_path(reference_data_dir)

        if not os.path.isdir(reference_data_dir):
            raise exceptions.FastrTypeError('The reference_data_dir should be pointing to an existing directory!')

        if source_data is None:
            source_data = iohelpers.load_gpickle(os.path.join(reference_data_dir, self.SOURCE_DUMP_FILE_NAME))

        temp_results_dir = None
        validation_result = True
        try:
            # Create temporary output directory
            temp_results_dir = os.path.normpath(mkdtemp(prefix='fastr_network_test_'.format(self.id), dir=fastr.config.mounts['tmp']))
            self.create_reference(source_data=source_data, output_directory=temp_results_dir)

            # Check all sinks results
            for sink in self.sinklist.values():
                sink_output_dir = os.path.join(temp_results_dir, sink.id)
                sink_reference_dir = os.path.join(reference_data_dir, sink.id)

                output_samples = sorted(os.listdir(sink_output_dir))
                reference_samples = sorted(os.listdir(sink_reference_dir))

                if output_samples != reference_samples:
                    fastr.log.info('Different samples found in sink "{}"'.format(sink.id))
                    fastr.log.info('Output samples: {}'.format(output_samples))
                    fastr.log.info('Reference samples: {}'.format(reference_samples))
                    validation_result = False
                    continue

                for sample in output_samples:
                    sample_output_dir = os.path.join(sink_output_dir, sample)
                    sample_reference_dir = os.path.join(sink_reference_dir, sample)

                    output_values = sorted(os.listdir(sample_output_dir))
                    reference_values = sorted(os.listdir(sample_reference_dir))

                    if output_values != reference_values:
                        fastr.log.info('Difference number of cardinality entries for {}/{}'.format(sink.id, sample))
                        fastr.log.info('Output cardinality entries: {}'.format(output_values))
                        fastr.log.info('Reference cardinality entries: {}'.format(reference_values))
                        validation_result = False
                        continue

                    for value in output_values:
                        with open(os.path.join(sample_output_dir, value, 'result.json')) as fh_in:
                            output_data = json.load(fh_in)
                        with open(os.path.join(sample_reference_dir, value, 'result.json')) as fh_in:
                            reference_data = json.load(fh_in)

                        output_item = fastr.typelist[output_data['datatype']](output_data['value'])
                        reference_item = fastr.typelist[reference_data['datatype']](reference_data['value'])

                        if output_item != reference_item:
                            fastr.log.info('Value for {}/{}/{} was not equal! (found "{}", expected "{}")'.format(
                                sink.id,
                                sample,
                                value,
                                output_item,
                                reference_item)
                            )

                            fastr.log.info('Output: [{}] {!r}'.format(type(output_item.value).__name__,
                                                                      output_item.value))
                            fastr.log.info('Reference: [{}] {!r}'.format(type(reference_item.value).__name__,
                                                                         reference_item.value))

                            validation_result = False

            if validation_result:
                fastr.log.info('Run and reference were equal! Test passed!')
            return validation_result
        finally:
            # Clean up
            fastr.log.info('Removing temp result directory {}'.format(temp_results_dir))
            if temp_results_dir is not None and os.path.isdir(temp_results_dir):
                shutil.rmtree(temp_results_dir, ignore_errors=True)

    def execute(self, sourcedata, sinkdata, execution_plugin=None, tmpdir=None, cluster_queue=None):
        """
        Execute the Network with the given data. This will analyze the Network,
        create jobs and send them to the execution backend of the system.

        :param dict sourcedata: dictionary containing all data for the sources
        :param dict sinkdata: dictionary containing directives for the sinks
        :param str execution_plugin: the execution plugin to use (None will use the config value)
        :raises FastrKeyError: if a source has not corresponding key in sourcedata
        :raises FastrKeyError: if a sink has not corresponding key in sinkdata
        """
        result = False

        self.timestamp = datetime.datetime.now()
        self.uuid = uuid.uuid1()

        with self.edit_lock:
            fastr.log.debug('Acquiring execution lock...')
            self.execution_lock.wait()
            self.execution_lock.clear()
            self.executing = True

            fastr.log.info("####################################")
            fastr.log.info("#     network execution STARTED    #")
            fastr.log.info("####################################")

            # Display the main file the Network is created from, if known it
            # is the network.filename, otherwise try to estimate the entry
            # point for the script used
            entry_file = self.filename

            if entry_file is None:
                for x in sys.argv[:2]:
                    if os.path.isfile(x):
                        entry_file = x
                        break

            # If there is no entry_file or the first argument is ipython or
            # bpython we assume that is not a network but via prompt
            if entry_file is not None and not entry_file.endswith((os.path.sep + "ipython",
                                                                   os.path.sep + "bpython")):
                entry_file = os.path.abspath(entry_file)
                entry_file_date = time.ctime(os.path.getmtime(entry_file))
                message = 'Running network via {} (last modified {})'.format(entry_file, entry_file_date)
            else:
                if entry_file is not None:
                    entry_file = os.path.basename(entry_file)
                message = 'Running network via {} session'.format(entry_file or 'python')

            fastr.log.info(message)
            fastr.log.info('FASTR loaded from {}'.format(fastr.__file__))

            if tmpdir is None:
                tmpdir = os.path.normpath(mkdtemp(prefix='fastr_{}_'.format(self.id), dir=fastr.config.mounts['tmp']))
            else:
                if url.isurl(tmpdir):
                    if not tmpdir.startswith('vfs://'):
                        raise exceptions.FastrValueError('The tmpdir keyword argument should be a path or vfs:// url!')
                    tmpdir = fastr.vfs.url_to_path(tmpdir)

                if not os.path.exists(tmpdir):
                    os.makedirs(tmpdir)

            self.tmpdir = tmpdir
            self.tmpurl = fastr.vfs.path_to_url(self.tmpdir)
            fastr.log.info('Network run tmpdir: {}'.format(self.tmpdir))

            network_file = os.path.join(self.tmpdir, self.NETWORK_DUMP_FILE_NAME)
            self.dumpf(network_file, method='json', indent=2)

            # If needed, send network to PIM for registration
            pim_session = pim_publisher.PimPublisher()
            pim_session.pim_register_run(self)
            self.job_finished_callback = pim_session.pim_update_status
            self.job_status_callback = pim_session.pim_update_status

            try:
                # Set the source and sink data
                for id_, source in self.sourcelist.items():
                    if isinstance(source, ConstantNode):
                        source.set_data()
                    elif id_ in sourcedata:
                        source.set_data(sourcedata[id_])
                    else:
                        raise exceptions.FastrKeyError('Could not find source data for SourceNode {}!'.format(id_))

                    source.update()

                for id_, sink in self.sinklist.items():
                    if id_ not in sinkdata:
                        raise exceptions.FastrKeyError('Could not find sink data for SinkNode {}!'.format(id_))
                    sink.set_data(sinkdata[id_])

                # Create execution objects
                chuncker = DefaultNetworkChunker()
                analyzer = DefaultNetworkAnalyzer()

                # Create a network chuncker to Chunk the Network in executable blocks
                chunks = chuncker.chunck_network(self)
                fastr.log.debug('Found chunks: {}'.format(chunks))

                # Select desired server execution plugin and instantiate
                fastr.log.debug('Selecting {} as executor plugin'.format(fastr.config.execution_plugin))

                # Checlk what execution plugin to use
                if execution_plugin is None:
                    execution_plugin = fastr.config.execution_plugin

                if execution_plugin not in fastr.execution_plugins:
                    message = 'Selected non-existing execution plugin ({}), available plugins: {}'.format(execution_plugin,
                                                                                                          fastr.execution_plugins.keys())
                    fastr.log.error(message)
                    raise exceptions.FastrValueError(message)

                fastr.log.debug('Retrieving execution plugin ({})'.format(execution_plugin))
                execution_interface_type = fastr.execution_plugins[execution_plugin]
                fastr.log.debug('Creating exeuction interface')

                with execution_interface_type(self.job_finished, self.job_finished, self.job_status_callback) as execution_interface:
                    if cluster_queue is not None:
                        execution_interface.default_queue = cluster_queue
                    execution_interface._finished_callback = functools.partial(self.job_finished, execution_interface=execution_interface)
                    execution_interface._cancelled_callback = functools.partial(self.job_finished, execution_interface=execution_interface)

                    for chunk in chunks:
                        if not self.executing:
                            return

                        # Create a network analyzer to create the optimal execution order
                        executionlist = analyzer.analyze_network(self, chunk)

                        joblist = []
                        for node in executionlist:
                            joblist += node.execute()

                            if not self.executing:
                                return

                        fastr.log.debug('Joblist ID: {}'.format([j.id for j in joblist]))

                        # Only try to process chunks that actually have jobs...
                        if len(joblist) > 0:
                            # First queue all jobs that need to run
                            for job in joblist:
                                execution_interface.queue_job(job)

                                if not self.executing:
                                    return

                            fastr.log.info('Waiting for execution to finish...')
                            # Wait in chuncks of two seconds (hopefully this will allow ipython to update more regularly)
                            while len(execution_interface.job_dict) > 0:
                                sys.stdout.flush()
                                if not self.executing:
                                    return
                                time.sleep(1.0)

                        if not self.executing:
                            return

                        fastr.log.info('Chunk execution finished!')

                fastr.log.info("####################################")
                fastr.log.info("#    network execution FINISHED    #")
                fastr.log.info("####################################")
            finally:
                if not self.executing:
                    fastr.log.info("####################################")
                    fastr.log.info("#    network execution ABORTED     #")
                    fastr.log.info("####################################")

                # Make sure to unlock the Network
                fastr.log.debug('Releasing execution lock')
                self.executing = False
                self.execution_lock.set()

                fastr.log.debug('Releasing edit lock')

        fastr.log.info('===== RESULTS =====')
        result = True
        for sink_node, sink_data in sorted(self.sink_results.items()):
            fastr.log.info('---- {} ----'.format(sink_node))
            for sample_id, (job, failed_annotations) in sorted(sink_data.items()):
                fastr.log.info('{}[{}]: {}'.format(sink_node, sample_id, job.status))
                for error in failed_annotations:
                    fastr.log.info('* {e[0]} [{e[1]}]'.format(e=error))
                    result = False
        fastr.log.info('===================')

        sink_data_json = {
            sink_node: {
                str(sample_id): {
                    "status": str(job.status),
                    "errors": [list(str(e) for e in x) for x in failed_annotations],
                    "job_file": job.logfile,
                    "job_url": job.logurl,
                } for sample_id, (job, failed_annotations) in sink_data.items()
            } for sink_node, sink_data in self.sink_results.items()
        }

        sink_result_file = os.path.join(self.tmpdir, self.SINK_DUMP_FILE_NAME)
        with open(sink_result_file, 'w') as fh_out:
            json.dump(sink_data_json, fh_out, indent=2)

        return result

    def abort(self):
        self.executing = False

    def job_finished(self, job, execution_interface):
        """
        Call-back handler for when a job is finished. Will collect the results
        and handle blocking jobs. This function is automatically called when
        the execution plugin finished a job.

        :param job: the job that finished
        :type job: :py:class:`Job <fastr.execution.job.Job>`
        """
        # Find the connected Node
        node_id = job.node_id

        if self.id != job.network_id:
            fastr.log.warning('Jobid network name not matching name of network!'
                              ' ({} vs {})'.format(self.id, job.network_id))
        node = self.nodelist[node_id]

        # Collect earlier failed annotations
        failed_job_annotation = set()
        if not isinstance(node, SourceNode):
            for input_id, input_argument in job.input_arguments.items():
                if not isinstance(input_argument, SampleItem) and isinstance(node, SinkNode):
                    fastr.log.debug('Skipping sink system input: {}'.format(input_argument))
                    continue

                if not isinstance(input_argument, list):
                    input_argument = [input_argument]

                for input_argument_element in input_argument:
                    if str(input_argument_element.id) == '__EMPTY__':
                        continue

                    # Get the annotation from the input
                    fastr.log.debug('Getting annotation from {} --> {}'.format(node.inputs[input_id].get_sourced_outputs(),
                                                                               node.inputs[input_id][input_argument_element.index].failed_annotations))
                    item = node.inputs[input_id][input_argument_element.index]
                    failed_job_annotation.update(item.failed_annotations)

        # Log the status and add annotations if needed
        status_message = "Finished job {} with status {}".format(job.id, job.status)
        fastr.log.info(status_message)

        if job.status not in (JobState.finished, JobState.cancelled):
            if len(job.errors) > 0:
                error = job.errors[0]
                status_message = 'Encountered error: [{e[0]}] {e[1]} ({e[2]}:{e[3]})'.format(e=error)
            else:
                status_message = 'Encountered error in job {}'.format(job.id)

            failed_job_annotation.add((job.id, str(job.status), status_message))

        # Lock Network for editing, make sure not multiple threads will edit network data at the same time
        with self.callback_edit_lock:
            # Data is stored here, need to place it back in the Nodes
            node.set_result(job, failed_job_annotation)

        if self.job_finished_callback is not None:
            #  We will run a callback of which we do not know what it can
            # raise. Since we do not want to callback to crash we use a
            # bare except.
            # pylint: disable=bare-except
            try:
                self.job_finished_callback(job)
            except:
                fastr.log.error('Error in network job finished callback')
                fastr.log.error(traceback.format_exc())
        sys.stdout.flush()

    def is_valid(self):
        def check_object(obj):
            # obj.update()
            status = obj.status
            if not status['valid']:
                if status['messages']:
                    for message in status['messages']:
                        fastr.log.error(message)
                else:
                    fastr.log.error("{} {} is not valid, no message available!".format(type(obj).__name__, obj.id))
            return status['valid']

        valid = True
        for node in self.nodelist.itervalues():
            valid = valid & check_object(node)
        for link in self.linklist.itervalues():
            valid = valid & check_object(link)
        return valid

    def draw_network(self, name="network_layout", img_format='svg', draw_dimension=False):
        """
        Output a dot file and try to convert it to an image file.

        :param str img_format: extension of the image format to convert to
        :return: path of the image created or None if failed
        :rtype: str or None
        """
        allowed_img_formats = ['png', 'svg', 'pdf', 'ps', 'eps', 'gif', 'bmp', 'tif', 'jpg']
        dim_names = ['N', 'M', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        dim_names = dim_names + ["{}{}".format(a, b) for a in dim_names for b in dim_names]
        dim_names.reverse()
        dim = {}

        def lookup_dimname(name):
            if name in dim.keys():
                return dim[name]
            else:
                dim[name] = dim_names.pop()
                return dim[name]

        def format_dimname(dimnames):
            if len(dimnames) > 0:
                return " [{}] ".format("x".join([lookup_dimname(d) for d in dimnames]))
            else:
                return ""

        def print_constant_values(values):
            s = values
            for vi, value in enumerate(values):
                s[vi] = list(value)
                for ii, item in enumerate(value):
                    item = str(item)
                    s[vi][ii] = (item[:12] + '...' + item[-18:]) if len(item) > 33 else item
            return pprint.pformat(s).encode('string_escape')

        if img_format not in allowed_img_formats:
            # Default to svg.
            fastr.log.warning("Image format {} is not supported, falling back to svg".format(img_format))
            img_format = 'svg'

        sourceclr = 'darkolivegreen1'
        nodeclr = 'gray90'
        sinkclr = 'lightskyblue1'
        constantclr = 'plum1'

        dot_file = """digraph G {\n\trankdir = "LR"\n\tsplines=true;\n\tnode [ fontsize="16" shape="record" ];\n\n"""

        # Compile a sourcelist were the constantnodes are left out.
        sourcelist = {x: self.sourcelist[x] for x in self.sourcelist if x not in self.constantlist}

        nodes_in_clusters = []
        for stepid, nodes in self.stepids.items():
            dot_file += """\tsubgraph "cluster_{stepid}" {{\n\t\tlabel="{stepid}";\n\t\tcolor="gray60";\n""".format(stepid=stepid, )
            for node in nodes:
                nodes_in_clusters += [node.id]

                if node.id in sourcelist:
                    clr = sourceclr
                elif node.id in self.constantlist:
                    clr = constantclr
                elif node.id in self.toolnodelist:
                    clr = nodeclr
                elif node.id in self.sinklist:
                    clr = sinkclr
                else:
                    clr = nodeclr

                if node.id in self.constantlist:
                    if draw_dimension:
                        dot_file += '\t\t"{id}" [ style=filled fillcolor={clr} label="<id>{id}|<output>{data} {dim}" ];\n'.format(id=node.id, clr=clr, data=print_constant_values(node.data.values()), dim=format_dimname(node.outputs['output'].dimnames))
                    else:
                        dot_file += '\t\t"{id}" [ style=filled fillcolor={clr} label="<id>{id}|<output>{data}" ];\n'.format(id=node.id, clr=clr, data=print_constant_values(node.data.values()))
                else:
                    if draw_dimension:
                        format_inputs = '|'.join(['<i_{k}>{dim}{k}'.format(k=k, dim=format_dimname(v.dimnames)) for k, v in node.inputs.items()])
                        format_outputs = '|'.join(['<o_{k}>{k}{dim}'.format(k=k, dim=(format_dimname(v.dimnames) if len(v.listeners) > 0 else "")) for k, v in node.outputs.items()])
                    else:
                        format_inputs = '|'.join(['<i_{i}>{i}'.format(i=i) for i in node.inputs.keys()])
                        format_outputs = '|'.join(['<o_{i}>{i}'.format(i=i) for i in node.outputs.keys()])
                    dot_file += '\t\t"{id}" [ style=filled fillcolor={clr} label="<id>{id}|{{{{{inputs}}}|{{{outputs}}}}}" ];\n'.format(id=node.id, clr=clr, inputs=format_inputs, outputs=format_outputs)
            dot_file += "\t}\n\n"

        for clr, lst in zip([sourceclr, constantclr, nodeclr, sinkclr], [sourcelist, self.constantlist, self.toolnodelist, self.sinklist]):
            for id_, node in lst.items():
                if id_ not in nodes_in_clusters:
                    if node.id in self.constantlist:
                        if draw_dimension:
                            dot_file += '\t"{id}" [ style=filled fillcolor={clr} label="<o_id>{id}|<output>{data} {dim}" ];\n'.format(id=node.id, clr=clr, data=print_constant_values(node.data.values()), dim=format_dimname(node.outputs['output'].dimnames))
                        else:
                            dot_file += '\t"{id}" [ style=filled fillcolor={clr} label="<o_id>{id}|<output>{data}" ];\n'.format(id=node.id, clr=clr, data=print_constant_values(node.data.values()))
                    else:
                        if draw_dimension:
                            format_inputs = '|'.join(['<i_{k}>{dim}{k}'.format(k=k, dim=format_dimname(v.dimnames)) for k, v in node.inputs.items()])
                            format_outputs = '|'.join(['<o_{k}>{k}{dim}'.format(k=k, dim=(format_dimname(v.dimnames) if len(v.listeners) > 0 else "")) for k, v in node.outputs.items()])
                        else:
                            format_inputs = '|'.join(['<i_{i}>{i}'.format(i=i) for i in node.inputs.keys()])
                            format_outputs = '|'.join(['<o_{i}>{i}'.format(i=i) for i in node.outputs.keys()])
                        dot_file += '\t"{}" [ style=filled fillcolor={} label="<id>{}|{{{{{inputs}}}|{{{outputs}}}}}" ];\n'.format(node.id, clr, node.id, inputs=format_inputs, outputs=format_outputs)
        for link in self.linklist.values():
            source_node_id = link.source.node.id
            source_output_id = link.source.id
            target_node_id = link.target.node.id
            target_input_id = link.target.id
            edge_properties = " ["
            if link.collapse and not link.expand:
                edge_properties += " color=blue weight=3 penwidth=3"
            elif link.expand and not link.collapse:
                edge_properties += " color=red weight=3 penwidth=3"
            elif link.expand and link.collapse:
                edge_properties += " color=purple weight=3 penwidth=3"
            edge_properties += "]"
            dot_file += '\t"{}":o_{} -> "{}":i_{}{props};\n'.format(source_node_id, source_output_id, target_node_id, target_input_id, props=edge_properties)
        dot_file += "}"

        dot_file_path = '{}.dot'.format(name)
        if os.path.isfile(dot_file_path):
            os.remove(dot_file_path)

        image_file_path = '{}.{}'.format(name, img_format)
        if os.path.exists(image_file_path):
            os.remove(image_file_path)
        with open(dot_file_path, 'wb') as output_file:
            output_file.write(dot_file)
        filename = os.path.join(os.getcwd(), '{}.dot'.format(name))
        fastr.log.debug("%s file created.", filename)
        try:
            proc = subprocess.Popen(['dot', '-T{}'.format(img_format), '-o{}'.format(image_file_path), dot_file_path],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            stdout, stderr = proc.communicate()
            fastr.log.debug('Subprocess call to do finished with stdout: {}, stderr: {}'.format(stdout, stderr))

            if not os.path.exists(image_file_path):
                fastr.log.error('Network draw failed the graphviz coversion:\n{}'.format(stdout))
            fastr.log.debug("converted to %s", image_file_path)
            return image_file_path
        except OSError:
            fastr.log.warning("Cannot convert %s to an svg image. Please put dot (from GraphViz) in your PATH.", filename)
            return None
