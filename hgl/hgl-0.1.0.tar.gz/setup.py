# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.org') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

requirements = [
    'pyopengl',
    'numpy',
    'pillow',
    'pysdl2'
#    'pygame-sdl'
]

dependency_links=[
#    'https://github.com/renpy/pygame_sdl2/archive/master.zip#egg=pygame_sdl2'
    # 'https://github.com/renpy/pygame_sdl2/tarball/master#egg=pygame-sdl2'
    # 'https://github.com/olymk2/pygame-sdl2/tarball/master#egg=pygame-sdl2'
#    'git+ssh://git@github.com/renpy/pygame_sdl2.git/@master#egg=pygame_sdl2'
    'https://bitbucket.org/marcusva/py-sdl2/downloads/PySDL2-0.9.5.zip'
]

setup(
    name='hgl',
    version='0.1.0',
    description='Simple OpenGL helper library for testing code and writting examples with minimal fuss',
    long_description=readme,
    author='Oliver Marks',
    author_email='oly@digitaloctave.com',
    url='https://github.com/olymk2/hgl',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=requirements,
    dependency_links=dependency_links,
    setup_requires=['cython', 'numpy', 'pytest-runner'],
    tests_require=[ 'pytest-cov', 'pytest']
)
