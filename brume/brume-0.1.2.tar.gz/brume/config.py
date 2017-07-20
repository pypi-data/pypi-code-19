import os
import yaml
import click

from subprocess import check_output, CalledProcessError
from jinja2 import Template

from stack import stack_outputs
# current outputs of loaded stacks
stackOutputsDefinition = {}

def cloudformation(stack_name, key, *subKeys):
    """
    Return the value of the `key` in outputs of specified stack `stack_name`.

    If `subKey` is specified, return the value of the `subKey` found in the value of the `key` in outputs of specified stack `stack_name`.
    """
    if not (stack_name in stackOutputsDefinition):
        stackOutputsDefinition[stack_name] = stack_outputs(stack_name)
    currentDefinition = stackOutputsDefinition[stack_name]

    if not (key in currentDefinition):
        click.secho('[ERROR] No key {} variable in stack {}'.format(key, stack_name), err=True, fg='red')
        exit(1)
    currentDefinition = currentDefinition[key]

    for subKey in subKeys:
        if not (subKey in currentDefinition):
            click.secho('[ERROR] No key {} in stack {}'.format(subKey, stack_name), err=True, fg='red')
            exit(1)
        currentDefinition = currentDefinition[subKey]

    return currentDefinition


class Config():

    @staticmethod
    def cfn(stack_name, key, secondKey=None, thirdKey=None):
        if (secondKey is None):
            return cloudformation(stack_name, key)
        else:
            if (thirdKey is None):
                return cloudformation(stack_name, key, secondKey)
            else:
                return cloudformation(stack_name, key, secondKey, thirdKey)

    @staticmethod
    def env(key):
        """Return the value of the `key` environment variable."""
        try:
            return os.environ[key]
        except KeyError:
            click.secho('[ERROR] No environment variable with key {}'.format(key), err=True, fg='red')
            exit(1)

    @staticmethod
    def git_commit():
        """Return the SHA1 of the latest Git commit (HEAD)."""
        try:
            return check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
        except CalledProcessError:
            click.secho('[ERROR] Current directory is not a Git repository', err=True, fg='red')
            exit(1)

    @staticmethod
    def git_branch():
        """Return the name of the current Git branch."""
        try:
            return check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
        except CalledProcessError:
            click.secho('[ERROR] Current directory is not a Git repository', err=True, fg='red')
            exit(1)

    @staticmethod
    def load(config_file='brume.yml'):
        """
        Return the YAML configuration for a project based on the `config_file` template.

        By default, the template exposes `env` and `cfn` functions.
        The `git_branch` and `git_commit` values are exposed only when a `.git` folder
        exists in the current directory
        """
        template_functions = {}
        template_functions['env'] = Config.env
        template_functions['cfn'] = Config.cfn

        if os.path.isdir('.git'):
            template_functions['git_commit'] = Config.git_commit()
            template_functions['git_branch'] = Config.git_branch()

        try:
            template = Template(open(config_file, 'r').read())
        except IOError as e:
            print(e)
            exit(1)
        else:
            return yaml.load(
                template.render(**template_functions)
            )
