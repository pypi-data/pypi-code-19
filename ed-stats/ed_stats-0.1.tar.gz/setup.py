from setuptools import setup

setup(
    name='ed_stats',
    version='0.1',
    description='Collection of my augmented pandas classes, implementing ANOVA and machine learning methods',
    url='https://github.com/EdMan1022/ed_stats.git',
    author='EdMan1022',
    author_email='EdMan1022@gmail.com',
    license='MIT',
    packages=['ed_stats'],
    install_requires=['pandas', 'scipy'],
    python_requires='>=3',
    zip_safe=False)
