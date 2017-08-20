from setuptools import setup

setup(name='linear_regression',
      version='0.1',
      description='Least squares linear regression. y = mx + b or y = mx (i.e. 0 intercept)',
      url='http://github.com/drosenman/linear_regression',
      author='Dave Rosenman',
      author_email='rosenmd1@tcnj.edu',
      license='MIT',
      packages=['linear_regression'],
      install_requires=['numpy', 'pandas'],
      zip_safe=False)