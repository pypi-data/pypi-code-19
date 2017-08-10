# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013, 2015 Rocky Bernstein
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd


class ShowFilenames(Mbase_subcmd.DebuggerSubcommand):
    '''**show filenames**

Show how filenames are reported. The choices are:

* basename : just the file basename
* short : possibly relative, as seen by Python
* full: fully-qualified filename (external front-ends may like this)

Change with **set filenames**
'''
    short_help = "Show the basename portion only of filenames"
    min_abbrev = len('fi')

    def run(self, args):
        val = self.settings['basename']
        if 'full' == val:
            mess = 'full file paths used in showing file names'
        elif 'basename' == val:
            mess = 'file basename used in showing file names'
        elif 'short' == val:
            mess = 'possibly relative paths used in showing file names'
        else:
            self.errmsg('Internal error: incorrect basename setting %s' % val)
            return
        self.msg(mess)
        return

    pass

if __name__ == '__main__':
    from trepan.processor.command.show_subcmd import __demo_helper__ as Mhelper
    Mhelper.demo_run(ShowFilenames)
    pass
