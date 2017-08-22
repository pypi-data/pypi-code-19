import xml.etree.ElementTree as ET
import game
import os
import fileutils
from project import Project

logs = []


def log(msg):
    logs.append(msg)


def validate():
    units = game.get_units_list()
    index = 0
    while os.path.isfile(fileutils.root_dir + '/Resources/ini/maps/map%d.xml' % index):
        root = ET.parse(fileutils.root_dir + '/Resources/ini/maps/map%d.xml' % index).getroot()
        waves = root.find('waves')
        routes = root.find('routes')
        units_on_map = {}

        def validate_route(routeindex):
            try:
                int(routeindex)
            except:
                log('Route with index [{}] not is digit. map{}.xml'.format(routeindex, index))
                return False
            for route in routes:
                if route.attrib['name'] == routeindex:
                    return True
            log('Route with index [{}] not found in map{}.xml'.format(routeindex, index))
            return False

        def validate_routesubtype(rst):
            if rst not in ['main', 'left', 'right', 'random']:
                log('Unknow value of routesubtype [{}] in map{}.xml'.format(rst, index))

        for wave in waves:
            if 'defaultname' in wave.attrib:
                unit = wave.attrib['defaultname']
                if unit not in units:
                    log('Invalid name of unit [{}] in map{}.xml'.format(unit, index))
                units_on_map[unit] = 1
            if 'defaultrouteindex' in wave.attrib:
                validate_route(wave.attrib['defaultrouteindex'])
            if 'defaultroutesubtype' in wave.attrib:
                validate_routesubtype(wave.attrib['defaultroutesubtype'])
            for unitxml in wave:
                unit = unitxml.attrib['name'] if 'name' in unitxml.attrib else ''
                units_on_map[unit] = 1
                if unit and unit not in units:
                    log('Invalid name of unit [{}] in map{}.xml'.format(unit, index))
                if 'routeindex' in unitxml.attrib:
                    validate_route(unitxml.attrib['routeindex'])
                if 'routesubtype' in unitxml.attrib:
                    validate_routesubtype(unitxml.attrib['routesubtype'])
        if 'max_creeps_on_level' in Project.instance.validate:
            max_count = Project.instance.validate['max_creeps_on_level']
        else:
            max_count = 8
        if len(units_on_map) > max_count:
            log('Many creeps in map{}.xml ({}>{})'.format(index, len(units_on_map), max_count))
        index += 1
