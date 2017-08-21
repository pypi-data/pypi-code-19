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
"""General argument handling utils"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import subprocess
import tempfile
import uuid
import inspect
import json
import sys

#import apache_beam as beam
#import re
#from inquiry import PROJECT_ROOT_PATH

# HACK supreme
PROJECT_ROOT_PATH = '/Users/cb/Desktop/release/iqtk'

import apache_beam as beam

LOGGING_LEVEL = 'INFO'


def _require_allowed_severity(severity):
    allowed = ["INFO", "DEBUG", "WARN", "ERROR"]
    if severity not in allowed:
        raise ValueError('Severity specified to logger must be one of '
                         '%s, saw %s.' % (allowed, severity))


class Logger(object):
    """Structured (cloud) logging utility."""

    def __init__(self, severity='INFO', tag=None, log_name='inquiry',
                 cloud=False, local=True):
        if tag is not None:
            log_name += '-%s' % tag

        _require_allowed_severity(severity)

        if local:
            import coloredlogs
            import logging
            iqtk_logger = logging.getLogger('iqtk')
            iqtk_logger.setLevel(getattr(logging, severity))
            coloredlogs.install(level=severity)
            self.local_logger = iqtk_logger

        self.severity = 'INFO'
        self.system_info = self._get_system_info()

    def _get_system_info(self):
        return {'python_version': sys.version_info[0]}

    def _add_issuer(self):
        self.message['issuer'] = sys._getframe(4).f_code.co_name
        self.message['issuer_parent'] = sys._getframe(5).f_code.co_name

    def debug(self, message):
        self._log(message, severity='DEBUG')

    def error(self, message):
        self._log(message, severity='ERROR')

    def info(self, message):
        self._log(message, severity='INFO')

    def _log(self, message, severity='INFO'):
        self._build_message(message)

        getattr(self.local_logger, severity.lower())(self.message)

    def _build_message(self, message):
        if message is None:
            self.message = {'text': None}
            self.message['system_info'] = self.system_info
            return
        if isinstance(message, unicode):
            message = str(message)

        # if not isinstance(message, dict) and not isinstance(message, str):
        #     raise ValueError('logger expects messages to be dictionary, '
        #                      'string objects, saw: %s, %s' % (type(message),
        #                                                       message))
        # if not isinstance(message, str):
        #     message = {'text': message}
        self.message = {'content': message}
        self._add_issuer()
        self.message['system_info'] = self.system_info

    def _show_locally(self, message):
        pp = pprint.PrettyPrinter(depth=4)
        pp.pprint(self.message)


class CalledProcessError(Exception):
    pass


def _subprocess(command):

    logging.debug('subprocess executing command: %s' % command)
    assert isinstance(command, str)

    with open(os.devnull, 'w') as dev_null:
        cmd = subprocess.Popen(command, shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        err = [thing for thing in cmd.stderr]
        out_raw, _ = cmd.communicate()

        if cmd.returncode is 1:
            CalledProcessError(err)

        out = out_raw.strip('\n').split('\n')
        return out


def safe_mkdir(path):
    if len(path.split(' ')) > 1:
        raise ValueError('path cannot have spaces: %s' % path)
    if not path.startswith('/tmp/iq'):
        raise ValueError('during development, in the interest of safety, mkdir '
                         'not prefixed with /tmp/iq is '
                         'not allowed. Saw: %s' % (path))
    _subprocess('mkdir %s' % path)
    return path


def default_project():
    with open(os.devnull, 'w') as dev_null:
        return subprocess.check_output(['gcloud', 'config', 'list', 'project',
                                        '--format=value(core.project)'],
                                       stderr=dev_null).strip()


def dump_reqs(requirements):
    """Given an array of requirements, write them to a temporary file."""
    f = tempfile.NamedTemporaryFile(delete=False)
    fname = f.name
    for req in requirements:
        f.write(req + '\n')
    f.close()
    return fname


def bundle(args):

    tmpdir = tempfile.mkdtemp()
    from inquiry import __VERSION__ as version
    bundle_name = '%s/inquiry-%s.tar.gz' % (tmpdir, version)
    bundle_sh_path = PROJECT_ROOT_PATH + '/tools/bundle.sh'
    #subprocess.check_call(['sh', bundle_sh_path, tmpdir])
    subprocess.check_call(['python', 'setup.py', 'sdist', '--format=gztar',
                            '--dist-dir=%s' % tmpdir])
    subprocess.check_call(['gsutil', '-q', 'cp', os.path.join('dist',
                                                              bundle_name),
                           args.output_dir + '/'])
    return bundle_name


def write_dev(data, output, tag):
    """Write text to output stem with tag."""
    data | 'write_%s' % tag >> beam.io.WriteToText(output + '/' + tag)


def write(data, output, tag):
    """Write text to output stem with tag."""
    out_path = output + '/' + tag
    data | 'write_%s' % tag >> beam.io.WriteToText(out_path)
    return out_path


def hash_lookup(record, h):
    """Map record:(key, value0), hash:(key, value1) to (value1, value0)."""
    if record[0] in h:
        yield (h[record[0]], record[1])


def unpack_csv_line(line, schema):
    out = {}
    arr = line.split(',')
    assert len(schema) == len(arr)
    for i, schema_field in enumerate(schema):
        out[schema_field] = arr[i]
    yield out


def read_text(p, source, tag, csv_schema=None):
    collection = (p | beam.io.Read('load_%s' % tag,
                                   beam.io.TextFileSource(source)))

    if csv_schema is not None:
        return collection | beam.FlatMap('unpack_csv_line_%s' % tag,
                                         unpack_csv_line, csv_schema)
    return collection


class SaltShaker(object):

    def __init__(self, n=1000):
        self.pool = []
        for i in range(n):
            s = str(uuid.uuid4())[:8]
            if s not in self.pool:
                self.pool.append(s)

    def shake(self):
        if len(self.pool) == 0:
            logging.error('rutro looks like you tried to .shake() from an '
                          'empty SaltShaker :...(')
            raise ValueError()
        ret = self.pool.pop()
        return ret

SALTSHAKER = SaltShaker()

def require_type(variable, ty, invert=False, extra_message=None):
    """Require a variable be of a specified type, otherwise ValueError.

    Args:
        variable (any): The variable whose type will be checked.
        required_type (str): The type that the variable is required to be.
        invert (bool): Whether to invert the type requirement (~must).

    TODO:
        * Expand to generate contextual ValueError and integrate logging so
            this can be easily used, and potentially later changed, throughout.
        * Enable error message to be extended with statement reflecting logical
            context.

    """
    if not isinstance(variable, ty):
        msg = {'text': 'requires variable of type %s, saw %s' % (ty,
                                                                 type(variable)
                                                                 )}
        logging.error(msg)
        raise ValueError(json.dumps(msg))


def require_len(variable, l, invert=False):
    """Require an object be of specified length and impl. have that notion.

    Args:
        variable (any): The variable to check
        l (int): The required length.

    Returns:
        bool: The return value. True for success, False otherwise.

    Todo:
        * For module TODOs

    .. _Google Python Style Guide:
       http://google.github.io/styleguide/pyguide.html
    """
    pass


def _unique_label(label, tag):

    require_type(label, str)

    if len(label) == 0:
        logging.error('labels must have a length greater than zero')
        raise ValueError()

    if tag is None:
        tag = SALTSHAKER.shake()

    require_type(tag, str)

    logging.debug('update label if tag (label, tag): (%s, %s)' % (label, tag))
    label += ("_" + tag)

    return label


def update_label_if_tag(label, tag):
    """Temporarily, for compatibility."""
    return _unique_label(label, tag)


def bq_upload(files, table, schema, args):
  record_ids = p | 'CreateIDs' >> beam.Create(['1', '2', '3', '4', '5'])
  records = record_ids | 'CreateRecords' >> beam.Map(create_random_record)
  records | 'write' >> beam.io.Write(
      beam.io.BigQuerySink(
          known_args.output,
          schema=table_schema,
          create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
          write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE))


def dev_ladd(label, addition):
    if addition is None:
        return label
    return (label + "_" + addition)



def gsutil_expand_stem(stem, strip_extension=False):
    """Collect all GCS files matching a provided path stem.

    Args:
        stem (string): The GCS stem query.
        strip_extension (bool): Whether to remove the file extension from stem.

    Returns:
        list: A list, possibly, empty, of GCS files matching stem.

    """

    if strip_extension and stem[-3:] == '.fa': # HACK
        stem = stem[:-3]

    with open(os.devnull, 'w') as dev_null:
        try:
            cmd_str = ' '.join(['gsutil', 'ls', stem + '*'])
            cmd = subprocess.Popen(cmd_str, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=dev_null)
            files = []
            for line in cmd.stdout:
                files.append(line.strip())
            return files
            # cmd = subprocess.check_output(['gsutil', 'ls', stem + '*'],
            #                              stderr=dev_null)
        except:
            # TODO catch cases where the bucket already exists and is not owned
            # by you or where the provided name is invalid.
            print('exception')


def filename(path):
    if hasattr(path, 'remote_path'):
        path = path.remote_path  # hack
    logging.debug('file with path %s' % path)
    return path.split('/')[-1]


def _localize_single(remote_path, local_stem='/mnt/data/input'):
    fname = filename(remote_path)
    return os.path.join(local_stem, fname)


def recursive_flatten(flattenable):
    """Flatten a potentially non-flat file list."""
    flattened = []
    if not isinstance(flattenable, list):
        # if it doesn't need to be flattened then just return it.
        return flattenable
    for item in flattenable:
        if isinstance(item, list):
            flattened.extend(recursive_flatten(item))
        else:
            flattened.append(item)
    return flattened


def localize(localizable, local_stem='/mnt/data/input'):

    logging.debug('localizing %s' % localizable)

    if isinstance(localizable, list) and len(localizable) == 1:
        localizable = localizable[0]

    if (isinstance(localizable, str)
        or isinstance(localizable, File)
        or isinstance(localizable, unicode)):
        return _localize_single(localizable, local_stem)
    else:
        logging.error('Cannot localize object with type %s' % type(localizable))
        logging.error(localizable)
        raise ValueError()


def localize_set(localizable, local_stem='/mnt/data/input'):
    if isinstance(localizable, list):
        localizable = recursive_flatten(localizable)
        for i, thing in enumerate(localizable):
            localizable[i] = localize(thing, local_stem)
        return localizable
    else:
        logging.error('Cannot localize object with type %s' % type(localizable))
        logging.error(localizable)
        raise ValueError()

def flatten(input_array):
    """Flatten a potentially non-flat file list."""
    flattened = []
    for sublist in input_array:
        if isinstance(sublist, str):
            flattened.append(sublist)
            continue
        for val in sublist:
            flattened.append(val)
    return flattened


def format_java_mem(num_giggybites):
    return '-Xmx%sG' % str(int(math.floor(num_giggybites)))


def copy_input_to_output(nonlocal_input):
    cmd = build_cmd(['cp', localize(nonlocal_input), '/mnt/data/output/'])
    return cmd


def build_outputs(fnames, output_dir, meta=None):
    if not isinstance(fnames, list):
        logging.error('expected fnames argument to be of type list')
        raise ValueError()
    if not isinstance(output_dir, str):
        logging.error('expected output_dir argument to be of type str')
        raise ValueError()
    out = []
    for name in fnames:
        f = File()


def prepare_inputs(inputs):
    inputs = recursive_flatten(inputs)
    out = []
    for i in inputs:
        if isinstance(i, File):
            i = i.remote_path
        out.append(i)
    return out


def file_set(local_stem, names):
    files = []
    for fname in names:
        files.append(File(remote_path=localize(fname,
                                               local_stem=local_stem)))
    return files


class Command(object):
    """Build commands in a structured way."""

    def __init__(self, initial=None):
        """Initialize a command object optionally with an initial command."""
        self.txt = None
        if initial is not None:
            self.txt = self._build(initial)

    def _build(self, cmd_list):
        """Build a command string from an array of arguments.

        TODO: Extend with basic checking besides compiling command.

        Args:
            cmd_list (list): An array of command parameters.

        """
        assert isinstance(cmd_list, list)
        assert len(cmd_list) > 0
        for i, thing in enumerate(cmd_list):
            cmd_list[i] = str(thing)
        cmd = ' '.join(cmd_list)
        logging.info(cmd)
        return cmd

    def _extend(self, cmd_list, joiner):
        """Chain a sequence of commands with a joiner such as '&&' or '|'."""

        assert isinstance(cmd_list, list)
        assert len(cmd_list) > 0
        cmd_new = self._build(cmd_list)

        logging.info(cmd_new)

        if self.txt is None:
            self.txt = cmd_new
        else:
            self.txt += (' ' + joiner + ' ') + cmd_new

    def prepend_command(self, prefix):
        """Prepend a command to the current command series."""
        self.txt = ' && '.join([prefix.txt, self.txt])

    def chain(self, cmd_list):
        """Sequential-append a command to the current command with &&."""
        self._extend(cmd_list, joiner="&&")

    def chain_command(self, command):
        """Chain together two Command objects."""
        assert isinstance(command, Command)

        if command.txt is None:
            return
        elif self.txt is None:
            self.txt = command.txt
        else:
            self.txt += ' && ' + command.txt

    def pipe(self, cmd_list):
        """Pipe-append a command to the current command with |."""
        self._extend(cmd_list, joiner="|")


def check_setter_type(setter_name, expected_type, value, allow_none=False):
    if allow_none and value is None:
        return
    if not isinstance(value, expected_type):
        msg = 'Setting %s requires argument of type `%s`, saw: %s' % (
            setter_name, expected_type, value)
        logging.error(msg)
        raise ValueError(msg)


def expect_type(value, t, allow_none=False):
    if allow_none and value is None:
        return
    if not isinstance(value, t):
        msg = 'Expected type %s, saw %s.' % (t, value)
        logging.error(msg)
        raise ValueError(msg)


def regex_match(value, reg):
    return (value == reg)  # hack
    # try:
    #     pattern = re.compile(reg)
    # except Exception as e:
    #     msg = 'Error while compiling regex %s to match value %s' % (reg,
    #                                                                 value)
    #     logging.error(msg)
    #     raise ValueError(msg)
    # return (pattern.match(value) is not None)


class File(object):
    """Object for collecting attributes and operations for tracking files."""

    def __init__(self, file_type=None, condition=None, remote_path=None,
                 local_path=None, template=None):
        """Initialize a File object.

        Args:
            type (str): The type of file (e.g. 'txt', 'csv', 'fastq').
            condition (str): The file's case/control or other condition.

        """
        self.file_type = file_type
        self.condition = condition
        self.remote_path = remote_path
        self.local_path = local_path
        if template is not None:
            self.update(template)

    def __str__(self):
        return self.remote_path

    def as_dict(self):
        """Convert a File object into a dictionary.

        Returns:
            Dictionary representation of file object.

        """
        return {
            'file_type': self.file_type,
            'condition': self.condition,
            'remote_path': self.remote_path,
            'local_path': self.local_path
        }

    def match(self, query, debug=False):
        """Determine whether file object matches a specified query dict.

        Example:
            >>> f = File(type='bam', condition='a')
            >>> f.match({'type': '*am'})
            True

        Args:
            query: A dictionary representation of a query

        Returns:
            True if matched, False otherwise.

        """
        is_match = True
        if debug:
            logging.info('running File.match() for file: %s' % self.as_dict())
        for q, v in query.items():
            if debug:
                logging.info('considering query k,v: %s,%s' % (q, v))
            if not hasattr(self, q) or not regex_match(getattr(self, q), v):
                is_match = False
        if debug:
            logging.info('File.match() determined: %s' % is_match)
        return is_match

    def update(self, metadata, overwrite=True):
        """Update a file object with additional metadata.

        Example:
            >>> f = File(type='bam')
            >>> f.update({'condition': 'a'})

        Args:
            metadata (dict): A dictionary representing the attributes to update

        """
        expect_type(metadata, dict)
        for k, v in metadata.items():
            if not hasattr(self, k):
                raise ValueError('Could not set unknown field %s' % k)
            if not overwrite:
                if getattr(self, k) is not None:
                    raise ValueError()
            setattr(self, k, v)

    @property
    def file_type(self):
        """str: The type of the file (e.g. 'txt', 'csv', 'fastq')."""
        return self._file_type

    @file_type.setter
    def file_type(self, value):
        check_setter_type('File.file_type', str, value, allow_none=True)
        self._file_type = value

    @property
    def condition(self):
        """str: The file's case/control or other condition."""
        return self._condition

    @condition.setter
    def condition(self, value):
        check_setter_type('File.condition', str, value, allow_none=True)
        self._condition = value

    @property
    def remote_path(self):
        """str: The file's path on cloud storage."""
        return self._remote_path

    @remote_path.setter
    def remote_path(self, value):
        check_setter_type('File.remote_path', str, value, allow_none=True)
        self._remote_path = value

    @property
    def local_path(self):
        """str: The file's path on the local device."""
        return self._local_path

    @local_path.setter
    def local_path(self, value):
        check_setter_type('File.local_path', str, value, allow_none=True)
        self._local_path = value


