from setuptools import setup, find_packages

setup(name='pif_ingestor',
      version='0.2.0',
      url='http://github.com/CitrineInformatics/pif-ingestor',
      description='Script to ingest common data formats into Citrination',
      author='Max Hutchinson',
      author_email='maxhutch@citrine.io',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'pif-ingestor = pif_ingestor:drive_cli'
          ]
      },
      install_requires=[
          "pypif",
          "citrination_client",
          "stevedore"
      ],
      extra_require={
          "all" : ["dfttopif"],
          "dft" : ["dfttopif"],
      }
)
