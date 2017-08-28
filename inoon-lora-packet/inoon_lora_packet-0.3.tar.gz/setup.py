from setuptools import setup


setup_requires = [
]

install_requires = [
]

dependency_links = [
]

setup(
    name='inoon_lora_packet',
    version='0.3',
    description='LoRa packet parser for Ino-on, Inc.',
    author='Joonkyo Kim',
    author_email='jkkim@ino-on.com',
    packages=["inoon_lora_packet"],
    include_package_data=True,
    install_requires=install_requires,
    setup_requires=setup_requires,
    dependency_links=dependency_links,
    # scripts=['manage.py'],
    entry_points={
        'console_scripts': [
        ],
        "egg_info.writers": [
            "foo_bar.txt = setuptools.command.egg_info:write_arg",
        ],
    },
)
