from setuptools import setup, find_packages

setup(
    name = 'timed-alert',
    version = '0.1',
    packages = find_packages(),
    include_package_data = True,
    description = 'Set quick alerts at timed intervals',
    long_description = 'Do you ever wish that you could effortlessly set repeating alerts on your computer? The "timed-alert" or "tal" command lets you do just that!',
    url = 'https://github.com/omar-ozgur/Timed-Alert',
    author = 'Omar Ozgur',
    author_email = 'oozgur217@gmail.com',
    license = 'MIT',
    keywords = ['timed', 'alert', 'timed-alert', 'timer', 'sound', 'noise', 'repeating', 'intervals', 'command-line', 'python'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
    ],
    python_requires=' >= 2.6',
    install_requires = [
        'Click',
    ],
    entry_points = '''
        [console_scripts]
        tal = timed_alert.main:tal
        timed-alert = timed_alert.main:tal
    ''',
)
