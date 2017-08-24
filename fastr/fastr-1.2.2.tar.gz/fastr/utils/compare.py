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
Module to compare various fastr specific things such as a execution directory
or a reference directory.
"""

import os

import fastr
from fastr import Network, SourceNode
from fastr.execution.job import Job
from fastr.execution.networkanalyzer import DefaultNetworkAnalyzer
from fastr.utils.iohelpers import load_gpickle


def compare_execution_dir(path1, path2):
    # Compare network dumps
    network_file1 = os.path.join(path1, Network.NETWORK_DUMP_FILE_NAME)
    network_file2 = os.path.join(path2, Network.NETWORK_DUMP_FILE_NAME)

    network1 = Network.loadf(network_file1)
    network2 = Network.loadf(network_file2)

    fastr.log.debug('Network1 filename: {}'.format(network1.filename))
    fastr.log.debug('Network2 filename: {}'.format(network2.filename))

    if network1 != network2:
        yield "Networks dumps are not equal!"
    else:
        del network2

    # Get the order of the Nodes
    analyzer = DefaultNetworkAnalyzer()
    execution_order = analyzer.analyze_network(
        network1,
        (None, network1.nodelist.values())
    )

    fastr.log.debug('Execution order: "{}"'.format(execution_order))

    # Compare node outputs in execution order
    for node in execution_order:
        fastr.log.debug('Checking node {}'.format(node.id))
        # Get the sample present
        node_dir1 = os.path.join(path1, node.id)
        node_dir2 = os.path.join(path2, node.id)

        if isinstance(node, SourceNode):
            # Possible source nodes do not exist
            if not os.path.isdir(node_dir1):
                if not os.path.isdir(node_dir2):
                    # Non-existing in both
                    continue
                else:
                    yield("Node '{}' does not have output for result 2")
                    continue
            elif not os.path.isdir(node_dir2):
                yield("Node '{}' does not have output for result 1")
                continue

        samples1 = set(os.listdir(node_dir1))
        samples2 = set(os.listdir(node_dir2))

        # Compare the samples
        if samples1 != samples2:
            yield ("Node '{}' contains different samples, set 1 exclusively"
                   " contains {} and set 2 exclusively contains {}").format(
                node.id,
                samples1.difference(samples2),
                samples2.difference(samples1)
            )

        # Inspect the individual samples that are in both sets
        for sample in sorted(samples1.intersection(samples2)):
            fastr.log.debug('Checking sample {}'.format(sample))
            result1 = os.path.join(node_dir1, sample, Job.RESULT_DUMP)
            result2 = os.path.join(node_dir2, sample, Job.RESULT_DUMP)

            job1 = load_gpickle(result1)
            job2 = load_gpickle(result2)

            # Compare output data
            fastr.log.debug('Job1 data: {}'.format(job1.output_data))
            fastr.log.debug('Job2 data: {}'.format(job2.output_data))
            if job1.output_data != job2.output_data:
                yield "Output data for job {} does not match".format(job1.id)
