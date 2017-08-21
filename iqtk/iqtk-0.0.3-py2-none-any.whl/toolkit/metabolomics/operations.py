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
"""Metabolome analysis operations."""

import apache_beam as beam

import datetime
import pprint

import inquiry.framework as iqf
from inquiry.framework.util import localize

from inquiry.framework import task


def msconvert(p, args):
    """Wrapper to simplify use."""
    return p | iqf.task.ContainerTaskRunner(MSConvert(args=args))

def xcms_preprocess(p, args):
    """Wrapper to simplify use."""
    return p | iqf.task.ContainerTaskRunner(XCMSPreprocess(args=args))

class MSConvert(iqf.task.ContainerTask):

    def __init__(self, args):
        """Initialize an MSConvert container task."""
        container = iqf.task.ContainerTaskResources(
            disk=60, cpu_cores=4, ram=8,
            image='gcr.io/jbei-cloud/msconvert:0.0.1')
        super(MSConvert, self).__init__(task_label='msconvert', args=args,
                                        container=container)

    def process(self, file_path):

        # Declare intermediates
        decomp_target = self.out_path + '/decompressed'
        converted_name = 'converted-%s.mzML' % iqf.util.shaker.shake()
        converted_target = localize(converted_name, self.out_path)

        # Construct command
        cmd = iqf.util.Command(['mkdir', '-p', decomp_target])

        if file_path.endswith('.tar.gz') or file_path.endswith('.tgz'):
            cmd.chain(['tar', '-xzf', localize(file_path),
                       '-C', decomp_target, '--strip-components=1'])
            target = decomp_target
        else:
            target = localize(file_path)

        cmd.chain(["wine", "msconvert", target, "--zlib",
                   "-o", self.out_path])
        cmd.chain(["mv", self.out_path + "/*.mzML", converted_target])

        yield task.submit(self, cmd.txt, inputs=[file_path],
                          expected_outputs=[{'name': converted_name,
                                             'file_type': 'mzml'}])


def xcms_preprocess(p, args):
    return p | iqf.task.ContainerTaskRunner(XCMSPreprocess(args=args))


class RScriptCommand(iqf.util.Command):

    def __init__(self, out_path, script_body):
        salt = iqf.util.shaker.shake()
        out_dir = out_path
        self.out_path = out_path + '/' + salt + '.Rscript'
        self.script_body = script_body
        super(util.RScriptCommand, self).__init__()

        self.chain([
            'echo', '\"', self.script_body, '\"', '>', self.out_path
        ])
        self.chain(['cd', out_dir])
        self.chain(['Rscript', self.out_path])
        self.chain(['cat', self.out_path])
        self.chain(['cat', self.out_path + '.Rout'])

class XCMSPreprocess(iqf.task.ContainerTask):

    def __init__(self, args):
        """Initialize the XCMS contianer task."""
        container = iqf.task.ContainerTaskResources(
            image='gcr.io/jbei-cloud/xcms3:0.0.1',
            ram=8,
            disk=50
        )
        super(XCMSPreprocess, self).__init__(task_label='xcms_preprocess',
                                             args=args,
                                             container=container)

    def process(self, file_paths):
        rscript = RScriptCommand(out_path=self.out_path,
                                 script_body="""
library(xcms)
library(RColorBrewer)
register(SerialParam())
rm(list = setdiff(ls(), lsf.str()))

files = list.files('{input_path}',
                   recursive=TRUE,
                   pattern='mzML',
                   full.name=TRUE)
files

s_groups <- rep('ramos', length(files))
s_groups[grep(files, pattern = 'converted-9')] <- 'biolec'
s_groups

pheno <- data.frame(sample_name = sub(basename(files), pattern = '.mzML',
                                      replacement = '', fixed = TRUE),
                    sample_group = s_groups, stringsAsFactors = FALSE)
pheno

raw_data <- readMSData2(files, pdata = new('NAnnotatedDataFrame', pheno))

cwp <- CentWaveParam(snthresh = 20, noise = 1000)
xod <- findChromPeaks(raw_data, param = cwp)

## Doing the obiwarp alignment using the default settings.
xod <- adjustRtime(xod, param = ObiwarpParam())

proc.time()

                          """.format(**{
                              'input_path': self.input_path
                          }))

        yield task.submit(self, rscript.txt, inputs=file_paths,
                          expected_outputs=[{'name': '*.png'}])
