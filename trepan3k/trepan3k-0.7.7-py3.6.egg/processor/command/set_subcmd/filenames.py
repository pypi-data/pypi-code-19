# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013, 2015 Rocky Bernstein
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.lib import complete as Mcomplete


class SetFilenames(Mbase_subcmd.DebuggerSetBoolSubcommand):
    """**set filenames** {**basename**|**short**|**full**}

Set how filenames are reported. The choices are:

* basename : just the file basename

* short : possibly relative, as seen by Python

* full: fully-qualified filename (external front-ends may like this)

See also:
---------
`show basename`"""

    in_list    = True
    min_abbrev = len('fi')

    filenames_choices = ('basename', 'short', 'full')

    def complete(self, prefix):
        return Mcomplete.complete_token(SetFilenames.filename_choices,
                                        prefix)

    def get_filenames_choice(self, arg):
        if not arg: return 'short'
        if arg in SetFilenames.filenames_choices:
            return arg
        else:
            self.errmsg('Expecting %s"; got %s' %
                        ', '.join(SetFilenames.choices.arg))
            return None
        pass

    def run(self, args):
        if len(args) == 0:
            self.debugger.settings['basename'] = 'short'
        else:
            filenames_choice = self.get_filenames_choice(args[0])
        self.debugger.settings['basename'] = filenames_choice
        show_cmd = self.proc.commands['show']
        show_cmd.run(['show', 'filenames'])
        return


    pass

if __name__ == '__main__':
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper
    Mhelper.demo_run(SetFilenames)
    pass
