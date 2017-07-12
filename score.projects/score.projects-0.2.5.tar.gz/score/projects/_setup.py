# vim: set fileencoding=UTF-8
# Copyright © 2015-2017 STRG.AT GmbH, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in the
# file named COPYING.LESSER.txt.
#
# The SCORE Framework and all its parts are distributed without any WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. For more details see the GNU Lesser General Public
# License.
#
# If you have not received a copy of the GNU Lesser General Public License see
# http://www.gnu.org/licenses/.
#
# The License-Agreement realised between you as Licensee and STRG.AT GmbH as
# Licenser including the issue of its valid conclusion and its pre- and
# post-contractual effects is governed by the laws of Austria. Any disputes
# concerning this License-Agreement including the issue of its valid conclusion
# and its pre- and post-contractual effects are exclusively decided by the
# competent court, in whose district STRG.AT GmbH has its registered seat, at
# the discretion of STRG.AT GmbH also the competent court, in whose district the
# Licensee has his registered seat, an establishment or assets.

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
