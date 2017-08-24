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

import gzip
import json
# Try to import the faster cPickle if available and fall back when needed
try:
    import cPickle as pickle
except ImportError:
    import pickle
import os
import time

import fastr


def load_gpickle(path, retry_scheme=None):
    if retry_scheme is None:
        retry_scheme = (1, 3, 5)

    fastr.log.debug('Attempting to load {} with retry scheme {}'.format(path, retry_scheme))

    # Start with a non-delayed attempt
    retry_scheme = (0,) + tuple(retry_scheme)

    # Get the jobfile if given a job
    for attempt, delay in enumerate(retry_scheme):
        try:
            # Wait before trying to load the file
            fastr.log.debug('Attempt {} after {} seconds of delay'.format(attempt, delay))
            time.sleep(delay)

            try:
                with gzip.open(path, 'rb') as fh_in:
                    data = pickle.load(fh_in)
            except AttributeError as exception:
                # This is probably due to an Enum that is created on the fly
                # when a Tool is loaded
                fastr.log.warning('Cannot find attribute during unpickling,'
                                  ' this is probably an extension type that'
                                  'was created with an older fastr version, '
                                  'attempting to populate resources and try '
                                  'again. Original exception: {}'.format(exception))
                fastr.toollist.populate()
                with gzip.open(path, 'rb') as fh_in:
                    data = pickle.load(fh_in)

            return data
        except Exception as exception:
            pass

    raise exception


def save_gpickle(path, data):
    with gzip.open(path, 'wb') as fh_out:
        pickle.dump(data, fh_out)

        # Make sure the data gets flushed
        fh_out.flush()
        os.fsync(fh_out.fileno())


def save_json(path, data, indent=2):
    with open(path, 'w') as out_fh:
        json.dump(data, out_fh, indent=indent)


def load_json(path):
    with open(path, 'r') as in_fh:
        return json.load(in_fh)
