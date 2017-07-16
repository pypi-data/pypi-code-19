import re
import itertools

from tek.tools import index_of, find
from golgi import cli
from golgi.logging import golgi_logger

logger = golgi_logger('paludis')


class Package(object):

    def __init__(self, _type, name, version, desc, new_use, reasons):
        self.type = _type
        self.name = name
        self.version = version
        self.description = desc
        self.new_use = new_use
        self.reasons = reasons

    def __str__(self):
        _str = '{} {}-{}'
        _str = _str.format(self.type, self.name, self.version)
        if self.description:
            _str += '\n' + self.description
        if self.new_use:
            _str += '\n' + 'changed use: ' + ' '.join(self.new_use)
        return _str

    @property
    def str_for_new(self):
        return str(self) + '\n' + self.reasons

install_begin_rex_s = (r'^(?P<type>[nusr])\s+(?P<pkg>[^/]+/[^:]+)[^ ]+'
                       r'\s*(?P<version>[^ ]+)')
install_begin_rex = re.compile(install_begin_rex_s)
desc_rex = re.compile(r'\s+"(.*)"')
new_use_rex = re.compile(r'.*\*')
errors_begin_s = 'I encountered the following errors'
hints_begin_s = 'I cannot proceed without being permitted'
reasons_rex = re.compile(r'\s+Reasons:')


def package_factory(package_line, *lines):
    match = install_begin_rex.match(package_line)
    if not match:
        return None
    _type, package, version = match.groups()
    match = desc_rex.match(lines[0])
    if match:
        desc = match.group(1) if match else ''
        lines = lines[1:]
    else:
        desc = ''
    use_list = lines[0].split()
    new_use = list(filter(new_use_rex.match, use_list))
    new_use = [use[:-1] for use in new_use]
    reasons = find(reasons_rex.match, lines) or ''
    reasons = reasons.strip()
    return Package(_type, package, version, desc, new_use, reasons)


def is_errors_begin(line):
    return line.startswith(errors_begin_s) or line.startswith(hints_begin_s)


def parse_output(lines):
    end_installs_rex = re.compile('^Total')
    end_installs = index_of(end_installs_rex.match, lines)
    installs = lines[:end_installs]
    begins = [i for i, m in
              enumerate(map(install_begin_rex.match, installs))
              if m] + [len(installs)]
    package_blocks = (installs[i:j] for i, j in zip(begins[:-1], begins[1:]))
    packages = list(itertools.starmap(package_factory, package_blocks))
    errors_begin = index_of(is_errors_begin, lines)
    errors = lines[errors_begin:] if errors_begin is not None else None
    return packages, errors


def print_summary(packages, errors):
    def trivial_update(package):
        return package.type == 'u' and not package.new_use

    def new_use_update(package):
        return package.type in ['u', 'r'] and package.new_use

    def new_package(package):
        return package.type in ['s', 'n']
    updates = list(filter(trivial_update, packages))
    if updates:
        logger.info('Trivial package updates:\n')
        logger.info('\n'.join((p.name for p in updates)))
        logger.info('')
    new_use = list(filter(new_use_update, packages))
    if new_use:
        logger.info('Installs with use changes:\n')
        logger.info('\n\n'.join(map(str, new_use)))
        logger.info('')
    new_packages = list(filter(new_package, packages))
    if new_packages:
        logger.info('New packages:\n')
        logger.info('\n\n'.join((p.str_for_new for p in new_packages)))
        logger.info('')
    if errors:
        logger.warning('\n'.join(errors))


@cli()
def summary():
    import sys
    output = sys.stdin.read().splitlines()
    print_summary(*parse_output(output))


__all__ = ('parse_output', 'print_summary')
