# vim: set fileencoding=utf-8
import re

from regulations.generator import node_types

# A section title comprises
#   - one or more §
#   - a section label like 11.45 or 11.45-50
#   - one or more space or - separators
#   - a section subject
SECTION_TITLE_REGEX = re.compile(u'^§+ ([-.\w]*)[\s-]*(.*)', re.UNICODE)


def appendix_supplement(data):
    """Handle items pointing to an appendix or supplement"""
    node_type = node_types.type_from_label(data['index'])
    if len(data['index']) == 2 and node_type in (node_types.APPENDIX,
                                                 node_types.INTERP):
        element = {}
        if node_type == node_types.INTERP:
            element['is_supplement'] = True
        else:
            element['is_appendix'] = True

        segments = try_split(data['title'])
        if segments:
            element['label'], element['sub_label'] = segments[:2]
        elif '[' in data['title']:
            position = data['title'].find('[')
            element['label'] = data['title'][:position].strip()
            element['sub_label'] = data['title'][position:]
        else:
            element['label'] = data['title']

        element['section_id'] = '-'.join(data['index'])
        return element


def try_split(text, chars=(u'—', '-')):
    """Utility method for splitting a string by one of multiple chars"""
    for c in chars:
        segments = text.split(c)
        if len(segments) > 1:
            return [s.strip() for s in segments]


def section(data):
    """ Parse out parts of a section title. """
    if len(data['index']) == 2 and data['index'][1][0].isdigit():
        element = {}
        element['is_section'] = True
        element['section_id'] = '-'.join(data['index'])
        if u"§§ " == data['title'][:3]:
            element['is_section_span'] = True
        else:
            element['is_section_span'] = False
        match = SECTION_TITLE_REGEX.match(data['title'])
        element['label'] = match.group(1)
        element['sub_label'] = match.group(2)
        return element
