"""Setup for Gymbag."""

from setuptools import setup
import os.path
import re

HERE = os.path.abspath(os.path.dirname(__file__))


def clean_rst(rst):
    """:Return: a reStructuredText string `rst` with things that PyPI doesn't like removed."""
    return re.sub(r'\.\. toctree::.*?\n\n(?=\S)', '', rst, flags=re.DOTALL)


def find_version(*file_paths):
    """:Return: the __version__ string from the path components `file_paths`."""
    with open(os.path.join(os.path.dirname(__file__), *file_paths)) as verfile:
        file_contents = verfile.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", file_contents, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='gymbag',
    version=find_version('gymbag', '__init__.py'),
    description='Simple efficient data recording for OpenAI Gym reinforcement learning environments',
    long_description=clean_rst(open(os.path.join(HERE, 'README.rst')).read()),
    url='https://gitlab.com/doctorj/gymbag',
    author='Doctor J',
    license='LGPL-3.0+',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='reinforcement learning openai gym record storage binary hdf5',
    packages=['gymbag'],
    test_suite='tests',
    python_requires='>=3.4',
    install_requires=['numpy', 'gym', 'tables', 'typing'],
    extras_require={'dev': ['scandir', 'mypy', 'pylint', 'sphinx', 'sphinx_rtd_theme', 'twine']},
)
