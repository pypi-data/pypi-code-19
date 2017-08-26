from distutils.core import setup
setup(
    name='tsahelper',
    version='0.3.3',
    author='Brian Farrar',
    author_email='brian.farrar@mavenwave.com',
    packages=['tsahelper'],
    url='http://pypi.python.org/pypi/tsahelper/',
    license='LICENSE.txt',
    install_requires=['numpy','seaborn','matplotlib','opencv-contrib-python','pandas','scipy'],
    description='Useful preprocessing TSA HD-AIT image files.',
    long_description=open('README.txt').read()
)
