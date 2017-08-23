# Copyright (C) 2011, 2012, 2013 Michal Goral.
# 
# This file is part of Subconvert
# 
# Subconvert is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Subconvert is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Subconvert. If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import QWidget

class VideoWidget(QWidget):
    '''Empty VideoWidget, which is a replacement in case when mpv
    cannot be imported.'''
    def __init__(self, parent=None):
        super().__init__(parent)

    def __getattr__(self, name):
        '''If attribute exists, return it, otherwise return _noop'''
        try:
            return super().__getattr__(name)
        except AttributeError:
            return self._noop

    def _noop(self, *args, **kwargs):
        '''A dummy function which accepts any arguments and returns nothing'''
        pass

    @property
    def real(self):
        '''Is this a real life?'''
        return False
