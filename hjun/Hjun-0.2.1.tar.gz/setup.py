from setuptools import setup, find_packages

setup_requires=[ ]
install_requires = [ 'pillow==3.2.0',
                    'numpy==1.11.0',
                    'scipy==0.17.0',
                    'sklearn==0.0',
                    ]
dependency_links = [ ]

setup(
        name='Hjun',
        version='0.2.1',
        description='hjun machine learning',
        author='HJUN',
        author_email='hjun.jeon@samsung.com',
        #packages=["HJUN"],
        packages=find_packages(),
        include_package_data=True,
        install_requires=install_requires,
        setup_requires=setup_requires,
        dependency_links=dependency_links,
        entry_points={
            #'console_scripts':['HJUN=HJUN.hj:hjun_call'],
#            "egg_infro.writers":[
#                "foo_bar.txt = setuptools.command.egg_info:write_arg",
#                ],
            },
    )



