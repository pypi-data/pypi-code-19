#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sfftk.notes.view



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

import re
import sys
import textwrap

import h5py

from sfftk import schema
from sfftk.core.print_tools import print_date


__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-04-07"


def _add_index(L, pre="\t"):
    """Add indexes to items in L"""
    LL = list()
    i = 0
    for l in L:
        LL.append("{}{}: {}".format(pre, i, l))
        i += 1
    return LL

class View(object):
    DISPLAY_WIDTH = 100
    NOT_DEFINED = "-*- NOT DEFINED -*-"
    LINE1 = '=' * DISPLAY_WIDTH
    LINE2 = '-' * DISPLAY_WIDTH
    LINE3 = '*' * DISPLAY_WIDTH


class NoteView(View):
    """NoteView class
    
    Display annotation for a single segment
    """
    def __init__(self, segment, _long=False):
        self._segment = segment
        self._long = _long
    @property
    def id(self):
        return self._segment.id
    @property
    def parentID(self):
        return self._segment.parentID
    @property
    def description(self):
        if self._segment.biologicalAnnotation.description:
            return textwrap.fill(self._segment.biologicalAnnotation.description, self.DISPLAY_WIDTH)
        else:
            return self.NOT_DEFINED
    @property
    def numberOfInstances(self):
        if self._segment.biologicalAnnotation.numberOfInstances:
            return self._segment.biologicalAnnotation.numberOfInstances
        else:
            return self.NOT_DEFINED
    @property
    def externalReferences(self):
        if self._segment.biologicalAnnotation:
            string_list = list()
            string_list.append(
                "\t{:<20}\t{:<20}\t{:<20}".format(
                    "#  ontology",
                    "type",
                    "term",
                    )
                )
            string_list.append("\t" + "-" * (self.DISPLAY_WIDTH - len("\t".expandtabs())))
            i = 0
            for extRef in self._segment.biologicalAnnotation.externalReferences:
                string_list.append(
                    "\t{}: {:<20}\t{:<20}\t{:<20}".format(
                        i,
                        extRef.type,
                        extRef.otherType if extRef.otherType else '-',
                        extRef.value,
                        )
                    )
                i += 1
            return "\n".join(string_list)
        else:
            return "\t" + self.NOT_DEFINED 
    @property
    def complexes(self):
        if self._segment.complexesAndMacromolecules:
            return "\n".join(_add_index(self._segment.complexesAndMacromolecules.complexes))
        else:
            return "\t" + self.NOT_DEFINED
    @property
    def macromolecules(self):
        if self._segment.complexesAndMacromolecules:
            return "\n".join(_add_index(self._segment.complexesAndMacromolecules.macromolecules))
        else:
            return "\t" + self.NOT_DEFINED
    @property
    def colour(self):
        if self._segment.colour.name:
            return self._segment.colour.name
        elif self._segment.colour.rgba:
            return str(self._segment.colour.rgba)
        else:
            return self.NOT_DEFINED
    @property
    def segmentType(self):
        segment_type = list()
        if self._segment.contours:
            segment_type.append("contourList")
        if self._segment.meshes:
            segment_type.append("meshList")
        if self._segment.shapes:
            segment_type.append("shapePrimitiveList")
        if self._segment.volume:
            segment_type.append("threeDVolume")
        # sanity check
        assert len(segment_type) > 0
        return ", ".join(segment_type)
    def __str__(self):
        if self._long:
            string = """\
            \r{}
            \rID:\t\t{}
            \rPARENT ID:\t{}
            \rSegment Type:\t{}
            \r{}
            \rDescription:
            \r\t{}
            \rNumber of instances:
            \r\t{}
            \r{}
            \rExternal References:
            \r{}
            \r{}
            \rComplexes:
            \r{}
            \rMacromolecules:
            \r{}
            \r{}
            \rColour:
            \r\t{}\
            """.format(
                # ****
                self.LINE3,
                self.id,
                self.parentID,
                self.segmentType,
                # ---
                self.LINE2,
                self.description,
                self.numberOfInstances,
                # -----
                self.LINE2,
                self.externalReferences,
                # ----
                self.LINE2,
                self.complexes,
                self.macromolecules,
                # ----
                self.LINE2,
                self.colour,
                )
        else:
            string = "{:>7}/{:>7}: {:<40} {:<30}".format(
                self.id,
                self.parentID,
                self.description,
                self.colour,
                )
        return string


