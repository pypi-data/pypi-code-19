from setuptools import setup, find_packages
import p4

def get_readme_text():
    with open('README.rst') as f:
        return f.read()

setup(
    name = 'p4',
    packages = find_packages(),
    include_package_data = True,
    install_requires = [],
    version = p4.VERSION,
    description = 'A Python Pre-Processor for the Processing system',
    long_description = get_readme_text(),
    license = 'GPLv3',
    author = 'Ben Weedon',
    author_email = 'ben.weedon@outlook.com',
    url = 'https://github.com/benweedon/p4',
    keywords = ['processing', 'generative', 'artwork', 'art'],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Artistic Software',
        'Topic :: Multimedia :: Graphics',
    ],
)
