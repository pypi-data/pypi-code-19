import textwrap
from score.cli.setup import BashrcModifier, ZshrcModifier


class UpdateBashPrompt(BashrcModifier):

    def test_if_installed(self):
        return 'VIRTUAL_ENV_NAME' in self.read_file('')

    def get_short_description(self):
        return "Add current project name to bash PROMPT"

    def get_description(self):
        return '''
            This step will update your ~/.bashrc file to add show the current
            project name in your shell prompt.

            We will create a backup of your ~/.bashrc file before changing it,
            But if you are not comfortable with automatically modifying your
            bash configuration file, you can add these lines manually:

              ''' + textwrap.indent(self.snippet, '            ').lstrip()

    def get_snippet(self):
        return r'''
            # This next line updates your shell prompt to include the name of
            # the current project.
            if [ -n "$VIRTUAL_ENV_NAME" ]; then
                export PS1="\[[0;33m\](${VIRTUAL_ENV_NAME})\[[0m\]$PS1"
            elif [ -n "$VIRTUAL_ENV" ]; then
                export PS1="\[[0;33m\](${VIRTUAL_ENV##*/})\[[0m\]$PS1"
            fi
        '''


class UpdateZshPrompt(ZshrcModifier):

    test_if_installed = UpdateBashPrompt.test_if_installed

    def get_short_description(self):
        return UpdateBashPrompt.get_short_description(self).\
            replace('bash', 'zsh')

    def get_description(self):
        return UpdateBashPrompt.get_description(self).\
            replace('bash', 'zsh')

    def get_snippet(self):
        return textwrap.dedent(r'''
            # This next line updates your shell prompt to include the name of
            # the current project.
            if [ -n "$VIRTUAL_ENV_NAME" ]; then
                export PROMPT="%{[0;33m%}(${VIRTUAL_ENV_NAME})%{[0m%}$PROMPT"
            elif [ -n "$VIRTUAL_ENV" ]; then
                export PROMPT="%{[0;33m%}(${VIRTUAL_ENV##*/})%{[0m%}$PROMPT"
            fi
        ''').strip()
