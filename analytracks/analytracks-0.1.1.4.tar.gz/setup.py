from setuptools import setup

setup(name='analytracks',
      version='0.1.1.4',
      description='The funniest joke in the world',
      url='http://github.com/ddolbecke/analytracks',
      author='Dimitri de Smet',
      author_email='dimitri.desmet@uclouvain.be',
      license='MIT',
      packages=['analytracks','analytracks.tracks'],
      package_dir={
                    'analytracks.tracks':'analytracks/tracks',
                  },
      package_data={
                    'analytracks.tracks': ['data/*.dat','data/*.key'],
                    'analytracks': ['data/*.dat']
                     },
      install_requires=[
                  'numpy', 'pandas', 'matplotlib', 'seaborn', 
                  'lxml', 'urllib', 'simplejson', 'haversine', 
                  'statsmodels', 'scipy', 'scikit-learn', 
                  'SRTM.py', 'requests', 'mplleaflet'
              ],
      zip_safe=True)
