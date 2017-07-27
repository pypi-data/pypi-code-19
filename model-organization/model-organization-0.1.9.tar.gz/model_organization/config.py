import os
import os.path as osp
import six
import inspect
import sys
import logging
import logging.config
import yaml
import glob
import fasteners
import copy
from collections import OrderedDict, defaultdict
import model_organization.utils as utils


docstrings = utils.docstrings


def _get_home():
    """Find user's home directory if possible.
    Otherwise, returns None.

    :see:  http://mail.python.org/pipermail/python-list/2005-February/325395.html

    This function is copied from matplotlib version 1.4.3, Jan 2016
    """
    try:
        if six.PY2 and sys.platform == 'win32':
            path = os.path.expanduser(b"~").decode(sys.getfilesystemencoding())
        else:
            path = os.path.expanduser("~")
    except ImportError:
        # This happens on Google App Engine (pwd module is not present).
        pass
    else:
        if os.path.isdir(path):
            return path
    for evar in ('HOME', 'USERPROFILE', 'TMP'):
        path = os.environ.get(evar)
        if path is not None and os.path.isdir(path):
            return path
    return None


def get_configdir(name):
    """
    Return the string representing the configuration directory.

    The directory is chosen as follows:

    1. If the ``name.upper() + CONFIGDIR`` environment variable is supplied,
       choose that.

    2a. On Linux, choose `$HOME/.config`.

    2b. On other platforms, choose `$HOME/.matplotlib`.

    3. If the chosen directory exists, use that as the
       configuration directory.
    4. A directory: return None.

    Notes
    -----
    This function is taken from the matplotlib [1] module

    References
    ----------
    [1]: http://matplotlib.org/api/"""
    configdir = os.environ.get('%sCONFIGDIR' % name.upper())
    if configdir is not None:
        return os.path.abspath(configdir)

    p = None
    h = _get_home()
    if ((sys.platform.startswith('linux') or
         sys.platform.startswith('darwin')) and h is not None):
        p = os.path.join(h, '.config/' + name)
    elif h is not None:
        p = os.path.join(h, '.' + name)

    if not os.path.exists(p):
        os.makedirs(p)
    return p


def setup_logging(default_path=None, default_level=logging.INFO,
                  env_key=None):
    """
    Setup logging configuration

    Parameters
    ----------
    default_path: str
        Default path of the yaml logging configuration file. If None, it
        defaults to the 'logging.yaml' file in the config directory
    default_level: int
        Default: :data:`logging.INFO`. Default level if default_path does not
        exist
    env_key: str
        environment variable specifying a different logging file than
        `default_path` (Default: 'LOG_CFG')

    Returns
    -------
    path: str
        Path to the logging configuration file

    Notes
    -----
    Function taken from
    http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python"""
    path = default_path or os.path.join(
        os.path.dirname(__file__), 'logging.yaml')
    value = os.getenv(env_key, None) if env_key is not None else None
    home = _get_home()
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
        for handler in config.get('handlers', {}).values():
            if '~' in handler.get('filename', ''):
                handler['filename'] = handler['filename'].replace(
                    '~', home)
        logging.config.dictConfig(config)
    else:
        path = None
        logging.basicConfig(level=default_level)
    return path


def ordered_yaml_load(stream, Loader=None, object_pairs_hook=OrderedDict):
    """Loads the stream into an OrderedDict.
    Taken from

    http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-
    mappings-as-ordereddicts"""
    Loader = Loader or yaml.Loader

    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def ordered_yaml_dump(data, stream=None, Dumper=None, **kwds):
    """Dumps the stream from an OrderedDict.
    Taken from

    http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-
    mappings-as-ordereddicts"""
    Dumper = Dumper or yaml.Dumper

    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


def safe_load(fname):
    """
    Load the file fname and make sure it can be done in parallel

    Parameters
    ----------
    fname: str
        The path name
    """
    lock = fasteners.InterProcessLock(fname + '.lck')
    lock.acquire()
    try:
        with open(fname) as f:
            return ordered_yaml_load(f)
    except:
        raise
    finally:
        lock.release()


