from distutils.core import setup

NAME = 'baseZhang'
_MAJOR = 1
_MINOR = 5
_MICRO = 3
VERSION = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
DESCRIPTION = "mir-feature-tools @ZHANG Xu-long"


def long_description():
    readme = open('README.md', 'r').read()
    changelog = open('CHANGELOG.md', 'r').read()
    return changelog + '\n\n' + readme


setup(
    packages=['baseZhang', 'pymir'],
    data_files=[('./', ['CHANGELOG.md', 'README.md']),
        ('./docs/', [ 'docs/install.md','docs/pymir.md','docs/pythonTutorial.md']),
                ('./docs/img/', ['docs/img/pycharm_command_line_arguments.png','docs/img/pycharm_create_new_project.png','docs/img/pycharm_create_new_project_pure_python.png','docs/img/pycharm_hello_open.png','docs/img/pycharm_new_file_input.png','docs/img/pycharm_new_python_file.png','docs/img/pycharm_open.png','docs/img/pycharm_output.png','docs/img/pycharm_run.png','docs/img/terminal_screenshot.png']),
               ]
    ,
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description(),
    author="ZHANG Xu-long",
    author_email="fudan0027zxl@gmail.com",
    license="BSD",
    url="http://zhangxulong.site",
    keywords='audio music sound',
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",

    ],
    install_requires=['stft==0.5.2','numpy==1.12.1', 'pandas==0.19.2', 'matplotlib==2.0.0', 'h5py==2.7.0', 'tqdm==4.11.2',
                      'PyAudio==0.2.11', 'pydub==0.18.0', 'pyPdf==1.13', 'PyYAML==3.12', 'six==1.10.0',
                      'SoundFile==0.9.0.post1', 'Theano==0.9.0', 'scikit-learn==0.18.1', 'Keras==1.2.2',
                      'librosa==0.5.0'],
)
