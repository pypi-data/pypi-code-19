from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='voiceads',
      version='0.0.5',
      description='VoiceAds.ai Python SDK',
      long_description=readme(),
      classifiers=[
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7'
      ],
      keywords='voiceads,voiceads.ai,alexasdk',
      url='https://bitbucket.org/voiceadsai/voiceads-python-sdk',
      author='Anupam Jain',
      author_email='tech@voiceads.ai',
      license='MIT',
      packages=['voiceads'],
      install_requires=[
          'requests',
      ],
      include_package_data=True,
      zip_safe=False)
