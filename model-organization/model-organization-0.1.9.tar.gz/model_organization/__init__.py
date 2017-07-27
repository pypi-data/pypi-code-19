from __future__ import print_function, division
import os
import glob
import copy
import os.path as osp
import six
import shutil
import inspect
import re
from functools import partial
import yaml
import datetime as dt
from argparse import Namespace
import logging
from model_organization.config import (
    Config, ordered_yaml_dump, ordered_yaml_load, OrderedDict, Archive,
    safe_dump, setup_logging)
from funcargparse import FuncArgParser
import model_organization.utils as utils


docstrings = utils.docstrings


if six.PY2:
    import __builtin__ as builtins
    from os import getcwdu as getcwd
    from itertools import ifilterfalse as filterfalse
else:
    import builtins
    from os import getcwd
    from itertools import filterfalse as filterfalse


__version__ = '0.1.9'


if six.PY2:
    input = raw_input


class ModelOrganizer(object):
    """
    A class for organizing a model

    This class is indended to hold the basic methods for organizing a model and
    should be adapted to your specific needs. The important steps are

    1. specify the name of your model in the :attr:`name` attribute
    2. use the existing commands, e.g. the :meth:`setup` method or :meth:`init`
       method if you need to adapt them to your specific needs
    3. when you need your own commands,

       a. create a new method
       b. insert the name of the method in the :attr:`commands` attribute
       c. If necessary, you can use another name for the command for the
          command line parser and specify this one in the
          :attr:`parser_commands` attribute
       d. Create a ``_modify_<command>`` method (where ``<command>`` should be
          replaced by the name of the command) which accepts a
          :class:`funcargparse.FuncArgParser` as an argument to update the
          parameters for the command line parsing
       e. In your new command, call the :meth:`app_main` method which sets the
          correct experiment, etc.. You can also use the
          :meth:`get_app_main_kwargs` method to filter out the right keyword
          arguments
    4. When storing paths in the experiment configuration, we store them
       relative the project directory. In that way, we only have to modify the
       project configuration if we move our files to another place.
       Hence, if you want to use this  possibility, you should include the
       configuration keys that represent file names in the :attr:`paths`
       attribute."""

    #: the name of the application/model
    name = 'model_organizer'

    #: commands that should be accessible from the command line. Each command
    #: corresponds to one method of this class
    commands = ['setup', 'init', 'set_value', 'get_value', 'del_value', 'info',
                'unarchive', 'configure', 'archive', 'remove']

    #: mapping from the name of the parser command to the method name
    parser_commands = {}

    #: The :class:`funcargparse.FuncArgParser` to use for controlling the model
    #: from the command line. This attribute is set by the :meth:`setup_parser`
    #: method and used by the `start` method
    parser = None

    #: list of str. The keys describing paths for the model
    paths = ['expdir', 'src', 'data', 'input', 'outdata', 'outdir',
             'plot_output', 'project_output', 'forcing']

    print_ = None

    @property
    def logger(self):
        """The logger of this organizer"""
        if self._experiment:
            return logging.getLogger('.'.join([self.name, self.experiment]))
        elif self._projectname:
            return logging.getLogger('.'.join([self.name, self.projectname]))
        else:
            return logging.getLogger('.'.join([self.name]))

    @property
    def exp_config(self):
        """The configuration settings of the current experiment"""
        return self.config.experiments[self.experiment]

    @property
    def project_config(self):
        """The configuration settings of the current project of the
        experiment"""
        return self.config.projects[self.projectname]

    @property
    def global_config(self):
        """The global configuration settings"""
        return self.config.global_config

    no_modification = False

    def __init__(self, config=None):
        """
        Parameters
        ----------
        config: model_organization.config.Config
            The configuration of the organizer"""
        if config is None:
            config = Config(self.name)
            setup_logging(osp.join(config.conf_dir, 'logging.yml'),
                          env_key='LOG_' + self.name.upper())
        self.config = config
        self.config.experiments.paths = self.paths
        self.config.projects.paths = self.paths
        self._parser_set_up = False

    @classmethod
    def main(cls, args=None):
        """
        Run the organizer from the command line

        Parameters
        ----------
        name: str
            The name of the program
        args: list
            The arguments that are parsed to the argument parser
        """
        organizer = cls()
        organizer.parse_args(args)
        if not organizer.no_modification:
            organizer.config.save()

    @docstrings.get_sectionsf('ModelOrganizer.start', sections=['Returns'])
    @docstrings.dedent
    def start(self, **kwargs):
        """
        Start the commands of this organizer

        Parameters
        ----------
        ``**kwargs``
            Any keyword from the :attr:`commands` or :attr:`parser_commands`
            attribute

        Returns
        -------
        argparse.Namespace
            The namespace with the commands as given in ``**kwargs`` and the
            return values of the corresponding method"""
        ts = {}
        ret = {}
        info_parts = {'info', 'get-value', 'get_value'}
        for cmd in self.commands:
            parser_cmd = self.parser_commands.get(cmd, cmd)
            if parser_cmd in kwargs or cmd in kwargs:
                kws = kwargs.get(cmd, kwargs.get(parser_cmd))
                if isinstance(kws, Namespace):
                    kws = vars(kws)
                func = getattr(self, cmd or 'main')
                ret[cmd] = func(**kws)
                if cmd not in info_parts:
                    ts[cmd] = str(dt.datetime.now())
        exp = self._experiment
        project_parts = {'setup'}
        projectname = self._projectname
        if (projectname is not None and project_parts.intersection(ts) and
                projectname in self.config.projects):
            self.config.projects[projectname]['timestamps'].update(
                {key: ts[key] for key in project_parts.intersection(ts)})
        elif not ts:  # don't make modifications for info
            self.no_modification = True
        if exp is not None and exp in self.config.experiments:
            projectname = self.projectname
            try:
                ts.update(self.config.projects[projectname]['timestamps'])
            except KeyError:
                pass
            if not self.is_archived(exp):
                self.config.experiments[exp]['timestamps'].update(ts)
        return Namespace(**ret)

    # -------------------------------------------------------------------------
    # -------------------------------- Main -----------------------------------
    # ------------- Parts corresponding to the main functionality -------------
    # -------------------------------------------------------------------------

    _projectname = None
    _experiment = None

    @property
    def projectname(self):
        """The name of the project that is currently processed"""
        if self._projectname is None:
            exps = self.config.experiments
            if self._experiment is not None and self._experiment in exps:
                return exps[self._experiment]['project']
            try:
                self._projectname = list(self.config.projects.keys())[-1]
            except IndexError:  # no project has yet been created ever
                raise ValueError(
                    "No experiment has yet been created! Please run setup "
                    "before.")
        return self._projectname

    @projectname.setter
    def projectname(self, value):
        if value is not None:
            self._projectname = value

    @property
    def experiment(self):
        """The identifier or the experiment that is currently processed"""
        if self._experiment is None:
            self._experiment = list(self.config.experiments.keys())[-1]
        return self._experiment

    @experiment.setter
    def experiment(self, value):
        if value is not None:
            self._experiment = value

    @docstrings.get_sectionsf('ModelOrganizer.app_main')
    @docstrings.dedent
    def app_main(self, experiment=None, last=False, new=False,
                 verbose=False, verbosity_level=None, no_modification=False,
                 match=False):
        """
        The main function for parsing global arguments

        Parameters
        ----------
        experiment: str
            The id of the experiment to use
        last: bool
            If True, the last experiment is used
        new: bool
            If True, a new experiment is created
        verbose: bool
            Increase the verbosity level to DEBUG. See also `verbosity_level`
            for a more specific determination of the verbosity
        verbosity_level: str or int
            The verbosity level to use. Either one of ``'DEBUG', 'INFO',
            'WARNING', 'ERROR'`` or the corresponding integer (see pythons
            logging module)
        no_modification: bool
            If True/set, no modifications in the configuration files will be
            done
        match: bool
            If True/set, interprete `experiment` as a regular expression
            (regex) und use the matching experiment"""
        if match:
            patt = re.compile(experiment)
            matches = list(filter(patt.search, self.config.experiments))
            if len(matches) > 1:
                raise ValueError("Found multiple matches for %s: %s" % (
                    experiment, matches))
            elif len(matches) == 0:
                raise ValueError("No experiment matches %s" % experiment)
            experiment = matches[0]
        if last and self.config.experiments:
            self.experiment = None
        elif new and self.config.experiments:
            try:
                self.experiment = utils.get_next_name(self.experiment)
            except ValueError:
                raise ValueError(
                    "Could not estimate an experiment id! Please use the "
                    "experiment argument to provide an id.")
        else:
            self._experiment = experiment
        if verbose:
            verbose = logging.DEBUG
        elif verbosity_level:
            if verbosity_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
                verbose = getattr(logging, verbosity_level)
            else:
                verbose = int(verbosity_level)
        if verbose:
            logging.getLogger(
                utils.get_toplevel_module(inspect.getmodule(self))).setLevel(
                    verbose)
            self.logger.setLevel(verbose)
        self.no_modification = no_modification

    docstrings.keep_params('ModelOrganizer.app_main.parameters', 'experiment')

    def _modify_app_main(self, parser):
        to_update = {
            'projectname': dict(short='p'),
            'experiment': dict(short='id', help=docstrings.params[
                'ModelOrganizer.app_main.parameters.experiment'] +
                '. If the `init` argument is called, the `new` argument is '
                'automatically set. Otherwise, if not specified differently, '
                'the last created experiment is used.'),
            'last': dict(short='l'),
            'new': dict(short='n'),
            'verbose': dict(short='v'),
            'verbosity_level': dict(short='vl'),
            'no_modification': dict(short='nm'),
            'match': dict(short='E')}
        for key, kwargs in to_update.items():
            try:
                parser.update_arg(key, **kwargs)
            except KeyError:
                pass

    def get_app_main_kwargs(self, kwargs, keep=False):
        """
        Extract the keyword arguments for the :meth:`app_main` method

        Parameters
        ----------
        kwargs: dict
            A mapping containing keyword arguments for the :meth:`app_main`
            method
        keep: bool
            If True, the keywords are kept in the `kwargs`. Otherwise, they are
            removed

        Returns
        -------
        dict
            The keyword arguments for the :meth:`app_main` method

        Notes
        -----
        The returned keyword arguments are deleted from `kwargs`
        """
        if not keep:
            return {key: kwargs.pop(key) for key in list(kwargs)
                    if key in inspect.getargspec(self.app_main)[0]}
        else:
            return {key: kwargs[key] for key in list(kwargs)
                    if key in inspect.getargspec(self.app_main)[0]}

    # -------------------------------------------------------------------------
    # --------------------------- Infrastructure ------------------------------
    # ---------- General parts for organizing the project infrastructure ------
    # -------------------------------------------------------------------------

    @docstrings.dedent
    def setup(self, root_dir, projectname=None, link=False, **kwargs):
        """
        Perform the initial setup for the project

        Parameters
        ----------
        root_dir: str
            The path to the root directory where the experiments, etc. will
            be stored
        projectname: str
            The name of the project that shall be initialized at `root_dir`. A
            new directory will be created namely
            ``root_dir + '/' + projectname``
        link: bool
            If set, the source files are linked to the original ones instead
            of copied

        Other Parameters
        ----------------
        ``**kwargs``
            Are passed to the :meth:`app_main` method
        """
        projects = self.config.projects
        if not projects and projectname is None:
            projectname = self.name + '0'
        elif projectname is None:  # try to increment a number in the last used
            try:
                projectname = utils.get_next_name(self.projectname)
            except ValueError:
                raise ValueError(
                    "Could not estimate a project name! Please use the "
                    "projectname argument to provide a project name.")
        self.app_main(**kwargs)
        root_dir = osp.abspath(osp.join(root_dir, projectname))
        projects[projectname] = OrderedDict([
            ('name', projectname), ('root', root_dir),
            ('timestamps', OrderedDict())])
        data_dir = self.config.global_config.get(
            'data', osp.join(root_dir, 'data'))
        projects[projectname]['data'] = data_dir
        self.projectname = projectname
        self.logger.info("Initializing project %s", projectname)
        self.logger.debug("    Creating root directory %s", root_dir)
        if not osp.exists(root_dir):
            os.makedirs(root_dir)
        return root_dir

    def _modify_setup(self, parser):
        self._modify_app_main(parser)

    @docstrings.dedent
    def init(self, projectname=None, description=None, **kwargs):
        """
        Initialize a new experiment

        Parameters
        ----------
        projectname: str
            The name of the project that shall be used. If None, the last one
            created will be used
        description: str
            A short summary of the experiment
        ``**kwargs``
            Keyword arguments passed to the :meth:`app_main` method

        Notes
        -----
        If the experiment is None, a new experiment will be created
        """
        self.app_main(**kwargs)
        experiments = self.config.experiments
        experiment = self._experiment
        if experiment is None and not experiments:
            experiment = self.name + '_exp0'
        elif experiment is None:
            try:
                experiment = utils.get_next_name(self.experiment)
            except ValueError:
                raise ValueError(
                    "Could not estimate an experiment id! Please use the "
                    "experiment argument to provide an id.")
        self.experiment = experiment
        if self.is_archived(experiment):
            raise ValueError(
                "The specified experiment has already been archived! Run "
                "``%s -id %s unarchive`` first" % (self.name, experiment))
        if projectname is None:
            projectname = self.projectname
        else:
            self.projectname = projectname
        self.logger.info("Initializing experiment %s of project %s",
                         experiment, projectname)
        exp_dict = experiments.setdefault(experiment, OrderedDict())
        if description is not None:
            exp_dict['description'] = description
        exp_dict['project'] = projectname
        exp_dict['expdir'] = exp_dir = osp.join('experiments', experiment)
        exp_dir = osp.join(self.config.projects[projectname]['root'], exp_dir)
        exp_dict['timestamps'] = OrderedDict()

        if not os.path.exists(exp_dir):
            self.logger.debug("    Creating experiment directory %s", exp_dir)
            os.makedirs(exp_dir)
        self.fix_paths(exp_dict)
        return exp_dict

    def _modify_init(self, parser):
        self._modify_app_main(parser)
        parser.update_arg('description', short='d')

    @docstrings.dedent
    def archive(self, odir=None, aname=None, fmt=None, projectname=None,
                experiments=None, current_project=False, no_append=False,
                no_project_paths=False, exclude=None, keep_exp=False,
                rm_project=False, dry_run=False, dereference=False, **kwargs):
        """
        Archive one or more experiments or a project instance

        This method may be used to archive experiments in order to minimize the
        amount of necessary configuration files

        Parameters
        ----------
        odir: str
            The path where to store the archive
        aname: str
            The name of the archive (minus any format-specific extension). If
            None, defaults to the projectname
        fmt: { 'gztar' | 'bztar' | 'tar' | 'zip' }
            The format of the archive. If None, it is tested whether an
            archived with the name specified by `aname` already exists and if
            yes, the format is inferred, otherwise ``'tar'`` is used
        projectname: str
            If provided, the entire project is archived
        experiments: str
            If provided, the given experiments are archived. Note that an error
            is raised if they belong to multiple project instances
        current_project: bool
            If True, `projectname` is set to the current project
        no_append: bool
            It True and the archive already exists, it is deleted
        no_project_paths: bool
            If True, paths outside the experiment directories are neglected
        exclude: list of str
            Filename patterns to ignore (see :func:`glob.fnmatch.fnmatch`)
        keep_exp: bool
            If True, the experiment directories are not removed and no
            modification is made in the configuration
        rm_project: bool
            If True, remove all the project files
        dry_run: bool
            If True, set, do not actually make anything
        dereference: bool
            If set, dereference symbolic links. Note: This is automatically set
            for ``fmt=='zip'``
        """
        fnmatch = glob.fnmatch.fnmatch

        def to_exclude(fname):
            if exclude and (fnmatch(exclude, fname) or
                            fnmatch(exclude, osp.basename(fname))):
                return True

        def do_nothing(path, file_obj):
            return

        def tar_add(path, file_obj):
            file_obj.add(path, self.relpath(path), exclude=to_exclude)

        def zip_add(path, file_obj):
            # ziph is zipfile handle
            for root, dirs, files in os.walk(path):
                for f in files:
                    abs_file = os.path.join(root, f)
                    if not to_exclude(abs_file):
                        file_obj.write(abs_file, self.relpath(abs_file))

        self.app_main(**kwargs)
        logger = self.logger
        all_exps = self.config.experiments
        if current_project or projectname is not None:
            if current_project:
                projectname = self.projectname
            experiments = list(
                self.config.experiments.project_map[projectname])
            if not experiments:
                raise ValueError(
                    "Could not find any unarchived experiment for %s" % (
                        projectname))
        elif experiments is None:
            experiments = [self.experiment]
        already_archived = list(filter(self.is_archived, experiments))
        if already_archived:
            raise ValueError(
                "The experiments %s have already been archived or are not "
                "existent!" % ', '.join(
                    already_archived))
        if projectname is None:
            projectnames = {all_exps[exp]['project'] for exp in experiments}
            if len(projectnames) > 1:
                raise ValueError(
                    "Experiments belong to multiple projects: %s" % (
                        ', '.join(projectnames)))
            projectname = next(iter(projectnames))

        self.projectname = projectname
        self.experiment = experiments[-1]

        exps2archive = OrderedDict(
            (exp, all_exps[exp]) for exp in experiments)
        project_config = self.config.projects[projectname]

        ext_map, fmt_map = self._archive_extensions()
        if aname is None:
            aname = projectname
        if fmt is None:
            ext, fmt = next(
                (t for t in fmt_map.items() if osp.exists(aname + t[0])),
                ['.tar', 'tar'])
        else:
            ext = fmt_map[fmt]
        if odir is None:
            odir = getcwd()
        archive_name = osp.join(odir, aname + ext)
        exists = osp.exists(archive_name)
        if exists and no_append:
            logger.debug('Removing existing archive %s' % archive_name)
            os.remove(archive_name)
            exists = False
        elif exists and fmt not in ['tar', 'zip']:
            raise ValueError(
                "'Cannot append to %s because this is only possible for 'tar' "
                "and 'zip' extension. Not %s" % (archive_name, fmt))
        logger.info('Archiving to %s', archive_name)

        paths = self._get_all_paths(exps2archive)
        root_dir = self.config.projects[projectname]['root']
        check_path = partial(utils.dir_contains, root_dir)
        not_included = OrderedDict([
            (key, list(filterfalse(check_path, utils.safe_list(val))))
            for key, val in paths.items()])

        for key, key_paths in not_included.items():
            for p in key_paths:
                logger.warn(
                    '%s for key %s lies outside the project directory and '
                    'will not be included in the archive!', p, key)
        modes = {'bztar': 'w:bz2', 'gztar': 'w:gz', 'tar': 'w', 'zip': 'w'}
        mode = 'a' if exists else modes[fmt]
        atype = 'zip' if fmt == 'zip' else 'tar'
        if dry_run:
            add_dir = do_nothing
            file_obj = None
        elif atype == 'zip':
            import zipfile
            add_dir = zip_add
            file_obj = zipfile.ZipFile(archive_name, mode)
        else:
            import tarfile
            add_dir = tar_add
            file_obj = tarfile.open(archive_name, mode,
                                    dereference=dereference)
        for exp in experiments:
            exp_dir = exps2archive[exp]['expdir']
            logger.debug('Adding %s', exp_dir)
            add_dir(exp_dir, file_obj)

        now = str(dt.datetime.now())  # current time

        # configuration directory
        config_dir = osp.join(root_dir, '.project')
        if not dry_run and not osp.exists(config_dir):
            os.makedirs(config_dir)
        for exp in experiments:
            conf_file = osp.join(config_dir, exp + '.yml')
            logger.debug('Store %s experiment config to %s', exp, conf_file)
            if not dry_run:
                exps2archive[exp].setdefault('timestamps', {})
                exps2archive[exp]['timestamps']['archive'] = now
                with open(osp.join(config_dir, exp + '.yml'), 'w') as f:
                    ordered_yaml_dump(self.rel_paths(
                        copy.deepcopy(exps2archive[exp])), f)
        # project configuration file
        conf_file = osp.join(config_dir, '.project.yml')
        logger.debug('Store %s project config to %s', projectname, conf_file)
        if not dry_run:
            safe_dump(project_config, conf_file)

        logger.debug('Add %s to archive', config_dir)
        add_dir(config_dir, file_obj)

        if not no_project_paths:
            for dirname in os.listdir(root_dir):
                if osp.basename(dirname) not in ['experiments', '.project']:
                    logger.debug('Adding %s', osp.join(root_dir, dirname))
                    add_dir(osp.join(root_dir, dirname), file_obj)
        if not keep_exp:
            for exp in experiments:
                exp_dir = exps2archive[exp]['expdir']
                logger.debug('Removing %s', exp_dir)
                if not dry_run:
                    all_exps[exp] = a = Archive(archive_name)
                    a.project = projectname
                    a.time = now
                    shutil.rmtree(exp_dir)
        if rm_project:
            logger.debug('Removing %s', root_dir)
            if not dry_run:
                shutil.rmtree(root_dir)
        if not dry_run:
            file_obj.close()

    def _modify_archive(self, parser):
        self._modify_app_main(parser)
        parser.update_arg('odir', short='d')
        parser.update_arg('aname', short='f')
        parser.update_arg('fmt', choices=['bztar', 'gztar', 'tar', 'zip'])
        parser.update_arg(
            'experiments', short='ids', metavar='exp1,[exp2[,...]]]',
            type=lambda s: s.split(','))
        parser.update_arg('current_project', short='P')
        parser.update_arg('no_append', short='na')
        parser.update_arg('no_project_paths', short='np')
        parser.update_arg('exclude', short='e')
        parser.update_arg('keep_exp', short='k', long='keep')
        parser.update_arg('rm_project', short='rm')
        parser.update_arg('dry_run', short='n')
        parser.update_arg('dereference', short='L')
        return parser

    @docstrings.dedent
    def unarchive(self, experiments=None, archive=None, complete=False,
                  project_data=False, replace_project_config=False, root=None,
                  projectname=None, fmt=None, force=False, **kwargs):
        """
        Extract archived experiments

        Parameters
        ----------
        experiments: list of str
            The experiments to extract. If None the current experiment is used
        archive: str
            The path to an archive to extract the experiments from. If None,
            we assume that the path to the archive has been stored in the
            configuration when using the :meth:`archive` command
        complete: bool
            If True, archives are extracted completely, not only the experiment
            (implies ``project_data = True``)
        project_data: bool
            If True, the data for the project is extracted as well
        replace_project_config: bool
            If True and the project does already exist in the configuration, it
            is updated with what is stored in the archive
        root: str
            An alternative root directory to use. Otherwise the experiment will
            be exctracted to

            1. the root directory specified in the configuration files
               (if the project exists in it) and `replace_project_config` is
               False
            2. the root directory as stored in the archive
        projectname: str
            The projectname to use. If None, use the one specified in the
            archive
        fmt: { 'gztar' | 'bztar' | 'tar' | 'zip' }
            The format of the archive. If None, it is inferred
        force: bool
            If True, force to overwrite the configuration of all experiments
            from what is stored in `archive`. Otherwise, the configuration of
            the experiments in `archive` are only used if missing in the
            current configuration
        """
        def extract_file(path):
            if atype == 'zip':
                return file_obj.open(path)
            else:
                return file_obj.extractfile(path)

        self.app_main(**kwargs)

        logger = self.logger

        project_config = None

        all_exps = self.config.experiments
        all_projects = self.config.projects
        # ---- set archive
        # if archive is None, check for the archives listed in `experiments`
        # and raise an error if one has not been archived yet or if they belong
        # to different files
        if archive is None:
            # ---- set experiments
            # if experiments is None, use the current experiment. If complete
            # is True, this will be replaced below
            if experiments is None:
                experiments = [self.experiment]
            archives = list(filter(utils.isstring,
                                   map(self.is_archived, experiments)))
            if len(archives) > 1:
                raise ValueError(
                    'The given experiments belong to multiple archives %s!' % (
                        ', '.join(archives)))
            archive = next(iter(archives))
        elif not complete and experiments is None:
            experiments = [self.experiment]

        logger.info('Unarchiving from %s', archive)

        # --- infer compression type
        ext_map, fmt_map = self._archive_extensions()
        if fmt is None:
            try:
                fmt = next(fmt for ext, fmt in ext_map.items()
                           if archive.endswith(ext))
            except StopIteration:
                raise IOError(
                    "Could not infer archive format of {}! Please specify it "
                    "manually using the `fmt` parameter!".format(archive))

        # if no root directory is specified but a projectname, we take the root
        # directory from the configuration if, and only if, the configuration
        # should not be replaced
        if (root is None and projectname is not None and
                not replace_project_config):
            all_projects.get(projectname, {}).get('root')

        # ---- open the archive
        modes = {'bztar': 'r:bz2', 'gztar': 'r:gz', 'tar': 'r', 'zip': 'r'}
        atype = 'zip' if fmt == 'zip' else 'tar'
        if atype == 'tar':
            from tarfile import open as open_file
        else:
            from zipfile import ZipFile as open_file
        file_obj = open_file(archive, modes[fmt])

        # ---- if root is None, get it from the archive
        if root is None:
            fp = extract_file(osp.join('.project', '.project.yml'))
            try:
                project_config = ordered_yaml_load(fp)
                # use the projectname in archive only, if nothing is specified
                # here
                projectname = projectname or project_config['name']
            except:
                raise
            finally:
                fp.close()
            # if the projectname is existent in our configuration and already
            # specified, use this one
            if (projectname in self.config.projects and
                    not replace_project_config):
                root = self.config.projects[projectname].get('root')
            else:
                root = project_config.get('root')
        # if we still don't have it, because it was not specified in the
        # archive or the configuration, raise an error
        if root is None:
            raise ValueError("Could not find a root directory path for the "
                             "project. Please specify manually!")

        logger.info('Root directory for the project: %s', root)

        t = str(dt.datetime.now())  # time at the beginning of extraction

        config_files = []

        def fname_filter(m):
            fname = get_fname(m)
            if (dir_contains('.project', fname) and
                    not osp.basename(fname).startswith('.')):
                config_files.append(fname)
            return (
                complete or fname in config_files or
                (project_data and not dir_contains('experiments', fname)) or
                any(dir_contains(d, fname) for d in dirs))

        if not complete:
            dirs = [osp.join('experiments', exp) for exp in experiments]
            dirs.append(osp.join('.project', '.project.yml'))
        dir_contains = partial(utils.dir_contains, exists=False)
        if atype == 'zip':
            def get_fname(m):
                return m
            members = list(filter(fname_filter, file_obj.namelist()))
        else:
            def get_fname(m):
                return m.name
            members = list(filter(fname_filter, file_obj.getmembers()))
        logger.debug('Extracting %s files from archive to %s',
                     len(members), root)
        file_obj.extractall(root, members=members)

        # if the project_config yet not has been red, read it now
        if not project_config:
            with open(osp.join(root, '.project', '.project.yml')) as fp:
                project_config = ordered_yaml_load(fp)
            if projectname:
                project_config['name'] = projectname
            else:
                projectname = project_config['name']
        if projectname not in all_projects or replace_project_config:
            all_projects[projectname] = project_config
        else:
            all_projects[projectname]['root'] = root

        # get all experiment names in the archive
        arc_exps = [osp.splitext(osp.basename(f))[0] for f in config_files]
        if complete:
            experiments = arc_exps
        else:
            for exp in filter(lambda exp: exp not in arc_exps, experiments[:]):
                logger.warn('Experiment %s was not found in archive!', exp)
                experiments.remove(exp)
        for exp in experiments:
            if force or exp not in self.config.experiments or self.is_archived(
                    exp):
                with open(osp.join(root, '.project', exp + '.yml')) as fexp:
                    exp_config = ordered_yaml_load(fexp)
                logger.debug('Update configuration for %s', exp)
                all_exps[exp] = self.fix_paths(exp_config)
            else:
                exp_config = all_exps[exp]
            exp_config['project'] = projectname
            exp_config['timestamps']['unarchive'] = t

        logger.debug('Done.')

    def _modify_unarchive(self, parser):
        self._modify_app_main(parser)
        parser.update_arg(
            'experiments', short='ids', metavar='exp1,[exp2[,...]]]',
            type=lambda s: s.split(','))
        parser.update_arg('archive', short='f', long='file')
        parser.update_arg('complete', short='a', long='all')
        parser.update_arg('project_data', short='pd')
        parser.update_arg('replace_project_config', short='P')
        parser.update_arg('root', short='d')
        parser.update_arg('force', short=None)
        return parser

    @docstrings.dedent
    def remove(self, projectname=None, complete=False,
               yes=False, all_projects=False, **kwargs):
        """
        Delete an existing experiment and/or projectname

        Parameters
        ----------
        projectname: str
            The name for which the data shall be removed. If True, the
            project will be determined by the experiment. If not None, all
            experiments for the given project will be removed.
        complete: bool
            If set, delete not only the experiments and config files, but also
            all the project files
        yes: bool
            If True/set, do not ask for confirmation
        all_projects: bool
            If True/set, all projects are removed

        Warnings
        --------
        This will remove the entire folder and all the related informations in
        the configurations!
        """
        self.app_main(**kwargs)
        if projectname in self.config.projects:
            self.projectname = projectname
        all_experiments = self.config.experiments
        projects_info = self.config.projects
        if all_projects:
            experiments = list(all_experiments.keys())
            projects = list(projects_info.keys())
        elif projectname is not None:
            experiments = all_experiments.project_map[projectname]
            projects = [self.projectname]
        else:
            experiments = [self.experiment]
            projects = [self.projectname]
        if not yes:
            if complete:
                msg = ('Are you sure to remove all experiments (%s) and '
                       'directories for the project instances %s?' % (
                           ', '.join(experiments), ', '.join(projects)))
            else:
                msg = ('Are you sure to remove the experiments %s' % (
                    ', '.join(experiments)))
            answer = ''
            while answer.lower() not in ['n', 'no', 'y', 'yes']:
                answer = input(msg + '[y/n] ')
            if answer.lower() in ['n', 'no']:
                return
        for exp in experiments:
            if not self.is_archived(exp):
                self.logger.debug("Removing experiment %s", exp)
                try:
                    exp_dict = self.fix_paths(all_experiments[exp])
                except KeyError:  # experiment has been removed already
                    pass
                else:
                    if osp.exists(exp_dict['expdir']):
                        shutil.rmtree(exp_dict['expdir'])
                    self.config.remove_experiment(exp)

        if complete:
            for project in projects:
                self.logger.debug("Removing project %s", project)
                projectdir = projects_info.pop(project)['root']
                if osp.exists(projectdir):
                    shutil.rmtree(projectdir)

    def _modify_remove(self, parser):
        self._modify_app_main(parser)
        parser.update_arg('complete', short='a', long='all')
        parser.update_arg('yes', short='y')
        parser.update_arg('all_projects', short='ap')
        parser.update_arg('projectname', const=True, nargs='?', help=(
            'The name for which the data shall be removed. If set without, '
            'argument, the project will be determined by the experiment. If '
            'specified, all experiments for the given project will be '
            'removed.'))

    # -------------------------------------------------------------------------
    # -------------------------- Information ----------------------------------
    # ---------- Parts for getting information from the configuration ---------
    # -------------------------------------------------------------------------

    @docstrings.get_sectionsf('ModelOrganizer.info')
    @docstrings.dedent
    def info(self, exp_path=False, project_path=False, global_path=False,
             config_path=False, complete=False, no_fix=False,
             on_projects=False, on_globals=False, projectname=None,
             return_dict=False, insert_id=True, only_keys=False,
             archives=False, **kwargs):
        """
        Print information on the experiments

        Parameters
        ----------
        exp_path: bool
            If True/set, print the filename of the experiment configuration
        project_path: bool
            If True/set, print the filename on the project configuration
        global_path: bool
            If True/set, print the filename on the global configuration
        config_path: bool
            If True/set, print the path to the configuration directory
        complete: bool
            If True/set, the information on all experiments are printed
        no_fix: bool
            If set, paths are given relative to the root directory of the
            project
        on_projects: bool
            If set, show information on the projects rather than the
            experiment
        on_globals: bool
            If set, show the global configuration settings
        projectname: str
            The name of the project that shall be used. If provided and
            `on_projects` is not True, the information on all experiments for
            this project will be shown
        return_dict: bool
            If True, the dictionary is returned instead of printed
        insert_id: bool
            If True and neither `on_projects`, nor `on_globals`, nor
            `projectname` is given, the experiment id is inserted in the
            dictionary
        only_keys: bool
            If True, only the keys of the given dictionary are printed
        archives: bool
            If True, print the archives and the corresponding experiments for
            the specified project
        """
        self.app_main(**kwargs)

        def get_archives(project):
            ret = OrderedDict()
            for exp, a in self.config.experiments.items():
                if self.is_archived(exp) and a.project == project:
                    ret.setdefault(str(a), []).append(exp)
            return ret

        paths = OrderedDict([
            ('conf_dir', config_path), ('_globals_file', global_path)])
        if any(paths.values()):
            for key, val in paths.items():
                if val:
                    return (self.print_ or six.print_)(getattr(
                        self.config, key))
            return
        if archives:
            base = OrderedDict()
            current = projectname or self.projectname
            if complete:
                for project in self.config.projects.keys():
                    d = get_archives(project)
                    if d:
                        base[project] = d
            else:
                base[current] = get_archives(current)
        elif exp_path:
            current = self.experiment
            base = self.config.experiments.exp_files
        elif project_path:
            current = self.projectname
            base = OrderedDict(
                (key, osp.join(val, '.project', '.project.yml'))
                for key, val in self.config.projects.project_paths.items())
        elif on_globals:
            complete = True
            no_fix = True
            base = self.config.global_config
        elif on_projects:
            base = OrderedDict(self.config.projects)
            current = projectname or self.projectname
        else:
            current = self.experiment
            if projectname is None:
                if insert_id:
                    base = copy.deepcopy(self.config.experiments)
                    if not complete:
                        base[current]['id'] = current
                        if six.PY3:
                            base[current].move_to_end('id', last=False)
                else:
                    base = self.config.experiments
                if not only_keys:
                    # make sure the experiments are loaded
                    if complete:
                        base.load()
                    else:
                        base[current]
                # convert to an OrderedDict
                base = base.as_ordereddict()
            else:
                base = OrderedDict(
                    (exp, self.config.experiments[exp])
                    for exp in self.config.experiments.project_map[projectname]
                    )
                complete = True

        if no_fix and not (archives or on_globals):
            for key, val in base.items():
                if isinstance(val, dict):
                    base[key] = self.rel_paths(copy.deepcopy(val))
        if not complete:
            base = base[current]
        if only_keys:
            base = list(base.keys())
        if not return_dict:
            if isinstance(base, six.string_types):
                ret = base
            else:
                ret = ordered_yaml_dump(base, default_flow_style=False)
            return (self.print_ or six.print_)(ret.rstrip())
        else:
            return base

    def _modify_info(self, parser):
        self._modify_app_main(parser)
        parser.update_arg('exp_path', short='ep')
        parser.update_arg('project_path', short='pp')
        parser.update_arg('global_path', short='gp')
        parser.update_arg('config_path', short='cp')
        parser.update_arg('no_fix', short='nf')
        parser.update_arg('complete', short='a', long='all', dest='complete')
        parser.update_arg('on_projects', short='P')
        parser.update_arg('on_globals', short='g', long='globally',
                          dest='on_globals')
        parser.update_arg('only_keys', short='k')
        parser.update_arg('archives', short='arc')
        parser.pop_arg('return_dict')
        parser.pop_arg('insert_id')

    docstrings.keep_params('ModelOrganizer.info.parameters',
                           'exp_path', 'project_path')
    docstrings.keep_params('ModelOrganizer.info.parameters',
                           'complete', 'on_projects', 'on_globals',
                           'projectname')
    # those are far too many, so we store them in another key
    docstrings.params['ModelOrganizer.info.common_params'] = (
        docstrings.params.pop(
            'ModelOrganizer.info.parameters.complete|on_projects|'
            'on_globals|projectname'))
    docstrings.keep_params('ModelOrganizer.info.parameters', 'no_fix',
                           'only_keys', 'archives')

    @docstrings.dedent
    def get_value(self, keys, exp_path=False, project_path=False,
                  complete=False, on_projects=False, on_globals=False,
                  projectname=None, no_fix=False, only_keys=False, base='',
                  return_list=False, archives=False, **kwargs):
        """
        Get one or more values in the configuration

        Parameters
        ----------
        keys: list of str
            A list of keys to get the values of. %(get_value_note)s
        %(ModelOrganizer.info.parameters.exp_path|project_path)s
        %(ModelOrganizer.info.common_params)s
        %(ModelOrganizer.info.parameters.no_fix|only_keys|archives)s
        base: str
            A base string that shall be put in front of each key in `values` to
            avoid typing it all the time
        return_list: bool
            If True, the list of values corresponding to `keys` is returned,
            otherwise they are printed separated by a new line to the standard
            output
        """
        def pretty_print(val):
            if isinstance(val, dict):
                if only_keys:
                    val = list(val.keys())
                return ordered_yaml_dump(
                    val, default_flow_style=False).rstrip()
            return str(val)
        config = self.info(exp_path=exp_path, project_path=project_path,
                           complete=complete, on_projects=on_projects,
                           on_globals=on_globals, projectname=projectname,
                           no_fix=no_fix, return_dict=True, insert_id=False,
                           archives=archives, **kwargs)
        ret = [0] * len(keys)
        for i, key in enumerate(keys):
            if base:
                key = base + key
            key, sub_config = utils.go_through_dict(key, config)
            ret[i] = sub_config[key]
        if return_list:
            return ret
        return (self.print_ or six.print_)('\n'.join(map(pretty_print, ret)))

    def _modify_get_value(self, parser):
        self._modify_app_main(parser)
        parser.update_arg('keys', metavar='level0.level1.level...')
        parser.update_arg('exp_path', short='ep')
        parser.update_arg('project_path', short='pp')
        parser.update_arg('complete', short='a', long='all', dest='complete')
        parser.update_arg('on_projects', short='P')
        parser.update_arg('on_globals', short='g', long='globally',
                          dest='on_globals')
        parser.update_arg('no_fix', short='nf')
        parser.update_arg('only_keys', short='k')
        parser.update_arg('base', short='b')
        parser.update_arg('archives', short='arc')
        parser.pop_arg('return_list')

    @docstrings.dedent
    def del_value(self, keys, complete=False, on_projects=False,
                  on_globals=False, projectname=None, base='', dtype=None,
                  **kwargs):
        """
        Delete a value in the configuration

        Parameters
        ----------
        keys: list of str
            A list of keys to be deleted. %(get_value_note)s
        %(ModelOrganizer.info.common_params)s
        base: str
            A base string that shall be put in front of each key in `values` to
            avoid typing it all the time
        """
        config = self.info(complete=complete, on_projects=on_projects,
                           on_globals=on_globals, projectname=projectname,
                           return_dict=True, insert_id=False, **kwargs)
        for key in keys:
            if base:
                key = base + key
            key, sub_config = utils.go_through_dict(key, config)
            del sub_config[key]

    def _modify_del_value(self, parser):
        self._modify_app_main(parser)
        parser.update_arg('keys', metavar='level0.level1.level...')
        parser.update_arg('complete', short='a', long='all', dest='complete')
        parser.update_arg('on_projects', short='P')
        parser.update_arg('on_globals', short='g', long='globally',
                          dest='on_globals')
        parser.update_arg('base', short='b')

    # -------------------------------------------------------------------------
    # -------------------------- Configuration --------------------------------
    # ------------------ Parts for configuring the organizer ------------------
    # -------------------------------------------------------------------------

    @docstrings.get_sectionsf('ModelOrganizer.configure')
    @docstrings.dedent
    def configure(self, global_config=False, project_config=False, ifile=None,
                  forcing=None, serial=False, nprocs=None, update_from=None,
                  **kwargs):
        """
        Configure the project and experiments

        Parameters
        ----------
        global_config: bool
            If True/set, the configuration are applied globally (already
            existing and configured experiments are not impacted)
        project_config: bool
            Apply the configuration on the entire project instance instead of
            only the single experiment (already existing and configured
            experiments are not impacted)
        ifile: str
            The input file for the project. Must be a netCDF file with
            population data
        forcing: str
            The input file for the project containing variables with population
            evolution information. Possible variables in the netCDF file are
            *movement* containing the number of people to move and *change*
            containing the population change (positive or negative)
        serial: bool
            Do the parameterization always serial (i.e. not in parallel on
            multiple processors). Does automatically impact global settings
        nprocs: int or 'all'
            Maximum number of processes to when making the parameterization in
            parallel. Does automatically impact global settings and disables
            `serial`
        update_from: str
            Path to a yaml configuration file to update the specified
            configuration with it
        ``**kwargs``
            Other keywords for the :meth:`app_main` method"""
        if global_config:
            d = self.config.global_config
        elif project_config:
            self.app_main(**kwargs)
            d = self.config.projects[self.projectname]
        else:
            d = self.config.experiments[self.experiment]

        if ifile is not None:
            d['input'] = osp.abspath(ifile)
        if forcing is not None:
            d['forcing'] = osp.abspath(forcing)

        if update_from is not None:
            with open('update_from') as f:
                d.update(yaml.load(f))

        global_config = self.config.global_config
        if serial:
            global_config['serial'] = True
        elif nprocs:
            nprocs = int(nprocs) if nprocs != 'all' else nprocs
            global_config['serial'] = False
            global_config['nprocs'] = nprocs

    def _modify_configure(self, parser):
        parser.update_arg('global_config', short='g', long='globally',
                          dest='global_config')
        parser.update_arg('project_config', short='p', long='project',
                          dest='project_config')
        parser.update_arg('ifile', short='i')
        parser.update_arg('forcing', short='f')
        parser.update_arg('serial', short='s')
        parser.update_arg('nprocs', short='n')

    @docstrings.get_sectionsf('ModelOrganizer.set_value')
    @docstrings.dedent
    def set_value(self, items, complete=False, on_projects=False,
                  on_globals=False, projectname=None, base='', dtype=None,
                  **kwargs):
        """
        Set a value in the configuration

        Parameters
        ----------
        items: dict
            A dictionary whose keys correspond to the item in the configuration
            and whose values are what shall be inserted. %(get_value_note)s
        %(ModelOrganizer.info.common_params)s
        base: str
            A base string that shall be put in front of each key in `values` to
            avoid typing it all the time
        dtype: str
            The name of the data type or a data type to cast the value to
        """
        def identity(val):
            return val
        config = self.info(complete=complete, on_projects=on_projects,
                           on_globals=on_globals, projectname=projectname,
                           return_dict=True, insert_id=False, **kwargs)
        if isinstance(dtype, six.string_types):
            dtype = getattr(builtins, dtype)
        elif dtype is None:
            dtype = identity
        for key, value in six.iteritems(dict(items)):
            if base:
                key = base + key
            key, sub_config = utils.go_through_dict(key, config,
                                                    setdefault=OrderedDict)
            if key in self.paths:
                if isinstance(value, six.string_types):
                    value = osp.abspath(value)
                else:
                    value = list(map(osp.abspath, value))
            sub_config[key] = dtype(value)

    def _modify_set_value(self, parser):
        self._modify_app_main(parser)
        parser.update_arg(
            'items', nargs='+', type=lambda s: s.split('='),
            metavar='level0.level1.level...=value', help="""
                The key-value pairs to set. If the configuration goes some
                levels deeper, keys may be separated by a ``'.'`` (e.g.
                ``'namelists.weathergen'``). Hence, to insert a  ``','``, it
                must be escaped by a preceeding ``'\'``.""")
        parser.update_arg('complete', short='a', long='all', dest='complete')
        parser.update_arg('on_projects', short='P')
        parser.update_arg('on_globals', short='g', long='globally',
                          dest='on_globals')
        parser.update_arg('base', short='b')
        parser.update_arg('dtype', short='dt', choices=dir(builtins))

    # -------------------------------------------------------------------------
    # -------------------------- Paths management -----------------------------
    # -------- Helper methods to cope relative and absolute paths -------------
    # -------------------------------------------------------------------------

    @docstrings.dedent
    def fix_paths(self, *args, **kwargs):
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
        return self.config.experiments.fix_paths(*args, **kwargs)

    @docstrings.dedent
    def rel_paths(self, *args, **kwargs):
        """
        Fix the paths in the given dictionary to get relative paths

        Parameters
        ----------
        %(ExperimentsConfig.rel_paths.parameters)s

        Returns
        -------
        %(ExperimentsConfig.rel_paths.returns)s

        Notes
        -----
        d is modified in place!"""
        return self.config.experiments.rel_paths(*args, **kwargs)

    def _get_all_paths(self, d, base=''):
        ret = OrderedDict()
        paths = self.paths
        if base:
            base += '.'
        for key, val in d.items():
            if isinstance(val, dict):
                for key2, val2 in self._get_all_paths(val, str(key)).items():
                    ret[base + key2] = val2
            elif key in paths:
                ret[base + key] = utils.safe_list(val)
        return ret

    def abspath(self, path, project=None, root=None):
        """Returns the path from the current working directory

        We only store the paths relative to the root directory of the project.
        This method fixes those path to be applicable from the working
        directory

        Parameters
        ----------
        path: str
            The original path as it is stored in the configuration
        project: str
            The project to use. If None, the :attr:`projectname` attribute is
            used
        root: str
            If not None, the root directory of the project

        Returns
        -------
        str
            The path as it is accessible from the current working directory"""
        if root is None:
            root = self.config.projects[project or self.projectname]['root']
        return osp.join(root, path)

    def relpath(self, path, project=None, root=None):
        """Returns the relative path from the root directory of the project

        We only store the paths relative to the root directory of the project.
        This method gives you this path from a path that is accessible from the
        current working directory

        Parameters
        ----------
        path: str
            The original path accessible from the current working directory
        project: str
            The project to use. If None, the :attr:`projectname` attribute is
            used
        root: str
            If not None, the root directory of the project

        Returns
        -------
        str
            The path relative from the root directory"""
        if root is None:
            root = self.config.projects[project or self.projectname]['root']
        return osp.relpath(path, root)

    # -------------------------------------------------------------------------
    # -------------------------- Parser management ----------------------------
    # -------- Methods to organizer the parsing from command line -------------
    # -------------------------------------------------------------------------

    def setup_parser(self, parser=None, subparsers=None):
        """
        Create the argument parser for this instance

        This method uses the functions defined in the :attr:`commands`
        attribute to create a command line utility via the
        :class:`FuncArgParser` class. Each command in the :attr:`commands`
        attribute is interpreted as on subparser and setup initially via the
        :meth:`FuncArgParser.setup_args` method. You can modify the parser
        for each command *cmd* by including a ``_modify_cmd`` method that
        accepts the subparser as an argument

        Parameters
        ----------
        parser: FuncArgParser
            The parser to use. If None, a new one will be created
        subparsers: argparse._SubParsersAction
            The subparsers to use. If None, the
            :attr:`~ArgumentParser.add_subparser` method from `parser` will be
            called

        Returns
        -------
        FuncArgParser
            The created command line parser or the given `parser`
        argparse._SubParsersAction
            The created subparsers action or the given `subparsers`
        dict
            A mapping from command name in the :attr:`commands` attribute to
            the corresponding command line parser

        See Also
        --------
        parse_args"""
        commands = self.commands[:]
        parser_cmds = self.parser_commands.copy()

        if subparsers is None:
            if parser is None:
                parser = FuncArgParser(self.name)
            subparsers = parser.add_subparsers(chain=True)

        ret = {}
        for i, cmd in enumerate(commands[:]):
            func = getattr(self, cmd)
            parser_cmd = parser_cmds.setdefault(cmd, cmd.replace('_', '-'))
            ret[cmd] = sp = parser.setup_subparser(
                func, name=parser_cmd, return_parser=True)
            sp.setup_args(func)
            modifier = getattr(self, '_modify_' + cmd, None)
            if modifier is not None:
                modifier(sp)
        self.parser_commands = parser_cmds
        parser.setup_args(self.app_main)
        self._modify_app_main(parser)
        self.parser = parser
        self.subparsers = ret
        return parser, subparsers, ret

    def _finish_parser(self):
        """Create the arguments of the :attr:`parser` attribute"""
        # create the arguments
        self.parser.create_arguments(True)
        self._parser_set_up = True

    @docstrings.dedent
    def parse_args(self, args=None):
        """
        Parse the arguments from the command line (or directly) to the parser
        of this organizer

        Parameters
        ----------
        args: list
            A list of arguments to parse. If None, the :attr:`sys.argv`
            argument is used

        Returns
        -------
        %(ModelOrganizer.start.returns)s
        """
        if self.parser is None:
            self.setup_parser()
        if not self._parser_set_up:
            self._finish_parser()
        ret = self.start(**vars(self.parser.parse_args(args)))
        return ret

    @classmethod
    def get_parser(cls):
        """Function returning the command line parser for this class"""
        organizer = cls()
        organizer.setup_parser()
        organizer._finish_parser()
        return organizer.parser

    # -------------------------------------------------------------------------
    # ------------------------------ Miscallaneous ----------------------------
    # -------------------------------------------------------------------------

    def is_archived(self, experiment, ignore_missing=True):
        """
        Convenience function to determine whether the given experiment has been
        archived already

        Parameters
        ----------
        experiment: str
            The experiment to check

        Returns
        -------
        str or None
            The path to the archive if it has been archived, otherwise None
        """
        if ignore_missing:
            if isinstance(self.config.experiments.get(experiment, True),
                          Archive):
                return self.config.experiments.get(experiment, True)
        else:
            if isinstance(self.config.experiments[experiment], Archive):
                return self.config.experiments[experiment]

    @staticmethod
    def _archive_extensions():
        """Create translations from file extension to archive format

        Returns
        -------
        dict
            The mapping from file extension to archive format
        dict
            The mapping from archive format to default file extension
        """
        if six.PY3:
            ext_map = {}
            fmt_map = {}
            for key, exts, desc in shutil.get_unpack_formats():
                fmt_map[key] = exts[0]
                for ext in exts:
                    ext_map[ext] = key
        else:
            ext_map = {'.tar': 'tar',
                       '.tar.bz2': 'bztar',
                       '.tar.gz': 'gztar',
                       '.tar.xz': 'xztar',
                       '.tbz2': 'bztar',
                       '.tgz': 'gztar',
                       '.txz': 'xztar',
                       '.zip': 'zip'}
            fmt_map = {'bztar': '.tar.bz2',
                       'gztar': '.tar.gz',
                       'tar': '.tar',
                       'xztar': '.tar.xz',
                       'zip': '.zip'}
        return ext_map, fmt_map

    def __reduce__(self):
        return self.__class__, (self.config, ), {
            '_experiment': self._experiment, '_projectname': self._projectname,
            'no_modification': self.no_modification}


def _get_parser():
    return ModelOrganizer.get_parser()


if __name__ == '__main__':
    ModelOrganizer.main()
