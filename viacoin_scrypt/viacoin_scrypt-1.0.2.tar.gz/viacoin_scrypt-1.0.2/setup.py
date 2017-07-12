from distutils.core import setup, Extension

viacoin_scrypt_module = Extension('viacoin_scrypt',
                               sources = ['viacoin_scrypt/scryptmodule.c',
                                          'viacoin_scrypt/scrypt.c'],
                               include_dirs=['./viacoin_scrypt/'])

setup (
    name = 'viacoin_scrypt',
    version = '1.0.1',
    description = 'Bindings for scrypt proof of work used by Viacoin',
    classifiers=[
        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    ext_modules = [viacoin_scrypt_module]
)
