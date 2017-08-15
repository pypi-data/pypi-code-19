# coding: utf-8
import os
import re
import logging
import logging.handlers
import shutil
import shlex
import spur
import random
import datetime
import base64
import tarfile
import simplejson as json
import jsonschema
import paramiko
from string import digits, ascii_letters  # pylint: disable=deprecated-module
from deployv.helpers import container
from deployv import base

logger = logging.getLogger(__name__)  # pylint: disable=C0103


def copy_list_dicts(lines):
    res = []
    for line in lines:
        dict_t = {}
        for keys in line.keys():
            dict_t.update({keys: line[keys]})
        res.append(dict_t.copy())
    return res


def setup_deployv_logger(name='deployv', level=logging.DEBUG, log_file=None):
    """Configures a logger, setting the level and a stream handler by default.
    If a log file name is passed, a file handler is also created.

    By default it configures the 'deployv' logger, so the config applies
    automatically to every other logger that belongs to a submodule.
    (For example: 'deployv.commands.deployvcmd')

    Important note: To avoid multiple configurations or overriding other loggers,
    the loggers should be called using 'logging.getLogger(__name__)', so the
    logger is named like the file where is being used. This also facilitates that
    every logger inside the 'deployv' module gets the correct parent settings.

    This function returns the configured logger, but it should be used to
    configure the parent logger ('deployv') and only use a child logger from
    another module.
    """
    dv_logger = logging.getLogger(name)
    dv_logger.propagate = False
    dv_logger.setLevel(level)
    dv_logger.handlers = []
    formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)-5s - "
                                      "%(name)s.%(module)s.%(funcName)s - "
                                      "%(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    dv_logger.addHandler(stream_handler)
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(log_file)
        file_handler.setFormatter(formatter)
        dv_logger.addHandler(file_handler)
    return dv_logger


def is_iterable(obj):
    """ Method that verifies if an object is iterable

    :param obj: Any object that will be tested if is iterable
    :return: True or False if the object can be iterated
    """
    return hasattr(obj, '__iter__')


def load_json(filename):
    """ Load info from Json file

    :param filename: Name of Json file (full path)

    :return: Object loaded
    """
    logger.debug("Opening json file %s", filename)
    with open(filename, "r") as dest:
        try:
            info = json.load(dest)
        except json.scanner.JSONDecodeError as error:
            logger.error('Could not load %s: %s', filename, error)
            return False
        logger.debug("File loaded")
        return info


def save_json(info, filename):
    """Save info into Json file.

    :param info: Object to be saved
    :param filename: Name of Json file

    Returns:
        Absolute path of Json file
    """
    logger.debug("Opening file %s", filename)
    try:
        with open(filename, 'w') as fout:
            json.dump(info, fout, sort_keys=True, indent=4, ensure_ascii=False,
                      separators=(',', ':'))
            if not os.path.isabs(filename):
                filename = os.path.abspath(filename)
            logger.debug("File saved")
    except IOError as error:
        logger.error(error)
        return False
    return filename


def load_default_config():
    """ Loads the default configuration file.

    :return: Dictionary with the default configuration
    """
    default_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       '..',
                                       'config')
    default_config = load_json(os.path.join(default_config_path, 'default_config.json'))
    return default_config


def merge_config(config_file, keys_file=False, branches=False):
    """Merges keys_file and branches into config_file and returns a single json
    if no keys_file or branches is given just loads the config file

     :param config_file: Config file in json format
     :param keys_file: Param with the key file name and full path to it
     :param branches: Branches file to be used
     :return: Dict with complete json configuration after saving it into the config_file file
    """
    json_config = load_json(config_file)
    if not isinstance(json_config, dict):
        return
    default_config = load_default_config()
    new_config = merge_dicts(default_config, json_config)
    changed = False
    if branches:
        json_branches = load_json(branches)
        new_config.get("instance").update({"repositories": json_branches})
        changed = True
    if keys_file:
        encoded_key = generate_attachment(keys_file)
        new_config.get("instance").update({"ssh_key": encoded_key})
        changed = True
    if changed:
        save_json(new_config, config_file)
    return new_config


