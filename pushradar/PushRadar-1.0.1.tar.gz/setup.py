from setuptools import setup

# Create the setup function
setup(
    name='PushRadar',
    version='1.0.1',
    description="PushRadar's official Python library, wrapping the PushRadar API.",
    url='https://github.com/pushradar/pushradar-python',
    download_url='https://github.com/pushradar/pushradar-python/archive/v1.0.1.tar.gz',
    author='PushRadar',
    author_email='contact@pushradar.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    keywords='pushradar realtime push notifications api development websockets',
    packages=['PushRadar']
)