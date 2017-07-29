from setuptools import setup, find_packages

setup(
    name = 'command-safe',
    version = '0.1',
    packages = find_packages(),
    include_package_data = True,
    description = 'A simple way to save and recall commands with short aliases.',
    long_description = 'Command Safe is a great tool when you find yourself commonly typing the same long commands. Why not save those commands to a short and convenient alias that you can recall at any time!',
    url='https://github.com/omar-ozgur/Command-Safe',
    author = 'Omar Ozgur',
    author_email = 'oozgur217@gmail.com',
    license = 'MIT',
    keywords = ['command', 'line', 'command-line', 'safe', 'save', 'alias'],
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
        csa = command_safe.main:csa
        command-safe = command_safe.main:csa
    ''',
)
