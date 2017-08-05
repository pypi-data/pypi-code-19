from setuptools import setup, find_packages

setup(
    name = 'Keras_FB',
    version = '0.0.2',
    keywords = ('Facebook', 'Keras','Bot'),
    description = 'Transmit the real-time training data(like accuracy/loss) to your Facebook Messenger account',
    license = 'MIT License',
    install_requires = ['keras','numpy','scipy','matplotlib','fbchat'],
    author = 'Shou Chaofan',
    author_email = 'scf@ieee.org',
    packages = find_packages(),
    platforms = 'any',
)