def list_backups(file_dir, prefix):
    """List all files which start with prefix and sort
    them by date

    :param file_dir: Directory where backups are stored
    :param prefix: Prefix files to seek
    :return: sorted list
    """
    items = []
    for each in os.listdir(file_dir):
        if (prefix in each) and os.path.isfile(os.path.join(file_dir, each)):
            items.append(str(each))
    items.sort(reverse=True)
    return items


def clean_files(files):
    """ Remove unnecessary and temporary files

    :param files: A list or a str of absolute or relative paths thar will be erased
    """
    items = files if is_iterable(files) else [files]
    for item in items:
        fname = item[0] if is_iterable(item) else item
        if fname != "/":
            logger.info('Removing %s', fname)
            if os.path.isfile(fname):
                os.remove(fname)
            elif os.path.isdir(fname):
                shutil.rmtree(fname)
        else:
            logger.error(
                "Invalid target path: '/'. Are you trying to delete your root path?")


def resume_log(log_lines):
    """Gets the log lines from -u (modules or all) and parse them to get the totals
    according to the filters dict

    :param log_lines: each element of the list is a log line
    :return: dict with key filters as keys and a list with all matched lines
    """
    def critical(line):
        criteria = re.compile(r'.*\d\sCRITICAL\s.*')
        return criteria.match(line)

    def errors(line):
        criteria = re.compile(r'.*\d\sERROR\s.*')
        return criteria.match(line)

    def warnings_trans(line):
        criteria = re.compile(
            r'.*\d\sWARNING\s.*no translation for language.*')
        return criteria.match(line)

    def import_errors(line):
        criteria = re.compile(r'^ImportError.*')
        return criteria.match(line)

    def warnings(line):
        criteria = re.compile(r'.*\d\sWARNING\s.*')
        return criteria.match(line) and 'no translation for language' not in line

    filters = {
        'critical': critical,
        'errors': errors,
        'warnings': warnings,
        'warnings_trans': warnings_trans,
        'import_errors': import_errors
    }
    res = {name: [] for name in filters}
    for line in log_lines:
        stripped_line = line.strip()
        for name, criteria in filters.items():
            if criteria(stripped_line):
                res.get(name).append(stripped_line)
                break

    return res


def get_strtime():
    """ Returns time stamp formatted as follows:

        %Y%m%d_%H%M%S

        So all backups and files that require this in the name will have the same format,
        if changes will be in one place, here.
    :return: Formatted timestamp
    """
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def get_decompress_object(file_name):
    """ Returns an object to extract file_name*, only tar.gz and tar.bz2 are supported now
    ::
        >>> from deployv.helpers import utils
        >>> utils.get_decompress_object('filename.tar.bz2')
        (<bound method type.open of <class 'tarfile.TarFile'>>, 'r:bz2')

    Or if you pass a tar.gz file
    ::
        >>> from deployv.helpers import utils
        >>> utils.get_decompress_object('filename.tar.gz')
        (<bound method type.open of <class 'tarfile.TarFile'>>, 'r:gz')

    :param file_name: File name to be extracted
    :return: Tuple with the object and mode
    """
    if file_name.endswith('tar.gz'):
        fobject, modestr = tarfile.open, 'r:gz'
    elif file_name.endswith('tar.bz2'):
        fobject, modestr = tarfile.open, 'r:bz2'
    else:
        raise RuntimeError('Unknown file format "{}"'.format(file_name))
    return fobject, modestr


