# Copyright (C) 2011-2017 Michal Goral.
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

import logging

log = logging.getLogger('Subconvert.%s' % __name__)

from subconvert.utils.Locale import _

# A working VideoWidget class will be exposed depending on mpv availability.
try:
    import mpv
except (OSError, ImportError) as e:
    log.warning(str(e))
    log.warning(_('mpv cannot be imported. Video player disabled.'))
    from subconvert.gui._VideoWidgetNoMultimedia import VideoWidget
else:
    from subconvert.gui._VideoWidget import VideoWidget
