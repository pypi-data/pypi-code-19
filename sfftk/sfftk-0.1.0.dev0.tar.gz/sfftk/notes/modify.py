#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sfftk.notes.edit

Copyright 2017 EMBL - European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at 

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software 
distributed under the License is distributed on an 
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
either express or implied. 

See the License for the specific language governing permissions 
and limitations under the License.
"""


from __future__ import division

from collections import namedtuple
import re
import shlex
import shutil
import sys, os

import h5py

from .. import schema
from ..core.configs import get_configs
from ..core.parser import parse_args
from ..core.print_tools import print_date
from ..notes.view import NoteView
from ..sff import handle_convert

"""
:TODO: allow user to modify/view hierarchy through segmentation annotation toolkit 
"""

configs = get_configs()

    
__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-04-07"


# externalReference
extRef = namedtuple('extRef', ['type', 'otherType', 'value'], verbose=False)


class Note(object):
    def __init__(self, args):
        self._note_args = args
    @property
    def description(self):
        return self._note_args.description
    @property
    def numberOfInstances(self):
        if self._note_args.number_of_instances:
            return self._note_args.number_of_instances
        else:
            return 1
    @property
    def externalReferenceId(self):
        return self._note_args.external_ref_id
    @property
    def externalReference(self):
        if self._note_args.external_ref:
            extRefList = list()
            for _type, _value in self._note_args.external_ref:
                extRefList.append(
                    extRef(
                        type=_type,
                        otherType='-',
                        value=_value
                        )
                    )
            return extRefList
        else:
            return None
    @property
    def complexId(self):
        return self._note_args.complex_id
    @property
    def complexes(self):
        return self._note_args.complexes
    @property
    def macromoleculeId(self):
        return self._note_args.macromolecule_id
    @property
    def macromolecules(self):
        return self._note_args.macromolecules
    def add_to_segment(self, segment):
        """Add the annotations found in this ``Note`` object to the ``schema.SFFSegment`` object
        
        :param segment: single segment in EMDB-SFF
        :type segment: ``sfftk.schema.SFFSegment``
        """
        # biologicalAnnotation
        if segment.biologicalAnnotation:
            print_date("Note: A biological annotation exists. You can edit it using 'sff notes edit'.")
        else:
            bA = schema.SFFBiologicalAnnotation()
            bA.description = self.description
            bA.numberOfInstances = self.numberOfInstances
            if self.externalReference:
                if not bA.externalReferences:
                    bA.externalReferences = schema.SFFExternalReferences()
                for extRef in self.externalReference:
                    bA.externalReferences.add_externalReference(
                        schema.SFFExternalReference(
                            type=extRef.type,
                            otherType=extRef.otherType,
                            value=extRef.value,
                            )
                        )
            segment.biologicalAnnotation = bA
        # complexesAndMacromolecules
        if segment.complexesAndMacromolecules:
            print_date("Note: Complexes and macromolecules exist. You can edit them using 'sff notes edit'.")
        else:
            cAM = schema.SFFComplexesAndMacromolecules()
            if self.complexes:
                complexes = schema.SFFComplexes()
                for c in self.complexes:
                    complexes.add_complex(c)
                cAM.complexes = complexes
            if self.macromolecules:
                macromolecules = schema.SFFMacromolecules()
                for m in self.macromolecules:
                    macromolecules.add_macromolecule(m)
                cAM.macromolecules = macromolecules
            segment.complexesAndMacromolecules = cAM
        return segment
    def edit_in_segment(self, segment):
        """Edit the annotations found in this ``Note`` object to the ``schema.SFFSegment`` object
        
        :param segment: single segment in EMDB-SFF
        :type segment: ``sfftk.schema.SFFSegment``
        """
        # biologicalAnnotation
        if not segment.biologicalAnnotation:
            print_date("Note: no biological anotation was found. You may edit only after adding with 'sff notes add'.")
        else:
            bA = segment.biologicalAnnotation
            if self.description:
                bA.description = self.description
            if self.numberOfInstances:
                bA.numberOfInstances = self.numberOfInstances
            if self.externalReference:
                if not bA.externalReferences:
                    bA.externalReferences = schema.SFFExternalReferences()
                start_index = self.externalReferenceId  
                for extRef in self.externalReference:
                    bA.externalReferences.insert_externalReference(
                        schema.SFFExternalReference(
                            type=extRef.type, 
                            otherType=extRef.otherType,
                            value=extRef.value,
                            ),
                        start_index,              
                        )
                    start_index += 1
            segment.biologicalAnnotation = bA
        # complexesAndMacromolecules
        if not segment.complexesAndMacromolecules:
            print_date("Note: no complexes and macromolecules were found. You may edit only after adding with 'sff notes add'.")
        else:
            cAM = segment.complexesAndMacromolecules
            # complexes
            if self.complexes:
                if cAM.complexes: # complexes already present
                    for i in xrange(len(self.complexes)):                            
                        if i == 0: # there are complexes but editing the first item mentioned
                            try:
                                cAM.complexes.replace_complex_at(self.complexId + i, self.complexes[i])
                            except IndexError:
                                cAM.complexes.add_complex(self.complexes[i])
                        else: # all other new complexes are inserted after pushing others down
                            try:
                                cAM.complexes.insert_complex_at(self.complexId + i, self.complexes[i])
                            except IndexError:
                                cAM.complexes.add_complex(self.complexes[i])
                else: # no complexes 
                    complexes = schema.SFFComplexes()
                    for c in self.complexes:
                        complexes.add_complex(c)
                    cAM.complexes = complexes
            # macromolecules
            if self.macromolecules:
                if cAM.macromolecules: # macromolecules already present
                    for i in xrange(len(self.macromolecules)):
                        if i == 0: # there are macromolecules but editing the first item mentioned
                            try:
                                cAM.macromolecules.replace_macromolecule_at(self.macromoleculeId + i, self.macromolecules[i])
                            except IndexError:
                                cAM.macromolecules.add_macromolecule(self.macromolecules[i])
                        else: # all other new macromolecules are inserted after pushing others down
                            try:
                                cAM.macromolecules.insert_macromolecule_at(self.macromoleculeId + i, self.macromolecules[i])
                            except IndexError:
                                cAM.macromolecules.add_macromolecule(self.macromolecules[i])
                else: # no macromolecules
                    macromolecules = schema.SFFMacromolecules()
                    for m in self.macromolecules:
                        macromolecules.add_macromolecule(m)
                    cAM.macromolecules = macromolecules
            segment.complexesAndMacromolecules = cAM
        return segment
    def del_from_segment(self, segment):
        """Delete the annotations found in this ``Note`` object to the ``schema.SFFSegment`` object
        
        :param segment: single segment in EMDB-SFF
        :type segment: ``sfftk.schema.SFFSegment``
        """
        # biologicalAnnotation
        if not segment.biologicalAnnotation:
            print_date("No biological anotation found! Use 'add' to first add a new annotation.")
        else:
            bA = segment.biologicalAnnotation
            if self.description:
                bA.description = None
            if self.numberOfInstances:
                bA.numberOfInstances = None
            if self.externalReferenceId is not None: # it could be 0, which is valid but False
                if bA.externalReferences:
                    try:
                        del bA.externalReferences[self.externalReferenceId] # externalReferences is a list
                    except IndexError:
                        print_date("Failed to delete external reference of ID {}".format(self.externalReferenceId))
                else:
                    print_date("No external references to delete from.")
            segment.biologicalAnnotation = bA
        # complexesAndMacromolecules
        if not segment.complexesAndMacromolecules:
            print_date("No complexes and macromolecules found! Use 'add' to first add a new set.")
        else:
            cAM = segment.complexesAndMacromolecules
            # complexes
            if self.complexId is not None:
                if cAM.complexes:
                    try:
                        cAM.complexes.delete_at(self.complexId)
                    except IndexError:
                        print_date("Failed to delete macromolecule of ID {}".format(self.complexId))
                else:
                    print_date("No complexes to delete from.")
            # macromolecules
            if self.macromoleculeId is not None:
                if cAM.macromolecules:
                    try:
                        cAM.macromolecules.delete_at(self.macromoleculeId)
                    except IndexError:
                        print_date("Failed to delete macromolecule of ID {}".format(self.macromoleculeId))
                else:
                    print_date("No macromolecules to delete from.")
            segment.complexesAndMacromolecules = cAM
        return segment


def add_note(args):
    """Add annotation to a segment specified in args
    
    :param args: parsed arguments
    :type args: ``argparse.Namespace``
    """
    if re.match(r'.*\.sff$', args.sff_file, re.IGNORECASE):
        sff_seg = schema.SFFSegmentation(args.sff_file, silence=True)
    elif re.match(r'.*\.hff$', args.sff_file, re.IGNORECASE):
        with h5py.File(args.sff_file) as h:
            sff_seg = schema.SFFSegmentation.from_hff(h)
    elif re.match(r'.*\.json$', args.sff_file, re.IGNORECASE):
        sff_seg = schema.SFFSegmentation.from_json(args.sff_file)
    else:
        print_date("Invalid file type: {}".format(args.sff_file))
        return 1
    found_segment = False
    for segment in sff_seg.segments:
        if segment.id in args.segment_id:
            note = Note(args)
            sff_seg.segment = note.add_to_segment(segment)
            print NoteView(sff_seg.segment, _long=True)
            found_segment = True
            break
        
    if not found_segment:
        print_date("Segment of ID(s) {} not found".format(", ".join(map(str, args.segment_id))))
        
    # export
    sff_seg.export(args.sff_file)
        
    return 0


def edit_note(args):
    """Edit annotation to a segment specified in args
    
    :param args: parsed arguments
    :type args: ``argparse.Namespace``
    """
    if re.match(r'.*\.sff$', args.sff_file, re.IGNORECASE):
        sff_seg = schema.SFFSegmentation(args.sff_file, silence=True)
    elif re.match(r'.*\.hff$', args.sff_file, re.IGNORECASE):
        with h5py.File(args.sff_file) as h:
            sff_seg = schema.SFFSegmentation.from_hff(h)
    elif re.match(r'.*\.json$', args.sff_file, re.IGNORECASE):
        sff_seg = schema.SFFSegmentation.from_json(args.sff_file)
    
    found_segment = False
    for segment in sff_seg.segments:
        if segment.id in args.segment_id:
            note = Note(args)
            sff_seg.segment = note.edit_in_segment(segment)
            print NoteView(sff_seg.segment, _long=True)
            found_segment = True
            break
    
    if not found_segment:
        print_date("Segment of ID(s) {} not found".format(", ".join(map(str, args.segment_id))))
    
    # export
    sff_seg.export(args.sff_file)
    
    return 0


def del_note(args):
    """Delete annotation to a segment specified in args
    
    :param args: parsed arguments
    :type args: ``argparse.Namespace``
    """
    if re.match(r'.*\.sff$', args.sff_file, re.IGNORECASE):
        sff_seg = schema.SFFSegmentation(args.sff_file, silence=True)
    elif re.match(r'.*\.hff$', args.sff_file, re.IGNORECASE):
        with h5py.File(args.sff_file) as h:
            sff_seg = schema.SFFSegmentation.from_hff(h)
    elif re.match(r'.*\.json$', args.sff_file, re.IGNORECASE):
        sff_seg = schema.SFFSegmentation.from_json(args.sff_file)
        
    found_segment = False
    for segment in sff_seg.segments:
        if segment.id in args.segment_id:
            note = Note(args)
            sff_seg.segment = note.del_from_segment(segment)
            print NoteView(sff_seg.segment, _long=True)
            found_segment = True
            break
    
    if not found_segment:
        print_date("Segment of ID(s) {} not found".format(", ".join(map(str, args.segment_id))))
    
    # export
    sff_seg.export(args.sff_file)
        
    return 0


def merge(args):
    """Merge two EMDB-SFF files
    
    :param args: parsed arguments
    :type args: ``argparse.Namespace``
    """
    # sff_file1
    if args.verbose:
        print_date("Reading in file 1: {}...".format(args.sff_file1))
    if re.match(r'.*\.sff$', args.sff_file1, re.IGNORECASE):
        sff_seg1 = schema.SFFSegmentation(args.sff_file1, silence=True)
    elif re.match(r'.*\.hff$', args.sff_file1, re.IGNORECASE):
        with h5py.File(args.sff_file1) as h:
            sff_seg1 = schema.SFFSegmentation.from_hff(h)
    elif re.match(r'.*\.json$', args.sff_file1, re.IGNORECASE):
        sff_seg1 = schema.SFFSegmentation.from_json(args.sff_file1)
    # sff_file2
    if args.verbose:
        print_date("Reading in file 2: {}...".format(args.sff_file2))
    if re.match(r'.*\.sff$', args.sff_file2, re.IGNORECASE):
        sff_seg2 = schema.SFFSegmentation(args.sff_file2, silence=True)
    elif re.match(r'.*\.hff$', args.sff_file2, re.IGNORECASE):
        with h5py.File(args.sff_file2) as h:
            sff_seg2 = schema.SFFSegmentation.from_hff(h)
    elif re.match(r'.*\.json$', args.sff_file2, re.IGNORECASE):
        sff_seg2 = schema.SFFSegmentation.from_json(args.sff_file2)
    if args.verbose:
        print_date("Merging annotations...")
    sff_seg1.merge_annotation_from(sff_seg2)
    # export
    if args.verbose:
        print_date("Writing output to {}".format(args.output))
    sff_seg1.export(args.output)
    if args.verbose:
        print_date("Done.")
    
    return 0


def save(args):
    """Save changes made
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    temp_file = configs['__TEMP_FILE']
    if os.path.exists(temp_file):
        # temp_file: file.sff; args.sff_file: file.sff     copy
        # temp_file: file.hff; args.sff_file: file.hff     copy
        # temp_file: file.json; args.sff_file: file.json   copy
        if (re.match(r'.*\.sff$', temp_file, re.IGNORECASE) and re.match(r'.*\.sff$', args.sff_file, re.IGNORECASE)) or \
            (re.match(r'.*\.hff$', temp_file, re.IGNORECASE) and re.match(r'.*\.hff$', args.sff_file, re.IGNORECASE)) or \
            (re.match(r'.*\.json$', temp_file, re.IGNORECASE) and re.match(r'.*\.json$', args.sff_file, re.IGNORECASE)):
            print_date("Copying temp file {} to {}...".format(temp_file, args.sff_file))
            shutil.copy(temp_file, args.sff_file)
            print_date("Deleting temp file {}...".format(temp_file))
            os.remove(temp_file)
            assert not os.path.exists(temp_file)
        # temp_file: file.sff; args.sff_file: file.hff     convert
        # temp_file: file.sff; args.sff_file: file.json    convert
        # temp_file: file.hff; args.sff_file: file.sff     convert
        # temp_file: file.hff; args.sff_file: file.json    convert
        elif (re.match(r'.*\.sff$', temp_file, re.IGNORECASE) and (re.match(r'.*\.hff$', args.sff_file, re.IGNORECASE) or re.match(r'.*\.json$', args.sff_file, re.IGNORECASE))) or \
            (re.match(r'.*\.hff$', temp_file, re.IGNORECASE) and (re.match(r'.*\.json$', args.sff_file, re.IGNORECASE) or re.match(r'.*\.sff$', args.sff_file, re.IGNORECASE))):
            cmd = shlex.split("convert -v {} -o {}".format(temp_file, args.sff_file))
            _args = parse_args(cmd)
            handle_convert(_args) # convert
            print_date("Deleting temp file {}...".format(temp_file))
            os.remove(temp_file)
            assert not os.path.exists(temp_file)
        # temp_file: file.json; args.sff_file: file.sff    merge
        # temp_file: file.json; args.sff_file: file.hff    merge
        elif re.match(r'.*\.json$', temp_file, re.IGNORECASE) and (re.match(r'.*\.sff$', args.sff_file, re.IGNORECASE) or re.match(r'.*\.hff$', args.sff_file, re.IGNORECASE)):
            json_seg = schema.SFFSegmentation.from_json(temp_file)
            if re.match(r'.*\.sff$', args.sff_file, re.IGNORECASE):
                seg = schema.SFFSegmentation(args.sff_file, silence=True)
            elif re.match(r'.*\.hff$', args.sff_file, re.IGNORECASE):
                with h5py.File(args.sff_file) as h:
                    seg = schema.SFFSegmentation.from_hff(h)
            # merge
            seg.merge_annotation_from(json_seg)
            seg.export(args.sff_file)
            print_date("Deleting temp file {}...".format(temp_file))
            os.remove(temp_file)
            assert not os.path.exists(temp_file)
    else:
        print_date("Missing temp file {}. First perform some edit actions ('add', 'edit', 'del') before trying to save.".format(temp_file))
    return 0


def trash(args):
    """Trash changes made
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    temp_file = configs['__TEMP_FILE']
    if os.path.exists(temp_file):
        print_date("Discarding all changes made in temp file {}...".format(temp_file), newline=False)
        os.remove(temp_file)
        assert not os.path.exists(temp_file)
        print_date("Done", incl_date=False)
    else:
        print_date("Unable to discard with missing temp file {}. No changes made.".format(temp_file))
    return 0


def main():
    """Main function"""
    

    return 0

if __name__ == "__main__":
    sys.exit(main())