class FileCollection(object):
    """A collection of file objects."""

    def __init__(self, template=None):
        """Initialize a FileCollection object.

        Args:
            template (list, optional): A list of `dict` objects specifying the
                files that should be present in the created FileCollection.

        """
        self._files = []
        if template is not None:
            expect_type(template, list)
            for item in template:
                self.add(File(template=item))

    def add(self, f):
        """Add a single file to this file collection.

        Args:
            addition (obj): Either a File or dict object specifying a file.

        Returns:
            A FileCollection object.

        """
        expect_type(f, File)
        self._files.append(f)

    def add_paths(self, addition, metadata):
        """Add multiple files to this file collection.

        TODO: This has some issues. Do you always want to assume the added
        paths are local paths? Is this whole schema a bit heavy-handed?

        Example:
            >>> cond_a_pairs = ['file/path/one_a.fq', 'file/path/two_a.fq']
            >>> reads_a = FileCollection().add_multi(cond_a_pairs,
            ...                                      {'condition': 'a'})
            >>> reads_a.dump()
            [{'path': 'file/path/one_a.fq', 'condition': 'a'},
             {'path': 'file/path/two_a.fq', 'condition': 'a'}]

        Args:
            addition (list): A list of file paths to add to this collection.
            metadata (dict): A dictionary describing the metadata to assign
                to each File object created from each path specified via the
                addition parameter.

        Returns:
            A FileCollection object.

        """
        expect_type(addition, list)
        for path in addition:
            expect_type(path, str)
            f = File(template={'remote_path': path})
            f.update(metadata)
            self.add(f)

    def as_pcollection(self):
        """Casts the FileCollection to a PCollection object for use in Beam.

        Args:
            pipeline (PCollection): A Beam pipeline to which to chain this op.

        Returns:
            A PCollection object.

        """
        pass

    def size(self):
        """Get the size of the file collection."""
        return len(self._files)

    def items(self):
        """Get the items belonging to the file collection."""
        return self._files

    def dump(self):
        """Translate a FileCollection object to an array of dictionaries.

        Example:
            >>> fc = FileCollection([{'type': 'bam'}])
            >>> f.dump()
            [{'type': 'bam'}]

        Returns:
            An array of dictionaries.

        """
        out = []
        for f in self._files:
            out.append(f.as_dict())
        return out


