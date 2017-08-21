# Copyright 2017 The Regents of the University of California
#
# Licensed under the BSD-3-clause license (the "License"); you may not
# use this file except in compliance with the License.
# You are provided a copy of the license in LICENSE.md at the root of
# this project.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Metabolome analysis workflow."""

from __future__ import absolute_import

from . import operations as ops
from inquiry.framework.workflow import Workflow
from inquiry.framework import util
from inquiry.framework import task


class ConvertWorkflow(Workflow):
    """Convert Agilent .d files into mzML format using msconvert."""

    def __init__(self):
        """Initialize an msconvert workflow."""
        self.tag = 'msconvert-dtomzml'
        self.arg_template = {
            'archives': {
                'help': 'List of paths to compressed Agilent .d files.'
            }
        }
        self.meta = {
          "name": "msconvert",
          "description": "Convert Agilent .d files into mzML.",
          "parameters": [{
            "name": "archives",
            "label": "Archives list file",
            "help_text": "List of GCS paths to .d files.",
            "regexes": ["^gs:\/\/[^\n\r]+$"],
            "is_optional": False
          }]
        }
        super(ConvertWorkflow, self).__init__()

    def define(self):
        """Metabolome analysis workflow."""

        return (util.fc_create(self.p, self.args.archives)
                | task.ContainerTaskRunner(ops.MSConvert(self.args)))


class XCMSPreprocess(Workflow):
    """Convert .d files to mzml and preprocess with XCMS."""

    def __init__(self):
        """Initialize an msconvert workflow."""
        self.tag = 'xcms3-preprocess'
        self.arg_template = {
            'files': {
                'help': 'List of paths to files.'
            }
        }
        super(XCMSPreprocess, self).__init__()

    def define(self, p):
        """Metabolome analysis workflow."""
        # Hack ... so here we will want to map from a pcollection down
        # to a single array.
        inputs = util.create_file_set(p, [self.args.files])
        return ops.xcms_preprocess(inputs, self.args)


def run(config=None):
    """Run as a Dataflow."""
    ConvertWorkflow().run(config)
    #Preprocess().run(config)

if __name__ == '__main__':
    run(sys.argv[1])