def safe_dump(d, fname, *args, **kwargs):
    """
    Savely dump `d` to `fname` using yaml

    This method creates a copy of `fname` called ``fname + '~'`` before saving
    `d` to `fname` using :func:`ordered_yaml_dump`

    Parameters
    ----------
    d: object
        The object to dump
    fname: str
        The path where to dump `d`

    Other Parameters
    ----------------
    ``*args, **kwargs``
        Will be forwarded to the :func:`ordered_yaml_dump` function
    """
    if osp.exists(fname):
        os.rename(fname, fname + '~')
    lock = fasteners.InterProcessLock(fname + '.lck')
    lock.acquire()
    try:
        with open(fname, 'w') as f:
            ordered_yaml_dump(d, f, *args, **kwargs)
    except:
        raise
    finally:
        lock.release()


class Archive(six.text_type):
    """
    Just a dummy string subclass to identify archived experiments
    """

    #: The name of the project inside this archive
    project = None

    #: The time when this project has been archived
    time = None


class ExperimentsConfig(OrderedDict):
    """
    The configuration of the experiments

    This class acts like a :class:`collections.OrderedDict` but loads the
    experiment configuration only when you access the specific item (i.e. via
    ``d['exp_id']``)
    """

    #: list of str. The keys describing paths for the model. Note that these
    #: keys here are replaced by the keys in the
    #: :attr:`~model_organization.ModelOrganizer.paths` attribute of the
    #: specific :class:`model_organization.ModelOrganizer` instance
    paths = ['expdir', 'src', 'data', 'input', 'outdata', 'outdir',
             'plot_output', 'project_output', 'forcing']

    _initialized = True

    @property
    def exp_file(self):
        """The path to the file containing all experiments in the configuration
        """
        return osp.join(self.projects.conf_dir, 'experiments.yml')

    @property
    def project_map(self):
        """A mapping from project name to experiments"""
        # first update with the experiments in the memory (the others should
        # already be loaded within the :attr:`exp_files` attribute)
        for key, val in self.items():
            if isinstance(val, dict):
                l = self._project_map[val['project']]
            elif isinstance(val, Archive):
                l = self._project_map[val.project]
            else:
                continue
            if key not in l:
                l.append(key)
        return self._project_map

    @property
    def exp_files(self):
        """A mapping from experiment to experiment configuration file

        Note that this attribute only contains experiments whose configuration
        has already dumped to the file!
        """
        ret = OrderedDict()
        # restore the order of the experiments
        exp_file = self.exp_file
        if osp.exists(exp_file):
            for key, val in safe_load(exp_file).items():
                ret[key] = val
        for project, d in self.projects.items():
            project_path = d['root']
            config_path = osp.join(project_path, '.project')
            if not osp.exists(config_path):
                continue
            for fname in glob.glob(osp.join(config_path, '*.yml')):
                if fname == '.project.yml':
                    continue
                exp = osp.splitext(osp.basename(fname))[0]
                if not isinstance(ret.get(exp), Archive):
                    ret[exp] = osp.join(config_path, exp + '.yml')
                if exp not in self._project_map[project]:
                    self._project_map[project].append(exp)
        return ret

    def __init__(self, projects, d=None, project_map=None):
        """
        Parameters
        ----------
        projects: ProjectConfig
            The project configuration
        d: dict
            An alternative dictionary to initialize from. If not given, the
            experiments are loaded on the fly from the :attr:`exp_files`
            attribute
        project_map: dict
            A mapping from project to experiments. If not given, it is created
            when accessing the :attr:`project_map` experiment
        """
        super(ExperimentsConfig, self).__init__()
        self.projects = projects
        # necessary switch for python 2 since the item is accessed when setting
        # it
        self._initialized = False
        self._project_map = project_map or defaultdict(list)
        if projects:
            if d is not None:
                for key, val in d.items():
                    self[key] = val
            else:
                # setup the paths for the experiments
                for key, val in self.exp_files.items():
                    self[key] = val
        del self._initialized

    def __getitem__(self, attr):
        ret = super(ExperimentsConfig, self).__getitem__(attr)
        if self._initialized and not isinstance(ret, (dict, Archive)):
            fname = super(ExperimentsConfig, self).__getitem__(attr)
            self[attr] = d = safe_load(fname)
            if isinstance(d, dict):
                self.fix_paths(d)
            return d
        else:
            return ret

    def __setitem__(self, key, val):
        if (isinstance(val, Archive) and
                key not in self._project_map[val.project]):
            # make sure the project_map is up-to-date
            self._project_map[val.project].append(key)
        super(ExperimentsConfig, self).__setitem__(key, val)

    def __reduce__(self):
        # in Python2 do not simply make an OrderedDict, because that
        # accesses the item itself
        return self.__class__, (self.projects, self.as_ordereddict(),
                                self._project_map)

    @docstrings.get_sectionsf('ExperimentsConfig.fix_paths',
                              sections=['Parameters', 'Returns'])
    @docstrings.dedent
    def fix_paths(self, d, root=None, project=None):
        """
        Fix the paths in the given dictionary to get absolute paths

        Parameters
        ----------
        d: dict
            One experiment configuration dictionary
        root: str
            The root path of the project
        project: str
            The project name

        Returns
        -------
        dict
            The modified `d`

        Notes
        -----
        d is modified in place!"""
        if root is None and project is None:
            project = d.get('project')
            if project is not None:
                root = self.projects[project]['root']
            else:
                root = d['root']
        elif root is None:
            root = self.projects[project]['root']
        elif project is None:
            pass
        paths = self.paths
        for key, val in d.items():
            if isinstance(val, dict):
                d[key] = self.fix_paths(val, root, project)
            elif key in paths:
                val = d[key]
                if isinstance(val, six.string_types) and not osp.isabs(val):
                    d[key] = osp.join(root, val)
                elif (isinstance(utils.safe_list(val)[0], six.string_types) and
                      not osp.isabs(val[0])):
                    for i in range(len(val)):
                        val[i] = osp.join(root, val[i])
        return d

    @docstrings.get_sectionsf('ExperimentsConfig.rel_paths',
                              sections=['Parameters', 'Returns'])
    @docstrings.dedent
    def rel_paths(self, d, root=None, project=None):
        """
        Fix the paths in the given dictionary to get relative paths

        Parameters
        ----------
        %(ExperimentsConfig.fix_paths.parameters)s

        Returns
        -------
        %(ExperimentsConfig.fix_paths.returns)s

        Notes
        -----
        d is modified in place!"""
        if root is None and project is None:
            project = d.get('project')
            if project is not None:
                root = self.projects[project]['root']
            else:
                root = d['root']
        elif root is None:
            root = self.projects[project]['root']
        elif project is None:
            pass
        paths = self.paths
        for key, val in d.items():
            if isinstance(val, dict):
                d[key] = self.rel_paths(val, root, project)
            elif key in paths:
                val = d[key]
                if isinstance(val, six.string_types) and osp.isabs(val):
                    d[key] = osp.relpath(val, root)
                elif (isinstance(utils.safe_list(val)[0], six.string_types) and
                      osp.isabs(val[0])):
                    for i in range(len(val)):
                        val[i] = osp.relpath(val[i], root)
        return d

    def save(self):
        """Save the experiment configuration

        This method stores the configuration of each of the experiments in a
        file ``'<project-dir>/.project/<experiment>.yml'``, where
        ``'<project-dir>'`` corresponds to the project directory of the
        specific ``'<experiment>'``. Furthermore it dumps all experiments to
        the :attr:`exp_file` configuration file.
        """
        for exp, d in dict(self).items():
            if isinstance(d, dict):
                project_path = self.projects[d['project']]['root']
                d = self.rel_paths(copy.deepcopy(d))
                fname = osp.join(project_path, '.project', exp + '.yml')
                if not osp.exists(osp.dirname(fname)):
                    os.makedirs(osp.dirname(fname))
                safe_dump(d, fname, default_flow_style=False)
        exp_file = self.exp_file
        # to be 100% sure we do not write to the file from multiple processes
        lock = fasteners.InterProcessLock(exp_file + '.lck')
        lock.acquire()
        safe_dump(OrderedDict((exp, val if isinstance(val, Archive) else None)
                              for exp, val in self.items()),
                  exp_file, default_flow_style=False)
        lock.release()

    def load(self):
        """Load all experiments in this dictionary into memory
        """
        for key in self:
            self[key]
        return self

    def as_ordereddict(self):
        """Convenience method to convert this object into an OrderedDict"""
        if six.PY2:
            d = OrderedDict()
            copied = dict(self)
            for key in self:
                d[key] = copied[key]
        else:
            d = OrderedDict(self)
        return d

    def items(self):
        # Reimplemented to not load all experiments under python2.7
        if six.PY2:
            d = dict(self)
            return [(key, d[key]) for key in self]
        return super(ExperimentsConfig, self).items()

    def iteritems(self):
        # Reimplemented to not load all experiments under python2.7
        if six.PY2:
            d = dict(self)
            return iter((key, d[key]) for key in self)
        return iter(super(ExperimentsConfig, self).items())

    def values(self):
        # Reimplemented to not load all experiments under python2.7
        if six.PY2:
            d = dict(self)
            return [d[key] for key in self]
        return super(ExperimentsConfig, self).values()

    def itervalues(self):
        # Reimplemented to not load all experiments under python2.7
        if six.PY2:
            d = dict(self)
            return iter(d[key] for key in self)
        return iter(super(ExperimentsConfig, self).values())

    def remove(self, experiment):
        """Remove the configuration of an experiment"""
        try:
            project_path = self.projects[self[experiment]['project']]['root']
        except KeyError:
            return
        config_path = osp.join(project_path, '.project', experiment + '.yml')
        for f in [config_path, config_path + '~', config_path + '.lck']:
            if os.path.exists(f):
                os.remove(f)
        del self[experiment]

    _note = """

    Notes
    -----
    Reimplemented to not load all experiments under python2.7"""

    for _m in ['items', 'iteritems', 'values', 'itervalues']:
        locals()[_m].__doc__ = (
            (inspect.getdoc(getattr(OrderedDict, _m, None)) or '') + _note)

    del _m, _note


