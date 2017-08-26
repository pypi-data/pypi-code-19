from __future__ import unicode_literals

import csv
import os
import re

from past.builtins import basestring

import inflection


class Base(object):
    def __init__(self, column):
        self.column = column
        self.name = self.column + '_' + inflection.underscore(self.__class__.__name__)
        
    def transform(self, data):
        if self.name not in data.index:
            data[self.name] = data[self.column].apply(self.transform_datum)

        return data[self.name]
    

class AreaCode(Base):
    """Transforms various phone number formats into area codes (strings)
    
    e.g. '12345678901' => '234'
         '+1 (234) 567-8901' => '234'
         '1234567' => ''
         float.nan => None
    """

    COUNTRY_DIGITS = re.compile(r'^\+?1(\d{10})$', re.UNICODE)
    PUNCTUATED = re.compile(r'(?:1[.\-]?)?\s?\(?(\d{3})\)?\s?[.\-]?[\d]{3}[.\-]?[\d]{4}', re.UNICODE)

    def __init__(self, column):
        super(AreaCode, self).__init__(column)
        
    def transform_datum(self, datum):
        if not isinstance(datum, basestring):
            return None

        match = re.match(AreaCode.COUNTRY_DIGITS, datum)
        if match:
            return match.group(1)[0:3]
    
        match = re.match(AreaCode.PUNCTUATED, datum)
        if match:
            return match.group(1)

        return ''


class EmailDomain(Base):
    """Transforms email addresses into their full domain name
    
    e.g. 'bob@bob.com' => 'bob.com'
    """
    NAIVE = re.compile(r'^[^@]+@(.+)$', re.UNICODE)

    def transform_datum(self, datum):
        if not isinstance(datum, basestring):
            return None
            
        match = re.match(EmailDomain.NAIVE, datum)
        if match:
            return match.group(1)

        return ''


class NameStats(Base):
    LOOKUP = {}
    SEX = 0
    AGE = 1
    POPULATION = 2
    
    with open(os.path.join(os.path.dirname(__file__), 'data', 'names.csv'), 'r') as file:
        reader = csv.reader(file)
        for line in reader:
            LOOKUP[line[0]] = (float(line[1]), float(line[2]), float(line[3]))
            

class NameSex(NameStats):
    def transform_datum(self, datum):
        if not isinstance(datum, basestring):
            return None

        lower = datum.lower()
        if lower in NameStats.LOOKUP:
            return NameStats.LOOKUP[lower][NameStats.SEX]

        return -1


class NamePopulation(NameStats):
    def transform_datum(self, datum):
        if not isinstance(datum, basestring):
            return None

        lower = datum.lower()
        if lower in NameStats.LOOKUP:
            return NameStats.LOOKUP[lower][NameStats.POPULATION]

        return -1


class NameAge(NameStats):
    def transform_datum(self, datum):
        if not isinstance(datum, basestring):
            return None
            
        lower = datum.lower()
        if lower in NameStats.LOOKUP:
            return NameStats.LOOKUP[lower][NameStats.AGE]

        return -1

    
class NameFamilial(Base):
    NAIVE = re.compile(r'\b(mom|dad|mother|father|mama|papa|bro|brother|sis|sister)\b', re.UNICODE | re.IGNORECASE)
    
    def transform_datum(self, datum):
        if not isinstance(datum, basestring):
            return None
        
        match = re.match(NameFamilial.NAIVE, datum)
        if match:
            return 1
        
        return 0
