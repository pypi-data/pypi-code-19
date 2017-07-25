
from setuptools import setup, find_packages

setup(
        name='simulatesv',
        version='0.1.0',
        description='Simulate structural variations and SNPs with artificial dna sequences',
        long_description='Simulate SNPs and Structural Variations on artificially generated dna sequences',
        url='https://github.com/mlliou112/simulatesv',
        author='Michael Liou',
        author_email='mliou112@yahoo.com',
        license='MIT',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: Scientific/Engineering :: Bio-Informatics'
            ],
        keywords='bioinformatics structural-variation simulate dna genetics, sequencing',
        packages=find_packages(),
        install_requires=['numpy'])

        
        
