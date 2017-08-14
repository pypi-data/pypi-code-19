from setuptools import setup

with open("README.rst", 'r') as f:
    long_description = f.read()

setup(
   name='aquami',
   version='0.9.4',
   description=''.join(('A module to extract quantitative microstructure ',
                        'information from micrographs of morphologically ',
                        'complex microstructures.')),
   license="MIT",
   long_description=long_description,
   author='Joshua Stuckner',
   author_email='stuckner@vt.edu',
   url="https://github.com/JStuckner/aquami",
   packages=['aquami'],
   install_requires=['matplotlib>=1.5.3',
                     'numpy>=1.12.0',
                     'openpyxl>=2.3.2',
                     'pandas>=0.18.1',
                     'scipy>=0.18.1',
                     'scikit_image>=0.12.3',
                     'Pillow>=4.0.0',
                     'setuptools>=34.3.2'],
   python_requires='>=3',
   package_data={
       'auqami':['ttps/*txt', 'icon.ico'],
       }
)

