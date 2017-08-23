import os
import sys
import subprocess
import glob

import distutils.command.build as distutils_build
from distutils import log as dist_log
from setuptools import setup, find_packages, Command

basepath = os.path.dirname(__file__)


class NoOptsCmd(Command):
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

class BuildQrc(NoOptsCmd):
    """Builds qrc files with pyrcc"""
    user_options = []

    def run(self):
        subc_dir = os.path.join(basepath, 'src', 'subconvert')
        in_ = os.path.join(subc_dir, 'resources.qrc')
        out = os.path.join(subc_dir, 'resources.py')
        subprocess.check_call(['pyrcc5', '-o', out, in_])


class BuldManpages(NoOptsCmd):
    """Builds manpages in docs/build/man"""
    user_options = []

    def run(self):
        try:
            subprocess.check_call(['make', '-C', 'docs', 'man'])
        except Exception:
            print("Failed to build manpages; they won't be available",
                  file=sys.stderr)

            # Create a dummy manual for the needs of data_files
            manpage = os.path.join('docs', 'build', 'man', 'man1',
                                   'subconvert.1')
            if not os.path.exists(os.path.dirname(manpage)):
                os.makedirs(os.path.dirname(manpage))
            if not os.path.exists(manpage):
                with open(manpage, 'w') as f_:
                    f_.write('Manpage for Subconvert wasn\'t generated\n')


class SubcBuild(distutils_build.build):
    """Overrides a default install_data"""
    user_options = []

    def run(self):
        self.run_command('build_qrc')
        self.run_command('compile_catalog')
        self.run_command('build_man')
        super().run()
        self.clean()

    def clean(self):
        dist_log.info('running build cleanup')
        # establish a path to build/lib, where build artifacts (before creating
        # wheels or bdist) are copied. We'll use distutils_build.build.build_lib
        # property for that.
        build_dir = os.path.join(basepath, self.build_lib)

        # file names relative to build/lib/subconvert directory
        to_clean = [
            'subconvert/resources.qrc'
        ]

        for expr in to_clean:
            for file_ in glob.glob(os.path.join(build_dir, expr)):
                dist_log.info('removing %s' % file_)
                os.unlink(file_)


with open(os.path.join(basepath, 'README.rst'), encoding='utf-8') as f_:
    long_description = f_.read()


def main():
    install_reqs = ['chardet==3.0.4',
                    'pymediainfo==2.1.9',
                    'python-mpv==0.3.2']
    if sys.version_info >= (3, 5):
        install_reqs.append('PyQt5==5.9')
    else:
        try:
            import PyQt5
        except ImportError:
            print('PyQt5 is not found on your system and it\'s not '
                  'available from PIP for your Python version.',
                  file=sys.stderr)
            raise

    setup(name='subconvert',
          description='Movie subtitles converter',
          long_description=long_description,
          use_scm_version={'write_to': '.version.txt'},
          license='GPLv3+',
          author='Michał Góral',
          author_email='dev@mgoral.org',
          url='https://gitlab.com/mgoral/subconvert',
          platforms=['linux'],
          setup_requires=['setuptools_scm', 'babel'],
          install_requires=install_reqs,
          # https://pypi.python.org/pypi?%3Aaction=list_classifiers
          classifiers=['Development Status :: 6 - Mature',
                       'Environment :: Console',
                       'Environment :: X11 Applications :: Qt',
                       'Intended Audience :: End Users/Desktop',
                       'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                       'Natural Language :: English',
                       'Operating System :: POSIX',
                       'Programming Language :: Python :: 3 :: Only',
                       'Programming Language :: Python :: 3.2',
                       'Programming Language :: Python :: 3.3',
                       'Programming Language :: Python :: 3.4',
                       'Programming Language :: Python :: 3.5',
                       'Programming Language :: Python :: 3.6',
                       'Topic :: Utilities',
                       ],

          packages=find_packages('src'),
          package_dir={'': 'src'},

          # package_data is bdist specific
          package_data={'': ['locale/*/LC_MESSAGES/*.mo']},

          data_files=[
              ('share/applications', ['subconvert.desktop']),

              ('share/icons/hicolor/scalable/apps', ['icons/scalable/subconvert.svg']),
              ('share/icons/hicolor/16x16/apps', ['icons/16x16/subconvert.png']),
              ('share/icons/hicolor/22x22/apps', ['icons/22x22/subconvert.png']),
              ('share/icons/hicolor/32x32/apps', ['icons/32x32/subconvert.png']),
              ('share/icons/hicolor/48x48/apps', ['icons/48x48/subconvert.png']),
              ('share/icons/hicolor/128x128/apps', ['icons/128x128/subconvert.png']),
              ('share/icons/hicolor/256x256/apps', ['icons/256x256/subconvert.png']),

              ('share/man/man1', ['docs/build/man/man1/subconvert.1'])
          ],

          entry_points={
              'console_scripts': ['subconvert=subconvert.apprunner:main'],
          },

          cmdclass={
              'build': SubcBuild,
              'build_qrc': BuildQrc,
              'build_man': BuldManpages,
          }
    )

if __name__ == '__main__':
    assert sys.version_info >= (3, 2)
    main()
