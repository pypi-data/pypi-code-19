import setuptools

setuptools.setup(name='pyeuler',
      version='0.0.dev3',
      description='Python Math and Number Theory Library Inspired by Project Euler',
      url='https://github.com/schang1146/pyeuler',
      author='team.pyeuler',
      author_email='team.pyeuler@gmail.com',
      license='MIT',
      classifiers=[
      # Maturity of project:
      #     3 - Alpha
      #     4 - Beta
      #     5 - Production/Stable
      'Development Status :: 3 - Alpha',

      # Specify license (should match "license" above)
      'License :: OSI Approved :: MIT License',

      # Indicate audience
      'Intended Audience :: Science/Research',
      'Topic :: Scientific/Engineering :: Mathematics',

      # Specify supported Python versions
      'Programming Language :: Python :: 3',
      ],
      keywords='project euler math algorithms number theory',
      packages=setuptools.find_packages(exclude=['contrib', 'docs', 'tests*']),
      zip_safe=False)
