from setuptools import setup
import os
import os.path


def files(basedir, dirs):
    for directory in dirs:
        for (path, _, file_list) in os.walk(os.path.join(basedir, directory)):
            for filename in file_list:
                yield os.path.relpath(os.path.join(path, filename), basedir)


setup(name='skakdollar',
      version='0.1.3',
      description='The funniest joke in the world',
      url='http://github.com/killall5/skakdollar',
      author='Alexey Tamarevskiy',
      author_email='killall5@me.com',
      license='MIT',
      packages=['skakdollar'],
      package_data=dict(
          skakdollar=list(files('skakdollar', ['templates', 'static']))
      )
)
