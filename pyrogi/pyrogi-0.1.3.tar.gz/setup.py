from setuptools import setup, find_packages
import pyrogi

def get_readme_text():
    with open('README.rst') as f:
        return f.read()

setup(
    name = 'pyrogi',
    packages = find_packages(),
    install_requires = ['pygame'],
    version = pyrogi.VERSION,
    description = 'A feature-rich roguelike game engine focused on ease of development and beauty through text graphics.',
    long_description = get_readme_text(),
    license = 'GPLv3',
    author = 'Ben Weedon',
    author_email = 'ben.weedon@outlook.com',
    url = 'https://github.com/BenWeedon/pyrogi',
    download_url = 'https://github.com/BenWeedon/pyrogi/archive/v0.1.0.tar.gz',
    keywords = ['game', 'engine', 'game-engine', 'roguelike', 'ascii'],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Games/Entertainment',
    ],
)
