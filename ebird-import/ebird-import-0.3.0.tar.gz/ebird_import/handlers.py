#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import datetime
import os
import pkg_resources
import re

from shared import read_csv_file


EBIRD_HEADERS = [
    'Common Name',
    'Genus',
    'Species',
    'Number',
    'Species Comments',
    'Location Name',
    'Latitude',
    'Longitude',
    'Date',
    'Start Time',
    'State/Province',
    'Country Code',
    'Protocol',
    'Number of Observers',
    'Duration',
    'All observations reported?',
    'Effort Distance Miles',
    'Effort area acres',
    'Submission Comments',
]


class WorldbirdsHandler(object):

    headers = {
        'BirdLife common name': 6,
        'Location': 7,
        'Latitude': 12,
        'Longitude': 13,
        'Visit date': 21,
        'Start time': 22,
        'End time': 23,
        'Number of observers': 25,
        'Visit notes': 26,
        'Number': 27,
        'All birds recorded?': 34,
        'Visit species notes': 36,
    }

    def __init__(self):
        self.species = {}

    def load_resources(self, species_filename):
        species_file = pkg_resources.resource_filename(
            'ebird_import', species_filename)
        if os.path.exists(species_file):
            self.load_species(self.species, species_file)

    def load_species(self, table, filename):
        """Update the species table with the records from the file.

        arguments:
            table (dict): maps BirdLife common name to the equivalent species
                used by eBird.
            filename (str): the path to a csv formatted file.
        """
        species_table = read_csv_file(filename)
        for entry in species_table:
            key = entry['BirdLife common name']
            table[key] = entry

    def read_header(self, file):
        """Get the names of the fields for the records.

        Skip over the contents of the file until the data section starts, which
        is a line containing only the string 'Data'. The first non-blank row after
        that contains the field names for the exported records.

        A ValueError is raised if the row contains the field names appears to be
        missing.

        arguments:
            fp (File): a file object containing the records.

        returns:
            an array containing the names of the fields.
        """
        headers = []
        next = False
        for line in file:
            line = line.strip()
            if not line:
                continue
            if line.lower() == u'data':
                next = True
            elif next:
                if re.search('\d', line, re.UNICODE):
                    raise ValueError("Found a record instead of the column names")
                headers = line.split('\t')
                break
        if not headers:
            raise ValueError("Could not find row containing column names")
        return headers

    def read_record(self, line, names):
        """Read selected columns from the record into a dict.

        arguments:
            line (unicode): a line read from the file containing a record from
                WorldBirds.
            names (dict): a dict containing of the names of each field and the
                column in the record to extract the value from.

        returns:
            a dict with the field names as the key and the value from the
            corresponding column in the record.
        """
        fields = [column.strip() for column in line.strip().split('\t')]
        return {name: fields[column] for (name, column) in names.iteritems()}

    def convert_species(self, rin):
        """Map the WorldBirds species name to the species name used in eBird.

        In addition to the fields used by eBird a field, species Converted,
        with a value of True or False is added to indicate whether an eBird
        species name matching the BirdLife common name used by WorldBirds was
        found. This is used to identify the records which must either be edited
        before the records are imported into eBird or corrected after the
        initial import.

        arguments:
            rin (dict): the record from WorldBirds

        returns:
            a dict containing the fields for an eBird species.
        """
        name = rin['BirdLife common name']
        rout = {
            'Common Name': '',
            'Genus': '',
            'Species': '',
            }
        if name in self.species:
            rout['Common Name'] = self.species[name]['eBird Common Name']
            rout['Species Converted'] = True
        else:
            rout['Common Name'] = name
            rout['Species Converted'] = False
        return rout

    def convert_location(self, rin):
        """Map the location fields to the fields used in eBird.

        arguments:
            rin (dict): the record from WorldBirds

        returns
            a dict containing the fields for an eBird location.

        """
        return {
            'Location Name': rin['Location'],
            'Latitude': rin['Latitude'],
            'Longitude': rin['Longitude'],
            'State/Province': '',
            'Country Code': '',
            'Location Converted': False,
            }

    def convert_record(self, rin):
        """Convert the record from WorldBirds to the format used by eBird.

        In addition to mapping the different fields and values the conversion
        also handles mapping locations and species names used in WorldBirds to the
        equivalent locations and species named used in eBird. If a mapping cannot
        be found then the value(s) from the WorldBirds record will be added
        directly allowing the mapping to be performed when the records are imported
        into eBird.

        arguments:
            record_in (dict): a dict containing the fields names and values from
                the WorldBirds record.

        returns:
            a dict mapping the names and values from the WorldBirds record to the
            format used by eBird.
        """
        rout = {
            'Protocol': '',
            'Effort Distance Miles': '',
            'Effort area acres': '',
            }

        rout.update(self.convert_species(rin))

        if not rin['Number'] or rin['Number'].lower() == 'present':
            rout['Number'] = 'X'
        else:
            rout['Number'] = rin['Number']

        rout['Species Comments'] = rin['Visit species notes'].replace('"', "'")

        rout.update(self.convert_location(rin))

        date = datetime.datetime.strptime(rin['Visit date'], "%Y-%m-%d")
        rout['Date'] = date.strftime("%m/%d/%Y")

        start_time = datetime.datetime.strptime(rin['Start time'], "%H:%M")
        rout['Start Time'] = start_time.strftime("%H:%M")

        end_time = datetime.datetime.strptime(rin['End time'], "%H:%M")
        duration_hours = (end_time - start_time).seconds / 3600
        duration_minutes = ((end_time - start_time).seconds % 3600) / 60
        rout['Duration'] = "%d" % (duration_hours * 60 + duration_minutes)

        rout['Number of Observers'] = rin['Number of observers']
        rout['All observations reported?'] = rin['All birds recorded?'][0].upper()
        rout['Submission Comments'] = rin['Visit notes'].replace('"', "'")

        return rout

    def convert_file(self, filein, fileout):
        fout = None
        record_number = 1

        fin = codecs.open(filein, 'rb', 'utf-16')
        self.read_header(fin)

        for line in fin:
            rin = self.read_record(line, self.headers)
            rout = self.convert_record(rin)
            if not fout:
                fout = open(fileout, 'wb')
            row = ['"%s"' % rout[name] for name in EBIRD_HEADERS]
            fout.write(','.join(row).encode('utf-8'))
            fout.write('\r\n')
            record_number += 1

        fin.close()
        fout.close()
