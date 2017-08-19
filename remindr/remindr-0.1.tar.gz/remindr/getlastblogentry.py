# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
# Copyright © 2017 Carl Chenet <carl.chenet@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

'''Manage entries to remind to users'''

# standard libraires imports
import os
import os.path
import sys

def getlastblogentry(options):
    '''Return the last blog entry'''

    lastblogentry = ''
    newlist = []
    nextmessage = False
    pathtolist = options['path_to_list']
    # read the list of blog entries
    with open(pathtolist) as lstc:
        listofentries = lstc.readlines()
    for line in listofentries:
        elements = line.split()
        if len(elements) < 3:
            sys.exit('The list of messages does not seem valid. Please format it correcty before retrying')
        else:
            # extract the current line from the file of the list of blog entries
            status = elements[0]
            # detect if the line should be used
            if status == 'o' and not nextmessage:
                nextmessage = True
                lastblogentry = line[2:].rstrip('\n')
                newlist.append(''.join(['x', line[1:]]))
            # configure the next line to be usded
            elif status == 'x' and nextmessage:
                newlist.append(''.join(['o', line[1:]]))
                nextmessage = False
            else:
                newlist.append(line)
    # checking if entry was found on the last line of the file
    if nextmessage:
        newlist[0] = 'o' + newlist[0][1:]
    # rewrite the modified file
    with open(pathtolist, 'w') as lstc:
        lstc.writelines(newlist)
    return lastblogentry
