# coding: utf-8

"""This class has the algorithms that will be executed by deployvcmd and deployvd, both are
interfaces between the input (files, cmd interface and rabbitmq) and CommandV.

`extend_me <http://pythonhosted.org/extend_me/>`_ is used in the event manager class and the core
command component because it allows an easy app extension without the need of modifying the core
components.

CommandV inherits from `Extensible <http://pythonhosted.org/extend_me/#extensible>`_ base class so
it can be extended in a simple way by just inheriting from CommandV.
"""

import logging
import os
import re
import yaml
import simplejson as json
import base64
from tempfile import mkdtemp
from extend_me import Extensible
from psycopg2 import OperationalError
from docker import APIClient as Client
from docker.errors import APIError, NullResource, NotFound
from deployv.base.errors import BuildError, NoSuchContainer, DumpError, NotRunning
from deployv.base.extensions_core import events, load_extensions
from deployv.base import postgresv, nginxv
from deployv.helpers import utils, container, database_helper
from deployv.instance import instancev
from deployv.extensions.checkers import InstallTestRepo

logger = logging.getLogger(__name__)  # pylint: disable=C0103

load_extensions()


class CommandV(Extensible):
    """ Class that contains the main methods of each command

    :param config: Configuration dictionary. See :class:`~deployv.base.instancev.InstanceV`.
    :type config: dict
    :param instance_class: Class for the instance manager object.
    :type instance_class: class
    """

    def __init__(self, config, instance_class=None):
        self.__config = config
        self._domains = None
        if self.__config.get('instance', False):
            prefix = container.generate_prefix(self.__config)
            self.__config.get('instance').update({'prefix': prefix.lower()})
        if instance_class:
            self.__instance_manager = instance_class(self.__config)
        else:
            self.__instance_manager = instancev.InstanceV(self.__config, timeout=3000)

    @property
    def instance_manager(self):
        return self.__instance_manager

    def _can_add_new(self):
        """As we have a limited amount of resources in each node we need to check if the running
        instances count is less than the allowed to run a new one.

        :returns: If the count of running instances is lower than the allowed max.
        :rtype: bool
        """
        containers = self.instance_manager.cli.containers()
        try:
            max_instances = self.__config.get('node').get('max_instances')
        except AttributeError:
            return True
        count = 0
        for container_info in containers:
            for name in container_info.get('Names'):
                if re.match(r'^/[tiu][0-9]+_[a-z]+[0-9][0-9]_odoo', name):
                    count += 1
                    break
        logger.debug('Instance count %s/%s', count, max_instances)
        return count < max_instances

    @events
    def create(self):
        """Creates an Odoo dockerized instance with the provided configuration.

        :returns: A response in json format containing the info dict returned
            by :func:`~deployv.base.dockerv.DockerV.basic_info`.
        :rtype: dict
        """
        res = {'command': 'create',
               'attachments': list()}
        if not self._can_add_new():
            logger.info('Max instance count reached (%s allowed)',
                        self.__config.get('node').get('max_instances'))
            res.update({'error': 'Reached max instance count for this node ({} allowed)'
                       .format(self.__config.get('node').get('max_instances'))})
            return res
        container_cfg = self.__config.get('container_config')
        build_image = container_cfg.get('build_image') or container_cfg.get('full_stack')
        if build_image:
            build_res = self.instance_manager.build_image()
            logger.debug('Build res %s', build_res)
            if not build_res[0]:
                res.update(build_res[1])
                return res
        try:
            self.instance_manager.start_postgres_container()
            info = self.instance_manager.start_odoo_container()
        except Exception as error:  # pylint: disable=W0703
            logger.exception('Could not start container')
            res.update({'error': utils.get_error_message(error)})
            return res
        if info.get('error'):
            res.update({'error': info.get('error')})
            return res
        if info and self.__config.get('instance').get('ssh_key'):
            self.instance_manager.deploy_key()
            self.instance_manager.check_keys()
        try:
            res_build = self.instance_manager.build_instance()
            if not res_build[0]:
                res.update({
                    'error': res_build[1]
                })
                return res
            post_branch = os.path.join(self.instance_manager.temp_folder, 'post_process.json')
            res.get('attachments').append(
                {
                    'file_name': os.path.basename(post_branch),
                    'file': utils.generate_attachment(post_branch),
                    'type': 'application/json'
                }
            )
        except TypeError as error:
            res.update({'error': utils.get_error_message(error)})
        self.instance_manager.stop_instance()
        install_log = self.instance_manager.install_deps()
        logger.info(install_log)
        if info:
            info.update({'domain': self.instance_manager.config.get('domain')})
            if install_log:
                info.update(install_log)
            res.update({'result': info})
            if self.__config.get('node', False):
                logger.debug('Use nginx config: %s',
                             self.__config.get('node').get('use_nginx', False))
                if self.__config.get('node').get('use_nginx', False):
                    logger.debug('Using nginx')
                    self._domains = self.update_nginx()
                    nginx_url = self._get_nginx_url(info.get('name')[:-5])
                    res.get('result').update({
                        'nginx_url': nginx_url,
                        'instance_log': '{url}/logs/odoo_stdout.log'.format(url=nginx_url)
                    })
        self.instance_manager.start_instance()
        return res

    def _build_image(self):
        res = (True, dict())
        try:
            build_res = self.__instance_manager.build_instance_image()
        except BuildError as error:
            res = (False, {'error': utils.get_error_message(error)})
        else:
            if not build_res.get('result'):
                res = (False, build_res)
        return res

    def _get_nginx_url(self, name):
        nginx_url = None
        for domain in self._domains:
            if domain.get('domain').startswith(name):
                nginx_url = domain.get('domain')
                break
        logger.debug('Updating url : %s', nginx_url)
        return nginx_url

    def deactivate(self, database):
        db_config = self.instance_manager.db_config.copy()
        db_config.update({'nginx_url': self.instance_manager.config.get('nginx_url')})
        instancev.deactivate_database(db_config, database)
        new_admin = self.__config.get('instance').get('config').get('admin', False)
        if new_admin:
            instancev.InstanceV.change_password(1, new_admin, database, db_config)

    def restore_process(self, backup_src, database_name, deactivate=False):
        res = {}
        instance_type = self.__instance_manager.instance_type
        update = False
        if instance_type in instancev.UPDATE:
            update = True
            InstallTestRepo.event = 'after.updatedb.event'
        restore_res = self.__instance_manager.restore_database(database_name, backup_src)
        if not restore_res[0]:
            res.update({'error': restore_res[1]})
            return (False, res)
        res.update(restore_res[1])
        database_name = restore_res[1].get('result').get('database_name')
        if instance_type in instancev.DEACTIVATE or deactivate:
            db_config = self.instance_manager.db_config.copy()
            db_config.update({'nginx_url': self.instance_manager.config.get('nginx_url')})
            instancev.deactivate_database(db_config, database_name)
        if self.__config.get('instance').get('config').get('admin'):
            new_passwd = self.__config.get('instance').get('config').get('admin')
            instancev.InstanceV.change_password(1, new_passwd, database_name,
                                                self.instance_manager.db_config)
        if update:
            if self.instance_manager.instance_type == 'updates':
                original_db = self.instance_manager.clone_db(database_name)
                res.get('result').update({'original_database': original_db})
            update_res = self.updatedb(database_name)
            for key, values in update_res.items():
                if key in res:
                    res.get(key).update(values)
                else:
                    res.update({key: values})
        self.__instance_manager.start_instance()
        return (True, res)

    def post_process(self):
        """Command in charge of performing the steps required after deploying an instance
        like generating the cloc report.

        :returns: dict with the results or the errors
        """
        res = {'command': 'post_process'}
        post_process = ['cloc_report', 'list_packages']
        if self.__config.get('instance').get('original_database'):
            post_process.append('compare_databases')
        if self.instance_manager.instance_type == 'updates':
            post_process.append('push_image')
        for command in post_process:
            if not hasattr(self, command):
                logger.error('Command %s does not exist, skipping from the post process', command)
                continue
            cmd_method = getattr(self, command)
            cmd_res = cmd_method()
            if 'error' in cmd_res.keys():
                res.update({'error': cmd_res.get('error')})
                return res
            cmd_res.pop('command', False)
            res.update({command: cmd_res})
        return res

    def cloc_report(self):
        """This method generates a report by the cloc command the number of lines of code that has
        an instance and stores it in yaml format to be added as an attachment.

        :returns: a list of the dictionary that has the output of the cloc command in yaml format
            to be added as an attachment.
        :rtype: dict
        """
        res = {'command': 'cloc_report', 'attachments': list()}
        command_exists = self.__instance_manager.exec_cmd("which cloc")
        if not command_exists:
            res.update({
                'result': 'CLOC is not installed in the container, report not generated'
            })
            return res
        odoo_home = self.__instance_manager.\
            config.get('env_vars').get('odoo_home')
        module = os.path.join(odoo_home, 'instance')
        command_cloc = "cloc --yaml {module}".format(module=module)
        execute_cloc = self.__instance_manager.exec_cmd(command_cloc)
        body_content = execute_cloc.split('\n---')
        res.get('attachments').append(
            {
                "file_name": "cloc_report",
                "file": base64.b64encode(str(yaml.load(body_content[1]))),
                "type": 'application/json'
            }
        )
        res.update({'result': 'CLOC report successfully generated'})
        return res

    def list_packages(self):
        """This method dumps a list of packages installed inside the container with `apt` and `pip`.
        """
        res = {
            'command': 'list_packages',
            'packages': self.__instance_manager.get_container_packages()
        }
        return res

    @events
    def restore(self, backup_src=None, database_name=None, deactivate=False):
        """Restores a backup from a file or folder. If a folder is provided, searches the best
        match for the given configuration. Database name is an optional parameter.

        The return value is a dict as follows::

            {
                'command': 'command executed',
                'result':
                {
                    'backup': 'backup file used to restore the database',
                    'database_name': 'the database name created with the corresponding backup'
                }
            }

        In case of any error::

            {
                'command': 'command executed',
                'error': 'error message'
            }

        :param backup_src: Backup source, can be a folder or a backup file.
        :type backup_src: str
        :param database_name: Database name to restore. If None, is generated automatically.
        :type database_name: str
        :param deactivate: Force db deactivation ignoring the instance type.
        :type deactivate: bool
        :returns: A json object with the result or error generated. If any result is generated the
            result key will have the backup used and the database name.
        :rtype: dict
        """
        res = {'command': 'restore'}
        if not backup_src and not self.__config.get('container_config').get('backup_folder'):
            db_name = self.create_db_demo()
            res.update({'result': {'database_name': db_name}})
            return res
        backup_src = os.path.expanduser(backup_src or "")
        try:
            restore_res = self.restore_process(backup_src, database_name, deactivate)
            logger.debug('restore_res: %s', str(restore_res))
            if not restore_res[0]:
                res.update(restore_res[1])
                return res
            db_name = restore_res[1]["result"].get('database_name')
        except (OperationalError, EOFError, AttributeError) as error:
            error_msg = utils.get_error_message(error)
            if "'NoneType' object has no attribute 'get'" in error_msg:
                self.__config.get('instance').update({
                    'config': {
                        "db_host": self.__instance_manager.docker_env.get('DB_HOST'),
                        "db_password": self.__instance_manager.docker_env.get('DB_PASSWORD'),
                        "db_port": self.__instance_manager.docker_env.get('DB_PORT'),
                        "db_user": self.__instance_manager.docker_env.get('DB_USER')
                    }
                })
            else:
                res.update({
                    'error': error_msg
                })
                return res
        res.update({
            'result': {
                'backup': os.path.abspath(restore_res[1].get("result").get('source')),
                'database_name': db_name,
                'original_database': restore_res[1].get("result").get('original_database'),
                'update_logs': restore_res[1].get('result').get('update_logs', [])
            },
            'attachments': restore_res[1].get('attachments')
        })
        if self.__config.get('instance').get('install_module'):
            install_res = self._install_module(db_name)
            res.get('result').update({
                'install_module': install_res
            })
            res = self._attach_file(res, install_res.get('log_file'), 'text/plain')
        return res

    def _attach_file(self, msg, file_name, file_type):
        res = msg
        if not res.get('attachments', False):
            res.update({'attachments': list()})
        res.get('attachments').append(
            {
                'file_name': os.path.basename(file_name),
                'file': utils.generate_attachment(file_name),
                'type': file_type
            }
        )
        return res

    def _install_module(self, db_name):
        install_res = self.__instance_manager.install_module(
            self.__config.get('instance').get('install_module'),
            db_name
        )
        return install_res

    @events
    def backup(self, backup_dir, database_name, cformat=False, reason=False, tmp_dir=False,
               prefix=False):
        res = {'command': 'backup'}
        try:
            bkp = self.__instance_manager.generate_backup(database_name,
                                                          backup_dir,
                                                          cformat=cformat,
                                                          reason=reason,
                                                          tmp_dir=tmp_dir,
                                                          prefix=prefix)
        except DumpError as error:
            logger.exception('Backup could not be generated')
            res.update({'error': 'Could not generate the backup: {0}'
                       .format(utils.get_error_message(error))})
        else:
            if bkp:
                res.update({'result': bkp})
            else:
                res.update({'error': 'Could not generate the backup'})
        return res

    def deactivate_backup(self, db_config, backup, prefix, store_path, cformat, admin_password):
        if not db_config.get('db_host') or db_config.get('db_host').startswith('172.17.'):
            db_config.update({'db_host': 'localhost'})
        working_dir = mkdtemp(prefix='deployv_')
        db_helper_class = database_helper.DatabaseHelper.get_helper(use_template=False)
        db_helper = db_helper_class(utils.odoo2postgres(db_config))
        candidate = db_helper.search_candidate(backup, prefix)
        prefix = '{prefix}_deactivated'.format(prefix=prefix)
        db_name = utils.generate_dbname({}, candidate[1], prefix)
        postgres = postgresv.PostgresShell(utils.odoo2postgres(db_config))
        postgres.drop(db_name)
        try:
            dest_dir = utils.decompress_files(candidate[1], working_dir)
        except (EOFError, IOError):
            utils.clean_files(working_dir)
            return False
        restore_res = db_helper.create_database(dest_dir, db_name.lower())
        if not restore_res[0]:
            logger.error(restore_res[1])
            return False
        instancev.deactivate_database(db_config, db_name)
        instancev.InstanceV.change_password('1', admin_password, db_name, db_config)
        dump_path = os.path.join(dest_dir, 'database_dump.sql')
        postgres.dump(db_name, dump_path)
        backup_name = utils.generate_backup_name(db_name)
        files2backup = []
        files = os.listdir(dest_dir)
        for element in files:
            full_path = os.path.join(dest_dir, element)
            files2backup.append(full_path)
        backup = utils.compress_files(backup_name, files2backup,
                                      dest_folder=store_path, cformat=cformat)
        postgres.drop(db_name)
        if dest_dir != backup:
            utils.clean_files(working_dir)
        return backup

    def change_passwords(self):
        """Generates a random password for each one of the users in an instance.
        """
        res = {'command': 'change_passwords'}
        results = {}
        db_name = self.__config.get('instance').get('config').get('db_name')
        users = self.instance_manager.get_odoo_users(db_name)
        for user in users:
            if user.get('login') not in ['public', 'portaltemplate']:
                password = utils.random_string(10)
                instancev.InstanceV.change_password(user.get('id'), password, db_name,
                                                    self.instance_manager.db_config)
                results.update({user.get('login'): password})
        res.update({'result': results})
        return res

    def compare_databases(self):
        res = {'command': 'compare_databases'}
        original_db = self.__config.get('instance').get('original_database')
        updated_db = self.__config.get('instance').get('config').get('db_name')
        original_translations = self.instance_manager.get_translations(original_db)
        updated_translations = self.instance_manager.get_translations(updated_db)
        translations_diff = self.instance_manager.compare_translations(original_translations,
                                                                       updated_translations)
        original_menus = self.instance_manager.get_menus(original_db)
        updated_menus = self.instance_manager.get_menus(updated_db)
        menus_diff = self.instance_manager.compare_menus(
            original_menus, updated_menus, original_db, updated_db
        )
        original_views = self.instance_manager.get_views(original_db)
        updated_views = self.instance_manager.get_views(updated_db)
        views_diff = self.instance_manager.compare_views(original_views, updated_views)
        original_fields = self.instance_manager.get_fields(original_db)
        updated_fields = self.instance_manager.get_fields(updated_db)
        fields_diff = self.instance_manager.compare_fields(original_fields, updated_fields)
        res.update({'result': {'translations': translations_diff,
                               'menus': menus_diff,
                               'views': views_diff,
                               'fields': fields_diff}})
        return res

    @events
    def updatedb(self, database_name=None):
        """Updates an instance (branches and database) and returns the json with a summary of the
        operation.

        :param database_name: Database name to be updated.
        :type database_name: str
        :returns: The result from :meth:`deployv.instance.instancev.run_and_log`.
        :rtype: dict
        """
        db_name = database_name if database_name is not None \
            else self.__config.get('instance').get('config').get('db_name')
        update_modules = self.__config.get('instance').get('update_module', ["all"])
        if not isinstance(update_modules, list):
            update_modules = update_modules.split(",")
        res = {'command': 'updatedb'}
        try:
            self.__instance_manager.stop_instance()
        except APIError as error:
            logger.exception('Could not update database %s: %s', db_name, error.message)
            res.update({'error': error.explanation})
            return res
        retry = 0
        res.update({"attachments": [], "result": {"update_logs": []}})
        for module in update_modules:
            while retry <= 1:
                res_update = self.__instance_manager.update_db(module, db_name)
                if res_update.get('errors'):
                    if retry < 1:
                        logger.info(
                            'Some error shown in the update log, updating again')
                        retry = retry + 1
                    else:
                        logger.error('The instance was not updated properly, check logfile: %s',
                                     res_update.get('log_file'))
                        res['result']['update_logs'].append(res_update)
                        break
                else:
                    res['result']['update_logs'].append(res_update)
                    break
        self.__instance_manager.start_instance()
        for log in res["result"]["update_logs"]:
            res["attachments"].append(
                {
                    'file_name': os.path.basename(log["log_file"]),
                    'file': utils.generate_attachment(log["log_file"]),
                    'type': 'text/plain'
                })
        res['result'].update({'database_name': db_name})
        if self.__config.get('instance').get('install_module'):
            install_res = self.__instance_manager.install_module(
                self.__config.get('instance').get('install_module'),
                db_name
            )
            res.get('result').update({
                'install_module': install_res
            })
            if not res.get('attachments', False):
                res.update({'attachments': list()})
            res.get('attachments').append(
                {
                    'file_name': os.path.basename(install_res.get('log_file')),
                    'file': utils.generate_attachment(install_res.get('log_file')),
                    'type': 'text/plain'
                }
            )
        return res

    @events
    def update_branches(self):
        """Updates repos in the given instance.

        :return: Returns the operation result in the json format, additionally will attach the
            current instance status with the commits, repos and branches. See
            :mod:`~deployv.helpers.branches` for more info about the format.
        :rtype: dict
        """
        res = {'command': 'update_branches'}
        if self.__config.get('instance').get('ssh_key'):
            self.__instance_manager.deploy_key()
            self.__instance_manager.check_keys()
        try:
            res_build = self.__instance_manager.build_instance()
            if not res_build[0]:
                res.update({
                    'error': 'Could not generate instance with the given branches: {}'
                             .format(res_build[1])
                })
                return res
            install_log = self.__instance_manager.install_deps()
            logger.info(install_log)
            if install_log:
                res.update(install_log)
            self.__instance_manager.stop_instance()
            if not res.get('attachments', False):
                res.update({'attachments': list()})
            post_branch = os.path.join(self.__instance_manager.temp_folder, 'post_process.json')
            res.get('attachments').append(
                {
                    'file_name': os.path.basename(post_branch),
                    'file': utils.generate_attachment(post_branch),
                    'type': 'application/json'
                }
            )
        except TypeError as error:
            res.update({'error': str(error)})
        else:
            res.update({'result': 'Branches updated'})
        return res

    def _stop_instance(self):
        try:
            self.__instance_manager.stop_instance()
        except NotFound as error:
            logger.debug('Error message %s', utils.get_error_message(error))
            utils.get_error_message(error)
            return 'Instance already deleted'
        except NullResource as error:
            if "image or container param is undefined" in error.message:
                return 'Instance already deleted or misspelled name'
        return True

    def _drop_dbs(self):
        res_dropdb = list()
        psql_dict = utils.odoo2postgres(self.__instance_manager.db_config)
        error_msgs = ["Connection refused", "password authentication failed"]
        try:
            psql_shell = postgresv.PostgresShell(psql_dict)
            db_list = psql_shell.list_databases()
        except OperationalError as error:
            if not any([msg in error.message for msg in error_msgs]):
                raise
        else:
            if self.__config.get('instance').get('config').get('db_name'):
                prefix = self.__config.get('instance').get('config').get('db_name')
            else:
                prefix = container.generate_prefix(self.__config)
            copy_prefix = 'copy_{prefix}'.format(prefix=prefix)
            for db in db_list:
                logger.debug('Db in the list: %s Owner: %s', db.get('name'), db.get('owner'))
                if db.get('name').startswith((prefix.lower(), copy_prefix.lower())) and\
                        db.get('owner') == psql_dict.get('user'):
                    logger.debug('Dropping %s database', db.get('name'))
                    psql_shell.drop(db.get('name'))
                    res_dropdb.append('Dropped {} database'.format(db.get('name')))
        return res_dropdb

    @events
    def delete_instance(self):
        """Delete an instance and database from the node.  If it does not exists or was already
        deleted, will indicate it in the message.

        :returns: A json object with the result or error generated. The result key will contain the
            generated result message, if any.
        :rtype: dict
        """
        logger.info('Deleting container(s)')
        res = {'command': 'delete_instance'}
        result = []
        try:
            self.instance_manager.clean_volumes()
        except (NullResource, NotRunning) as error:
            allowed_errors = ['image or container param is undefined', 'is not running',
                              'Resource ID was not provided']
            error_msg = utils.get_error_message(error)
            if any([allowed_error in error_msg for allowed_error in allowed_errors]):
                logger.error(
                    'Could not clean the container\'s volumes, container not found or not running'
                )
            else:
                res.update({'error': utils.get_error_message(error)})
                return res
        try:
            config = self.instance_manager.config
            self.instance_manager.remove_container(config.get('container_name'))
            result.append('Instance {} deleted'.format(config.get('container_name')))
            if config.get('postgres_container_name'):
                self.instance_manager.remove_container(config.get('postgres_container_name'))
                result.append('Instance {} deleted'.format(config.get('postgres_container_name')))
            res_dropdb = self._drop_dbs()
            result.extend(res_dropdb)
            res.update({
                'result': result
            })
            if self.__config.get('node').get('use_nginx'):
                self.update_nginx()
        except Exception as error:  # pylint: disable=W0703
            logger.exception('Could not remove container')
            if "No such container or id: None" in utils.get_error_message(error):
                res.update({'result': 'Instance already deleted or misspelled name'})
            else:
                res.update({'error': utils.get_error_message(error)})
            return res
        return res

    def get_containers(self):
        """Gets the containers list that are currently executing, which names match the
        regex: '^/([tiu][0-9]+_[a-z]+[0-9][0-9])_odoo', for example: 't111_cust80_odoo'.

        :return: Containers (as dict) with the domain and mapping ports.
        :rtype: list
        """
        cli = Client()
        containers = cli.containers()
        res = list()
        logger.debug('Geting containes names')
        for container_info in containers:
            for name in container_info.get('Names'):
                logger.debug('Name : %s', name)
                domain = re.search(r'^/([tiu][0-9]+_[a-z]+[0-9][0-9])_odoo', name)
                if domain:
                    inspected = self.__instance_manager.inspect(container_info.get('Id'))
                    ports_info = container.get_ports_dict(inspected)
                    res.append({
                        'domain': '{sub}.{domain}'.format(
                            sub=domain.group(1),
                            domain=self.__config.get('container_config').get('domain')),
                        'port': ports_info.get('8069'),
                        'lp_port': ports_info.get('8072'),
                        'logs': os.path.join(
                                os.path.expanduser(
                                        self.__config.get('container_config').get('working_folder')
                                ),
                                inspected.get('Name')[1:])
                    })
                    break
        return res

    @events
    def update_nginx(self):
        """Updates nginx config file to match running containers. If any are stopped or removed,
        they will be removed from nginx config.

        :return: Containers config. See :meth:`deployv.base.commandv.get_containers`.
        :rtype: dict
        """
        containers_config = self.get_containers()
        nginx_manager = nginxv.NginxV(self.__config.get('node').get('nginx_folder'))
        nginx_manager.update_sites(containers_config)
        nginx_manager.restart()
        return containers_config

    @events
    def push_image(self):
        res = {'command': 'push_image'}
        res.update({'attachments': list()})
        response = ""
        try:
            container_info = self.__instance_manager.basic_info
        except NoSuchContainer:
            res.update({'error': 'Instance already deleted or misspelled name'})
            return res
        repo_image = self.__config.get('container_config').get('customer_image')
        if not repo_image:
            res.update({'error': "It is not specified the repository to upload the image"})
            return res
        split_repo = repo_image.split("/", 1)
        tag_name = split_repo[1].split(":", 1)
        name = tag_name[0]
        tag = tag_name[1]
        repo_image = "{base}/{name}".\
            format(base=split_repo[0], name=utils.clean_string(name))
        message = 'Commit container {container} to images {image}:{tag}'\
            .format(container=container_info.get('Id'), image=repo_image, tag=tag)
        logger.info(message)
        commit = self.instance_manager.cli.commit(container_info.get('Id'),
                                                  repository=repo_image, tag=tag)
        image = self.instance_manager.cli.inspect_image(commit.get('Id'))
        for line in self.instance_manager.cli.push(image.get('RepoTags')[0], stream=True):
            obj = json.loads(line)
            if obj.get('status'):
                logger.debug(obj)
                response = response+'\n'+line
            elif obj.get('error'):
                logger.debug(obj.get('error').strip())
                res.update({"result": {'error': obj.get('error').strip(),
                            "image": image.get('RepoTags')[0]}})
                return res
        res.get('attachments').append(
            {
                "file_name": "push_image.txt",
                "file": base64.b64encode(response),
                "type": 'application/txt'
            }
        )
        res.update({'result': {'image': image.get('RepoTags')[0]}})
        return res

    def create_db_demo(self):
        """ This method creates an empty database.

        :return: The name of the database
        :rtype: str
        """
        self._stop_instance()
        self._drop_dbs()
        if self.__config.get('instance').get('config').get('db_name'):
            db_name = self.__config.get('instance').get('config').get('db_name')
        else:
            db_name = utils.generate_dbname(self.__config,
                                            False,
                                            self.__config.get('instance').get('prefix'))
        db_config = self.instance_manager.db_config
        postgres = postgresv.PostgresShell(utils.odoo2postgres(db_config))
        postgres.create(db_name)
        postgres.create_extension_unaccent(db_name)
        self.updatedb(db_name)
        if self.__config.get('instance').get('config').get('admin'):
            new_passwd = self.__config.get('instance').get('config').get('admin')
            instancev.InstanceV.change_password(1, new_passwd, db_name,
                                                self.instance_manager.db_config)
        return db_name
