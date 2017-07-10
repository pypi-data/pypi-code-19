from setuptools import setup, find_packages

setup(
    name='indico_sixpay',
    version='1.2.2',
    description='Indico EPayment Sub-Plugin to use SixPay services',
    url='https://github.com/maxfischer2781/indico_sixpay',
    author='Max Fischer',
    author_email='maxfischer2781@gmail.com',
    entry_points={'indico.ext': ['EPayment.sixPay = indico_sixpay', ], },
    packages=find_packages(),
    package_data={'indico_sixpay': ['tpls/*.tpl']},
    install_requires=['requests', 'indico>=1.2'],
    license='GPLv3+',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications :: Conferencing',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    zip_safe=False,
    keywords='indico epayment six sixpay plugin',
)
