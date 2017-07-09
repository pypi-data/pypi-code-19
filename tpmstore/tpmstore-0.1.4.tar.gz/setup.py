#
# tpmstore - TeamPasswordManager lookup plugin for Ansible.
# Copyright (C) 2017 Andreas Hubert
# See LICENSE.txt for licensing details
#
# File: setup.py
#

from __future__ import print_function;

try:
    from setuptools import setup;
except ImportError:
    from ez_setup import use_setuptools;
    use_setuptools();

from setuptools.command.install import install;
from setuptools.command.sdist import sdist;
from setuptools.command.develop import develop;
from setuptools import setup;
from codecs import open;
import traceback;
import os;
import sys;
import re;
import stat;


pkg_name = 'tpmstore';
pkg_ver = '0.1.4';

cmdclass = {};


def pre_build_toolkit():
    print("[INFO] checking whether 'ansible' python package is installed ...");
    ansible_dirs = _find_py_package('ansible');
    if len(ansible_dirs) == 0:
        print("[ERROR] 'ansible' python package was not found");
        return [];
    print("[INFO] the path to 'ansible' python package is: " + str(ansible_dirs));
    for ansible_dir in ansible_dirs:
        for suffix in ['.py', '.pyc']:
            plugin_type = 'plugins/lookup'
            plugin_file = os.path.join(ansible_dir, plugin_type , pkg_name + suffix);
            try:
                os.unlink(plugin_file);
            except:
                pass;
            try:
                os.remove(plugin_file);
            except:
                pass;
            if os.path.exists(plugin_file):
                print("[ERROR] 'ansible' python package contains traces '" + pkg_name + "' package ("+ plugin_file +"), failed to delete, aborting!");
            else:
                print("[INFO] 'ansible' python package contains traces '" + pkg_name + "' package ("+ plugin_file +"), deleted!");
    return ansible_dirs;

def _find_utility(name):
    x = any(os.access(os.path.join(path, name), os.X_OK) for path in os.environ["PATH"].split(os.pathsep));
    return x;

def _find_py_package(name):
    pkg_dirs = [];
    for path in sys.path:
        if not re.search('site-packages$', path):
            continue;
        if not os.path.exists(path):
            continue;
        if not os.path.isdir(path):
            continue
        target = os.path.join(path, name);
        if not os.path.exists(target):
            continue;
        if not os.path.isdir(target):
            continue;
        if target not in pkg_dirs:
            pkg_dirs.append(target);
    return pkg_dirs;

def _post_build_toolkit(ansible_dirs, plugin_dir=None):
    if plugin_dir is None:
        plugin_dirs = _find_py_package(pkg_name);
        if len(plugin_dirs) > 0:
            print("[INFO] the path to '" + pkg_name + "' python package is: " + str(plugin_dirs));
            for d in plugin_dirs:
                if re.search('bdist', d) or re.search('build', d):
                    continue;
                plugin_dir = d;
                break;
    if plugin_dir is None:
        print("[ERROR] failed to find '" + pkg_name + "' python package, aborting!");
        return;
    if re.search('bdist', plugin_dir) or re.search('build', plugin_dir):
        return;
    if re.search('site-packages.?$', plugin_dir):
        plugin_dir += pkg_name;
    print("[INFO] the path to '" + pkg_name + "' python package is: " + str(plugin_dir));
    '''
    Create a symlink, i.e. `ln -s TARGET LINK_NAME`
    '''
    _egg_files = [];
    for ansible_dir in ansible_dirs:
        symlink_target = os.path.join(plugin_dir, 'tpmstore.py');
        symlink_name = os.path.join(ansible_dir, 'plugins/lookup/tpmstore.py');
        try:
            os.symlink(symlink_target, symlink_name);
            os.chmod(symlink_name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH);
            _egg_files.append(symlink_name);
            _egg_files.append(symlink_name + 'c');
            print("[INFO] created symlink '" + symlink_name + "' to plugin '" + symlink_target + "'");
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info();
            print('[ERROR] an attempt to create a symlink ' + symlink_name + ' to plugin ' + symlink_target + ' failed, aborting!');
            print(traceback.format_exception(exc_type, exc_value, exc_traceback));
    return;