def decompress_files(name, dest_folder):
    """ Decompress a file, set of files or a folder compressed in tar.bz2 format

    :param name: Compressed file name (full or relative path)
    :param dest_folder: Folder where the decompressed files will be extracted
    :return: The absolute path to decompressed folder or file
    """
    assert os.path.exists(name)
    logger.debug("Decompressing file: %s", name)
    if os.path.isdir(name):
        return name
    logger.debug('Extracting %s into %s', name, dest_folder)
    fobject, modestr = get_decompress_object(name)
    tar = fobject(name, mode=modestr)
    try:
        tar.extractall(dest_folder)
    except (EOFError, IOError) as error:
        logger.exception('Error uncompressing file %s', get_error_message(error))
        raise
    name_list = tar.getmembers()
    tar.close()
    base_folder = dest_folder
    for fname in name_list:
        if os.path.basename(fname.name) == 'database_dump.b64' or \
           os.path.basename(fname.name) == 'database_dump.sql':
            base_folder = os.path.dirname(fname.name)
            break

    logger.debug("Destination folder: %s", dest_folder)
    logger.debug("Bakcup folder: %s", base_folder)
    if name.endswith('tar.bz2') or name.endswith('tar.gz'):
        fname = os.path.basename(name)
        dest_folder = os.path.join(dest_folder, base_folder)
    logger.debug("Destination folder: %s", dest_folder)
    return dest_folder


def odoo2postgres(odoo_config):
    """ This is a helper to convert from a odoo configuration dict to a postgres configuration dict
    using libpq
    format: http://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-PARAMKEYWORDS,
    and also can map env vars gotten from a container

    :param odoo_config: Odoo database configuration
    :return: Dict with psql configuration
    """
    mapping = {
        'user': ['db_user', 'DB_USER'],
        'host': ['db_host', 'DB_HOST'],
        'port': ['db_port', 'DB_PORT'],
        'password': ['db_password', 'DB_PASSWORD'],
        'dbname': ['db_name', 'DB_NAME']
    }
    res = {}
    for psql_key, psql_value in mapping.items():
        for odoo_key, odoo_value in odoo_config.items():
            if odoo_key in psql_value:
                res.update({psql_key: odoo_value})
    return res


def generate_dbname(config, backup_name=False, prefix=False):
    """ Generates a database name for a test/dev instance based on the container name and
    backup used for the restoration. The created name will have the same timestamp that the one
    used, but if no backup name is supplied or the backup does not have a timestamp in the name
    the actual date will be used

    :param config: Instance configuration dict
    :param backup_name: Optional backup name to be restored
    :return:
    """
    if not prefix:
        prefix = container.generate_prefix(config)
    if backup_name:
        name = re.search(r"_(\d{8}_\d{6})", backup_name)
        if name:
            name = name.group(1)
        else:
            name = get_strtime()
    else:
        name = get_strtime()
    res = '{prefix}_{date}'.format(prefix=prefix, date=name)
    return res


