from setuptools import setup

setup(name='cuber',
      version='0.20',
      description='Calculation-graph base',
      url='https://github.com/kriot/Cuber',
      author='Georgy Borisenko',
      author_email='borisenko.gn@yandex.ru',
      license='GNU GPLv3',
      packages=['cuber'],
      install_requires=['click', 'numpy'],
      zip_safe=False)