def file_match(files, query):
    out = []
    if isinstance(files, list):
        for f in files:
            if f.match(query, debug=False):
                out.append(f)
    else:
        logging.error('file_match expects a list of File objects as input, '
                      'saw %s' % files)
        raise ValueError()
    # Here we're yielding the resulting array for this file set instead of yielding
    # individual elements which would flatten the global set. ...
    if len(out) > 0:
        yield out
    else:
        logging.info('file_match yield not matches on file set for '
                     'query: %s' % query)


def match(collection, query, label="match", tag=None):
    label = update_label_if_tag(label, tag)
    return (collection | label >> beam.FlatMap(lambda x: file_match(x, query)))


def combine(p, collections, label="combine", tag=None):
    if tag is not None and isinstance(tag, str):
        tag += ('_' + tag)
    return (collections | label >> beam.Flatten())


def _union(items):
    return [item for sublist in items for item in sublist]

def union(p):
  return (p | beam.CombineGlobally(_union))


def create_file_set(p, files, label="create", tag=None):
    """Temporary, for compatibility."""
    return fc_create(p, files, label="create", tag=None)


def fc_create(p, files, label="create", tag=None):
    label = update_label_if_tag(label, tag)
    out = (p | label >> beam.Create(files))
    return out


def dev_to_dict(files):
    out = []
    for f in files:
        if isinstance(f, dict):
            out.append(f)
        elif isinstance(f, File):
            out.append(f.as_dict())
        else:
            out.append(f)
    yield out


def dev_fc_to_dict(collection, label='to_dict', tag=None):
    label = update_label_if_tag(label, tag)
    return (collection | label >> beam.FlatMap(lambda x: dev_to_dict(x)))


logging = Logger()
shaker = SaltShaker()