class install_(install):
    def run(self):
        ansible_dirs = pre_build_toolkit();
        if len(ansible_dirs) == 0:
            return 1;
        install.run(self);
        if len(ansible_dirs) > 0:
            self.execute(_post_build_toolkit, (ansible_dirs, self.install_lib, ), msg="running post_install_scripts");

cmdclass['install'] = install_;

class uninstall_(develop):
    def run(self):
        plugin_dirs = [];
        for dp in sys.path:
            if not re.search('site-packages$', dp):
                continue;
            ds = [name for name in os.listdir(dp) if os.path.isdir(os.path.join(dp, name))];
            if ds:
                for d in ds:
                    if not re.match(pkg_name, d):
                        continue;
                    if os.path.join(dp, d) not in plugin_dirs:
                        plugin_dirs.append(os.path.join(dp, d));
        if plugin_dirs:
            for dp in plugin_dirs:
                try:
                    for root, dirs, files in os.walk(dp, topdown=False):
                        for name in files:
                            if os.path.islink(os.path.join(root, name)):
                                os.unlink(os.path.join(root, name));
                            else:
                                os.remove(os.path.join(root, name));
                        for name in dirs:
                            os.rmdir(os.path.join(root, name));
                    os.rmdir(dp);
                    print("[INFO] deleted '" + dp + "'");
                except:
                    print("[INFO] failed to delete '" + dp + "'");
                    exc_type, exc_value, exc_traceback = sys.exc_info();
                    print(traceback.format_exception(exc_type, exc_value, exc_traceback));
        else:
            print("[INFO] no relevant files for the uninstall found, all clean");

        ansible_dirs = _find_py_package('ansible');
        if len(ansible_dirs) == 0:
            print("[ERROR] 'ansible' python package was not found");
            return;
        for ansible_dir in ansible_dirs:
            for suffix in ['.py', '.pyc']:
                plugin_type = 'plugins/lookup'
                plugin_file = os.path.join(ansible_dir, plugin_type , pkg_name + suffix);
                try:
                    os.unlink(plugin_file);
                except:
                    pass;
                try:
                    os.remove(plugin_file);
                except:
                    pass;
        return;


cmdclass['uninstall'] = uninstall_;

pkg_dir = os.path.abspath(os.path.dirname(__file__));
pkg_license='OSI Approved :: GNU General Public License v3 or later (GPLv3+)';
pkg_description = 'Lookup TeamPasswordManager from Ansible.';
pkg_url = 'https://github.com/peshay/' + pkg_name;
#pkg_download_url = 'http://pypi.python.org/packages/source/' + pkg_name[0] + '/' + pkg_name + '/' + pkg_name + '-' + pkg_ver + '.tar.gz';
pkg_download_url = 'https://github.com/peshay/tpmstore/archive/master.zip';
pkg_author = 'Andreas Hubert';
pkg_author_email = 'anhubert@gmail.com';
pkg_packages = [pkg_name.lower()];
pkg_requires = ['ansible>=2.0', 'tpm'];
pkg_data=[
    'plugins/lookup/*.py',
    'README',
    'LICENSE.txt',
];
pkg_platforms='any';
pkg_classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: ' + pkg_license,
    'Programming Language :: Python',
    'Operating System :: POSIX :: Linux',
    'Topic :: Utilities',
    'Topic :: System :: Systems Administration',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6'
];
pkg_keywords=[
    'ansible',
    'ansible plugin',
    'console',
    'automation',
];

pkg_long_description=pkg_description;
with open(os.path.join(pkg_dir, pkg_name, 'README'), encoding='utf-8') as f:
    pkg_long_description = f.read();

setup(
    name=pkg_name,
    version=pkg_ver,
    description=pkg_description,
    long_description=pkg_long_description,
    url=pkg_url,
    download_url=pkg_download_url,
    author=pkg_author,
    author_email=pkg_author_email,
    license=pkg_license,
    platforms=pkg_platforms,
    classifiers=pkg_classifiers,
    packages=pkg_packages,
    package_data= {
        pkg_name.lower() : pkg_data,
    },
    keywords=pkg_keywords,
    install_requires=pkg_requires,
    cmdclass=cmdclass
);
