# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2017 Cisco Systems, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os

import yaml


class ConfigError(Exception):
    pass


class Config(object):
    def __init__(self, az, workflow, config_file='photon.yml'):
        """A class responsible for handling configuration, and provide the data
        needed to construct the proper ``ansible-playbook`` commands.

        Args:
            az (str): The az we'll be using.
            workflow (str): The workflow we'll be using.
            config_file (str): The file to read our configuration from.
        """
        self._az = az
        self._workflow = workflow
        self._config_file = config_file
        self._config = self._get_config()
        self._working_az = self._get_working_az()
        self._get_workflow_allowed()

    @property
    def inventory(self):
        """The path to inventory from ``az`` section of config.

        Returns:
            str: The path to inventory.
        """
        return self._working_az.get('inventory')

    @property
    def env(self):
        """Creates the environment that will be passed to the shell invoked
        when calling ansible-playbook. The environment can be modified in the
        ``env`` section of an az config.

        Returns:
            dict: A dictionary containing environment variables.
        """
        e = os.environ.copy()

        # merge az env args with our copy
        e.update(self._working_az.get('env', {}))

        # don't allow environment inventory to get used by accident
        e.pop('ANSIBLE_INVENTORY', None)
        return e

    @property
    def playbook_cmds(self):
        """Build a list of lists containing playbook and all flags to be
        passed to ansible-playbook on the CLI. Suitable for consumption by
        sh module.

        Returns:
            list: A list of lists containing CLI for ``ansible-playbook``.
        """
        cmds = []
        flags = []

        # get keys applied to all playbooks
        flags.extend(self.working_workflow.get('flags', []))

        # walk workflow's playbooks and build up commands
        for p in self.working_workflow['playbooks']:
            flags.extend(p.get('flags', []))
            cmds.append([p['path'], '-i', self.inventory] + flags)

        return cmds

    @property
    def working_workflow(self):
        """Get all information about current workflow.

        Raises:
            ConfigError: When provided workflow isn't found in config.
        Returns:
            dict: Dictionary containing current workflow config.
        """
        try:
            return self._config['workflows'][self._workflow]
        except KeyError:
            msg = "Invalid workflow '{}'. Valid workflows are: {}"
            raise ConfigError(
                msg.format(self._workflow, ', '.join(
                    self._get_available_workflows())))

    def _get_allowed_azs(self):
        """Get optional allowed_azs from the workflow section of the config.

        Returns:
            list: A list of allowed AZs for the current workflow.
            None: If allowed_azs isn't defined. All AZs allowed by default.
        """
        return self.working_workflow.get('allowed_azs')

    def _get_available_azs(self):
        """Get all AZs defined in config file.

        Returns:
            list: AZ names defined in config file.
        """
        return self._config['azs'].keys()

    def _get_available_workflows(self):
        """Get all workflows defined in config file.

        Returns:
            list: Workflow names defined in config file.
        """
        return self._config['workflows'].keys()

    def _get_config(self):
        """Read contents of YAML config file.

        Raises:
            ConfigError: If config file can't be found.
        Returns:
            dict: Dictionary representation of YAML config file.
        """
        try:
            with open(self._config_file) as stream:
                return yaml.safe_load(stream)
        except IOError as e:
            # raise our own exception if config file is not found
            if e.errno == 2:
                msg = "Unable to locate config file '{}'."
                raise ConfigError(msg.format(self._config_file))
            # re-raise IOError for all other errors
            else:
                raise

    def _get_working_az(self):
        """Get all information about current AZ.

        Raises:
            ConfigError: When provided AZ isn't found in config.
        Returns:
            dict: Dictionary containing current AZ config.
        """
        try:
            return self._config['azs'][self._az]
        except KeyError:
            msg = "Invalid AZ '{}'. Valid AZs are: {}"
            raise ConfigError(
                msg.format(self._az, ', '.join(self._get_available_azs())))

    def _get_workflow_allowed(self):
        """Determine if current workflow is allowed in current AZ.

        Raises:
            ConfigError: If workflow is not allowed in az.
        Returns:
            bool: True if workflow is allowed in AZ.
        """
        # if allowed_azs is not defined in the workflow, assume all are allowed
        if self._get_allowed_azs() is None:
            return True

        if self._az in self._get_allowed_azs():
            return True

        msg = "Workflow '{}' may only be run in AZs: {}"
        raise ConfigError(
            msg.format(self._workflow, ', '.join(self._get_allowed_azs())))
