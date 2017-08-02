from setuptools import setup

setup(
    name='phi-reducer',    # This is the name of your PyPI-package.
    version='0.4.2',  # Update the version number for new releases
    packages=['phireducer'],
    #include_package_data=True,
    package_data={'phireducer': ['whitelist.pkl'],
    },
    entry_points={
        'console_scripts': [
            'phi-reducer = phireducer.phi_reducer:main',
            'phi-annotation = phireducer.annotation:main',
            'phi-eval = phireducer.eval:main']
            },
        # The name of your scipt, and also the command you'll be using for calling it
    zip_safe = False,
    install_requires=[
          'nltk',
          'spacy'
      ],
    author='UCSF-ICHS',
    author_email='beaunorgeot@gmail.com'
)
