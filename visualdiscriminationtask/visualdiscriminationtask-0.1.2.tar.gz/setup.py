from setuptools import setup

setup(
    name='visualdiscriminationtask',
    description='A Visual Discrimination Task Whisker client',
    version='0.1.2',
    licence="MIT",
    keywords="Whisker Visual Discrimination",
    install_requires=[
        'whisker',
        'twisted'
    ],
    author="Tom Piercy",
    author_email="tap32@medschl.cam.ac.uk",
    packages=['visualdiscrimination'],
    python_requires='>=3',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'visualdiscrimination = visualdiscrimination.whisker_visualdiscrimination.py:main'
        ],
    }
)