class ProjectsConfig(OrderedDict):
    """The project configuration

    This class stores the configuration from the projects, where each key
    corresponds to the name of one project and the value to the corresponding
    configuration.

    Instances of this class are initialized by a file ``'projects.yml'`` in the
    configuration directory (see the :attr:`all_projects` attribute) that
    stores a mapping from project name to project directory path. The
    configuration for each individual project is then loaded from the
    ``'<project-dir>/.project/.project.yml'`` file

    Notes
    -----
    If you move one project has been moved to another directory, make sure to
    update the ``'projects.yml'`` file (the rest is updated when loading the
    configuration)
    """

    #: list of str. The keys describing paths for the model. Note that these
    #: keys here are replaced by the keys in the
    #: :attr:`~model_organization.ModelOrganizer.paths` attribute of the
    #: specific :class:`model_organization.ModelOrganizer` instance
    paths = ['expdir', 'src', 'data', 'input', 'outdata', 'outdir',
             'plot_output', 'project_output', 'forcing']

    @property
    def all_projects(self):
        """The name of the configuration file"""
        return osp.join(self.conf_dir, 'projects.yml')

    #: The path to the configuration directory
    conf_dir = None

    def __init__(self, conf_dir, d=None):
        """
        Parameters
        ----------
        conf_dir: str
            The path to the configuration directory containing a file called
            ``'projects.yml'``
        d: dict
            A dictionary to use to setup this configuration instead of loading
            them from the disk
        """
        super(ProjectsConfig, self).__init__()
        self.conf_dir = conf_dir
        fname = self.all_projects
        if osp.exists(fname):
            self.project_paths = project_paths = safe_load(fname)
        else:
            self.project_paths = project_paths = OrderedDict()
        if d is not None:
            for key, val in d.items():
                self[key] = val
        else:
            for project, path in project_paths.items():
                self[project] = self.fix_paths(safe_load(
                    osp.join(path, '.project', '.project.yml')))
                self[project]['root'] = path

    def __reduce__(self):
        return self.__class__, (self.conf_dir, OrderedDict(self))

    @docstrings.dedent
    def fix_paths(self, d, root=None, project=None):
        """
        Fix the paths in the given dictionary to get absolute paths

        Parameters
        ----------
        %(ExperimentsConfig.fix_paths.parameters)s

        Returns
        -------
        %(ExperimentsConfig.fix_paths.returns)s

        Notes
        -----
        d is modified in place!"""
        if root is None and project is None:
            project = d.get('project')
            if project is not None:
                root = self[project]['root']
            else:
                root = d['root']
        elif root is None:
            root = self[project]['root']
        elif project is None:
            pass
        paths = self.paths
        for key, val in d.items():
            if isinstance(val, dict):
                d[key] = self.fix_paths(val, root, project)
            elif key in paths:
                val = d[key]
                if isinstance(val, six.string_types) and not osp.isabs(val):
                    d[key] = osp.join(root, val)
                elif (isinstance(utils.safe_list(val)[0], six.string_types) and
                      not osp.isabs(val[0])):
                    for i in range(len(val)):
                        val[i] = osp.join(root, val[i])
        return d

    @docstrings.get_sectionsf('ExperimentsConfig.rel_paths',
                              sections=['Parameters', 'Returns'])
    @docstrings.dedent
    def rel_paths(self, d, root=None, project=None):
        """
        Fix the paths in the given dictionary to get relative paths

        Parameters
        ----------
        %(ExperimentsConfig.fix_paths.parameters)s

        Returns
        -------
        %(ExperimentsConfig.fix_paths.returns)s

        Notes
        -----
        d is modified in place!"""
        if root is None and project is None:
            project = d.get('project')
            if project is not None:
                root = self[project]['root']
            else:
                root = d['root']
        elif root is None:
            root = self[project]['root']
        elif project is None:
            pass
        paths = self.paths
        for key, val in d.items():
            if isinstance(val, dict):
                d[key] = self.rel_paths(val, root, project)
            elif key in paths:
                val = d[key]
                if isinstance(val, six.string_types) and osp.isabs(val):
                    d[key] = osp.relpath(val, root)
                elif (isinstance(utils.safe_list(val)[0], six.string_types) and
                      osp.isabs(val[0])):
                    for i in range(len(val)):
                        val[i] = osp.relpath(val[i], root)
        return d

    def save(self):
        """
        Save the project configuration

        This method dumps the configuration for each project and the project
        paths (see the :attr:`all_projects` attribute) to the hard drive
        """
        project_paths = OrderedDict()
        for project, d in OrderedDict(self).items():
            if isinstance(d, dict):
                project_path = d['root']
                fname = osp.join(project_path, '.project', '.project.yml')
                if not osp.exists(osp.dirname(fname)):
                    os.makedirs(osp.dirname(fname))
                if osp.exists(fname):
                    os.rename(fname, fname + '~')
                d = self.rel_paths(copy.deepcopy(d))
                safe_dump(d, fname, default_flow_style=False)
                project_paths[project] = project_path
            else:
                project_paths = self.project_paths[project]
        self.project_paths = project_paths
        safe_dump(project_paths, self.all_projects, default_flow_style=False)


class Config(object):
    """Configuration class for one model organizer"""

    #: Boolean that is True when the experiments shall be synched with the
    #: files on the harddisk. Use the :meth:`save` method to store the
    #: configuration
    _store = False

    #: :class:`ExperimentConfig`. The configuration of the experiments
    experiments = OrderedDict()

    #: :class:`ProjectsConfig`. The configuration of the projects
    projects = OrderedDict()

    #: :class:`OrderedDict`. The global configuration that applies to all
    #: projects
    global_config = OrderedDict()

    def __init__(self, name):
        self.name = name
        self.conf_dir = get_configdir(name)
        self.projects = ProjectsConfig(self.conf_dir)
        self.experiments = ExperimentsConfig(self.projects)
        self._globals_file = osp.join(self.conf_dir, 'globals.yml')
        if osp.exists(self._globals_file):
            self.global_config = safe_load(self._globals_file)
        else:
            self.global_config = OrderedDict()

    def remove_experiment(self, experiment):
        self.experiments.remove(experiment)

    def save(self):
        """
        Save the entire configuration files
        """
        self.projects.save()
        self.experiments.save()
        safe_dump(self.global_config, self._globals_file,
                  default_flow_style=False)
