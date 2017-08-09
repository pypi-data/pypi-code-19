from setuptools import setup, find_packages

install_requires = [ 'pillow==3.2.0',
                    'numpy==1.11.0',
                    'scipy==0.17.0',
                    'sklearn==0.0',
                    ]
dependency_links = [ ]

setup(
        name='Hjun2',
        version='0.1.0',
        description='hjun machine learning',
        author='Hjun',
        author_email='hjun.jeon@samsung.com',
        #packages=["Hjun2"],
        packages=find_packages(),
        include_package_data=True,
        install_requires=install_requires,
        dependency_links=dependency_links,
        entry_points={
            'console_scripts':['Hjun2=Hjun2.hj:hjun_call'],
            },
    )



