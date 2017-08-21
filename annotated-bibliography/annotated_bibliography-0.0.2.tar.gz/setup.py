from setuptools import setup

setup(name='annotated_bibliography',
      version='0.0.2',
      description='Simple annotated bibliography generator',
      url='https://github.com/manoelhortaribeiro/annotated_bibliography',
      download_url='https://github.com/manoelhortaribeiro/annotated_bibliography/dist/annotated_bibliography-0.1.tar.gz',
      author='Manoel Horta Ribeiro',
      author_email='manoelhortaribeiro@gmail.com',
      license='MIT',
      packages=['annotated_bibliography'],
      keywords='bibliography research annotations',
      install_requires=['matplotlib', 'mistune', 'pybtex', 'jinja2', 'numpy'],
      entry_points={
            'console_scripts': ['make_ann_bib=annotated_bibliography.make_ann_bib:make_html']
      },
      include_package_data=True,
      zip_safe=False)
