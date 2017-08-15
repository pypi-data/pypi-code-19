"""
The info submodule defines some helper functions producing information about the system itself.
"""
import sys, pkg_resources as pkg


def sysinfo():
    """
    Import different dependencies for the Python modules and check the versions. Returns a dictionary
    of package names given the found version, required version and a glyphicon identifier idicating wether
    the requirements matched or not.
    :return:
    """
    out = dict()

    # Python version
    pv = sys.version_info
    out['python'] = ['%d.%d.%d' % (pv[0], pv[1], pv[2])]
    out['python'].append('3.3')
    out['python'].append('ok' if pv > (3,5) else 'chevron-down')

    for name, requ in dict(numpy='1.9', pandas='0.16', scipy='0.14').items():
        try:
            v = pkg.parse_version(pkg.get_distribution(name).version)
            out[name] = [str(v), requ]
            out[name].append('ok' if v >= pkg.parse_version(requ) else 'chevron-down')
        except pkg.DistributionNotFound:
            out[name] = ['not found', requ]
            out[name].append('remove')

    return out