def generate_backup_name(database_name, reason=False, prefix=False):
    """Generates the backup name according to the following standard:
       database_name_reason_YYYYmmdd_HHMMSS
       If reason is none:
       database_name_YYYYmmdd_HHMMSS
    """
    if reason and not prefix:
        res = '%s_%s_%s' % \
            (database_name, reason, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    elif prefix and not reason:
        res = '%s_%s' % \
            (prefix, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    elif prefix and reason:
        res = '%s_%s_%s' % \
            (prefix, reason, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    else:
        res = '%s_%s' % (
            database_name, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    return res


def decode_b64_file(src, dst):
    """ Read src base64 encoded file and output its content to dst file
    :param src: Source file to read
    :param dst: Destination file
    """
    with open(src, 'r') as source_file:
        with open(dst, 'w') as destination_file:
            for line in source_file:
                destination_file.write(base64.b64decode(line))


def compress_files(name, files, dest_folder=None, cformat='bz2'):
    """ Compress a file, set of files or a folder in the specified cforma

    :param name: Desired file name w/o extension
    :param files: A list with the absolute o relative path to the files
                      that will be added to the compressed file
    :param dest_folder: The folder where will be stored the compressed file
    :param cformat: Desired format for compression, only supported bz2 and gz
    """
    if not dest_folder:
        dest_folder = '.'
    if cformat not in ['bz2', 'gz']:
        raise RuntimeError('Unknown file format "{}"'.format(cformat))
    if cformat == 'gz':
        fobject, modestr = tarfile.open, 'w:gz'
    elif cformat == 'bz2':
        fobject, modestr = tarfile.open, 'w:bz2'
    logger.debug("Generating compressed file: %s in %s folder",
                 name, dest_folder)

    bkp_name = '{0}.tar.{1}'.format(name, cformat)
    full_tmp_name = os.path.join(
        dest_folder,
        '._{}'.format(bkp_name)
    )
    full_name = os.path.join(dest_folder, bkp_name)

    with fobject(full_tmp_name, mode=modestr) as tar_file:
        for fname in files:
            if hasattr(fname, '__iter__'):
                tar_file.add(fname[0], os.path.join(name, fname[1]))
            else:
                basename = os.path.basename(fname)
                tar_file.add(fname, os.path.join(name, basename))
    shutil.move(full_tmp_name, full_name)
    return full_name


def generate_attachment(file_name):
    """ Helper that generates a file with base 64 encoded content
    to be used as an attachment in the messages returned by deployv

    :param file_name: Full path and name of the file to be attached
    :return: File content in b64 format
    """
    with open(file_name) as attch_file:
        res = base64.b64encode(attch_file.read())
    return res


def get_error_message(exception_obj):
    """ Some exceptions uses message and others explanation, so with this little helper we avoid
        to rewrite the code every single time.
    :param exception_obj: The raised exception Object
    :return: A string containing the exception message
    """
    if hasattr(exception_obj, 'stderr_output'):
        return exception_obj.stderr_output
    if hasattr(exception_obj, 'explanation'):
        return exception_obj.explanation
    return exception_obj.message


def makedir(path_name):
    try:
        os.mkdir(path_name)
    except OSError as error:
        if 'File exists' not in error.strerror:
            raise


def clone_repo(repo, branch, path):
    shell = spur.LocalShell()
    try:
        shell.run(
            shlex.split('git clone -b {branch} --single-branch --depth=1 {repo} {path}'.format(
                branch=branch, repo=repo, path=path)))
    except spur.results.RunProcessError as error:
        if 'Could not find remote branch' in get_error_message(error):
            raise base.errors.NoSuchBranch(branch, repo)
        if 'already exists and is not an empty directory' not in get_error_message(error):
            raise


def merge_dicts(original, new):
    """ Updates key by key a dictionary (original) with the values from another dictionary (new)
        if the value of a key in the new dictionay and the value of the same key in the original
        dictionary are dictionaries, it merges both dictionaries first, if they are lists, it
        appends the values of both lists, otherwise it will replace the value of the original
        dictionary with the value in the new one
    """
    res = original.copy()
    for new_key, new_value in new.items():
        original_value = original.get(new_key)
        if isinstance(original_value, dict) and isinstance(new_value, dict):
            new_dict = merge_dicts(original_value, new_value)
            res.update({new_key: new_dict})
        elif isinstance(original_value, list) and isinstance(new_value, list):
            res.update({new_key: original_value + new_value})
        else:
            res.update({new_key: new_value})
    return res


def clean_string(string):
    """ When creating an image from a branch containing any special char like ., # or $
        or containing upper case chars docker shows an error because those are not allowed chars
    :param string: The string you want to clean
    :return: A string without the invalid chars and without upper case chars
    """
    logger.debug('Clean string %s', string)
    res = re.sub(r"[\.#\$]", "", string)
    return res.lower()


def validate_external_file(file_path):
    """ Helper method that makes sure the a file is plain text and not too big
    so it can be added to the config json.

    :param file_path: Path to the external file we want to add to the config.
    :return: True if the file is an acceptable candidate to be added to the config,
             False otherwise.
    """
    file_size = os.path.getsize(file_path)
    if os.path.splitext(file_path)[1] == '.json':
        if not load_json(file_path):
            return False
    if file_size > 500000:
        logger.error('%s is not a valid file, it\'s size shouldn\'t be more than 500kb,'
                     ' file size: %s', file_path, file_size)
        return False
    return True


def random_string(length):
    """ Generates a random string consisting of numbers and chars with the specified length
    """
    res = u''.join(random.choice(ascii_letters+digits) for letter in range(length))
    return res


def check_message(message):
    """ Try to check the message against the defines schema. According to the documentation
    if any error is present the validate method will rise an exception:
    https://pypi.python.org/pypi/jsonschema

    :param message: The message you want to check
    :return: The list with all errors, none otherwise
    """
    schema = load_json(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'json_schema.json'))
    try:
        jsonschema.validate(message, schema)
    except jsonschema.ValidationError as error:
        s_path = list(error.absolute_schema_path)[:-1]
        msg = '{msg}\nIn {path}'.format(msg=get_error_message(error),
                                        path='.'.join(s_path))
        logger.error('An exception was catched while checking the message: %s', msg)
        return msg
    return None


def decode(string, errors='replace'):
    return string.decode(encoding=base.CHARSET, errors=errors)


def encode(string, errors='replace'):
    return string.encode(encoding=base.CHARSET, errors=errors)


def version_cid(customer_id):
    """ Extract the version from the customer id

    :param customer_id: A string with the customer id (customer80, customer100)
    :return: The sversion (8.0, 10.0)
    """
    version = None
    match = re.match("(([a-z]+_*))([0-9]+|saas-[0-9]+)", customer_id, re.I)
    if match:
        version = match.groups()[-1]
        if version.isdigit():
            res = float(version) / 10.0
            version = str(res)
    return version


def parse_url(url):
    """ Parses an url and returns the parts that we are interested in:
        port, domain, user, destination path

    :param url: the url to be parsed, the following format is expected:
                protocol://[user@]domain.com[:port]/remote/path
    :return: Dict with the parsed values
    """
    match = re.match(
        r'^(?P<prot>\w+)://((?P<user>\w+)@)?(?P<dom>[\w|.|-]+)(:(?P<port>\d+))?/(?P<path>.*)$',
        url)
    res = dict(
        protocol=match.group('prot'),
        user=match.group('user'),
        domain=match.group('dom'),
        port=match.group('port'),
        folder=match.group('path')
    )
    return res


def upload_scp(filename, credentials):
    logger.info('Uploading %s using SFTP', filename)
    port = credentials.get('port') if credentials.get('port') else 22
    transport = paramiko.Transport((credentials.get('domain'), int(port)))
    private_key = paramiko.RSAKey.from_private_key_file(
        os.path.expanduser(os.path.join('~', '.ssh', 'id_rsa')))
    transport.connect(username=credentials.get('user'), pkey=private_key)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.chdir(credentials.get('folder'))
    sftp.put(filename, os.path.basename(filename))
    sftp.close()


def upload_file(file_name, url):
    """ Uploads a file to the desired url using the matching protocol

    :param file_name: The full or relative path to the file that you want to upload
    :param url: the url and path to upload the file to with
                the following format: protocol://[user@]domain.com[:port]/remote/path
                if no port is provided will use 22, and if no user is provided will
                use the O.S. user that is executing the command
    """
    credentials = parse_url(url)
    if credentials.get('protocol') == 'sftp':
        upload_scp(file_name, credentials)
    else:
        raise NotImplementedError('Protocol {protocol} not implemented yet'
                                  .format(protocol=credentials.get('protocol')))


def get_backup_src(config_dict=False, deployv_config=False):
    res = False
    if config_dict and "backup_folder" in config_dict.get("container_config"):
        res = os.path.expanduser(config_dict.get("container_config").get("backup_folder"))
    elif deployv_config and deployv_config.has_option("deployer", "backup_folder"):
        res = os.path.expanduser(deployv_config.get("deployer", "backup_folder"))
    return res
