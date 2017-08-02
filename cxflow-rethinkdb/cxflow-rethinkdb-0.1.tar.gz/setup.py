from pip.req import parse_requirements
from setuptools import setup

setup(name='cxflow-rethinkdb',
      version='0.1',
      description='RethinkDB plugin for cxflow',
      long_description='Plugin providing RethinkDB support.',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Operating System :: Unix',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
      ],
      keywords='rethinkdb database cxflow',
      url='https://gitlab.com/Cognexa/cxflow-rethinkdb',
      author='Cognexa Solutions s.r.o.',
      author_email='info@cognexa.com',
      license='MIT',
      packages=[
          'cxflow_rethinkdb',
      ],
      include_package_data=True,
      zip_safe=False,
      test_suite='cxflow_rethinkdb.tests',
      install_requires=[str(ir.req) for ir in parse_requirements('requirements.txt', session='hack')],
     )