class HeaderView(View):
    """HeaverView class
    
    Display EMDB-SFF header
    """
    def __init__(self, segmentation):
        self._segmentation = segmentation
    @property
    def name(self):
        return self._segmentation.name
    @property
    def version(self):
        return self._segmentation.version
    @property
    def software(self):
        return u"""\
        \r\tSoftware: {}
        \r\tVersion: {}
        \r\tProcessing details: \n{}\
        """.format(
            self._segmentation.software.name,
            self._segmentation.software.version,
            textwrap.fill(
                u"\t\t" + self._segmentation.software.processingDetails \
                    if self._segmentation.software.processingDetails else '-', 
                self.DISPLAY_WIDTH
                ),
            ).encode('utf-8')
    @property
    def filePath(self):
        return self._segmentation.filePath
    @property
    def primaryDescriptor(self):
        return self._segmentation.primaryDescriptor
    @property
    def details(self):
        if self._segmentation.details:
            return "\n".join(textwrap.wrap(self._segmentation.details, self.DISPLAY_WIDTH))
        else:
            return self.NOT_DEFINED
    def __str__(self):
        string = """\
        \r{}
        \rEMDB-SFF v.{}
        \r{}
        \rSegmentation name:
        \r\t{}
        \rSegmentation software:
        \r{}
        \r{}
        \rPrimary descriptor:
        \r\t{}
        \r{}
        \rSegmentation details:
        \r\t{}
        \r{}\
        """.format(
            # ===
            self.LINE1,
            self.version,
            # ---
            self.LINE2,
            self.name,
            self.software,
            # ---
            self.LINE2,
            self.primaryDescriptor,
            # ----
            self.LINE2,
            self.details,
            # ****
            self.LINE3,
            )
        return string


def list_notes(args):
    """List all notes in an EMDB-SFF file
    
    :param args: parsed arguments
    :type args: ``argparse.Namespace``
    :return int status: 0 is OK, else failure
    """
    if re.match(r'.*\.sff$', args.sff_file, re.IGNORECASE):
        sff_seg = schema.SFFSegmentation(args.sff_file, silence=True)
    elif re.match(r'.*\.hff$', args.sff_file, re.IGNORECASE):
        with h5py.File(args.sff_file) as h:
            sff_seg = schema.SFFSegmentation.from_hff(h)
    elif re.match(r'.*\.json$', args.sff_file, re.IGNORECASE):
        sff_seg = schema.SFFSegmentation.from_json(args.sff_file)
    """
    :TODO: make this optional
    :TODO: define the stream to use
    """
    print HeaderView(sff_seg)
    for segment in sff_seg.segments:
        print NoteView(segment, _long=args.long_format)
    return 0


def show_notes(args):
    """Show notes in an EMDB-SFF file for the specified segment IDs
    
    :param args: parsed arguments
    :type args: ``argparse.Namespace``
    :return int status: 0 is OK, else failure
    """
    if re.match(r'.*\.sff$', args.sff_file, re.IGNORECASE):
        sff_seg = schema.SFFSegmentation(args.sff_file, silence=True)
    elif re.match(r'.*\.hff$', args.sff_file, re.IGNORECASE):
        with h5py.File(args.sff_file) as h:
            sff_seg = schema.SFFSegmentation.from_hff(h)
    elif re.match(r'.*\.json$', args.sff_file, re.IGNORECASE):
        sff_seg = schema.SFFSegmentation.from_json(args.sff_file)
    print HeaderView(sff_seg)
    found_segment = False
    for segment in sff_seg.segments:
        if segment.id in args.segment_id:
            print NoteView(segment, _long=args.long_format)
            found_segment = True
    if not found_segment:
        print_date("No segment with ID(s) {}".format(", ".join(map(str, args.segment_id))))
    return 0


def main():
    """Main function"""
    

    return 0

if __name__ == "__main__":
    sys.exit(main())