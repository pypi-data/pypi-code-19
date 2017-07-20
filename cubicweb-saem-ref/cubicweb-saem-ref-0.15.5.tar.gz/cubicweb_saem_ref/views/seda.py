# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-saem-ref views related to SEDA"""

from cubicweb.web.views import uicfg

from cubicweb_seda.views import archivetransfer
from cubicweb_seda.views.simplified import simplified_afs, simplified_pvs
from cubicweb_seda.views.archiveunit import copy_afs


# primary view configuration #######################################################################

afs = uicfg.autoform_section
afs.tag_attribute(('SEDAArchiveTransfer', 'simplified_profile'), 'main', 'hidden')
copy_afs.tag_attribute(('SEDAArchiveTransfer', 'simplified_profile'), 'main', 'hidden')

simplified_pvs.tag_attribute(('SEDAArchiveTransfer', 'ark'), 'attributes')
# we want only simplified_profile, so its default is set to true and it only has to be hidden
simplified_afs.tag_attribute(('SEDAArchiveTransfer', 'simplified_profile'), 'main', 'hidden')
# also hide transferring and archival agency
for rtype in ('seda_transferring_agency', 'seda_archival_agency'):
    # needed on afs as well as simplified_afs because it's selected during transfer creation
    afs.tag_subject_of(('SEDAArchiveTransfer', rtype, '*'), 'main', 'hidden')
    simplified_afs.tag_subject_of(('SEDAArchiveTransfer', rtype, '*'), 'main', 'hidden')
    simplified_pvs.tag_subject_of(('SEDAArchiveTransfer', rtype, '*'), 'hidden')

# copy rules from __init__ but not considered by this copy of pvs/afs
simplified_pvs.tag_subject_of(('*', 'ark_naa', '*'), 'attributes')
simplified_afs.tag_subject_of(('*', 'ark_naa', '*'), 'main', 'attributes')
simplified_afs.tag_subject_of(('*', 'custom_workflow', '*'), 'main', 'hidden')

simplified_pvs.tag_object_of(('*', 'use_profile', '*'), 'hidden')
simplified_afs.tag_object_of(('*', 'use_profile', '*'), 'main', 'hidden')

simplified_pvs.tag_attribute(('SEDABinaryDataObject', 'filename'), 'hidden')
simplified_afs.tag_attribute(('SEDABinaryDataObject', 'filename'), 'main', 'hidden')
afs.tag_attribute(('SEDABinaryDataObject', 'filename'), 'main', 'hidden')


archivetransfer.ArchiveTransferTabbedPrimaryView.tabs.append('saem.lifecycle_tab')
