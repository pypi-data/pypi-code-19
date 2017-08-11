from setuptools import setup

setup(
    name='robosignatory',
    version='0.4.0',
    description='fedmsg consumer that automatically signs artifacts',
    author='Patrick Uiterwijk',
    author_email='puiterwijk@redhat.com',
    url='https://pagure.io/robosignatory/',
    license='gplv2+',
    install_requires=[
        "fedmsg",
    ],
    packages=[
        'robosignatory',
    ],
    entry_points="""
    [moksha.consumer]
    tagsignerconsumer = robosignatory.tagconsumer:TagSignerConsumer
    atomicsignerconsumer = robosignatory.atomicconsumer:AtomicSignerConsumer

    [console_scripts]
    robosignatory-signbuild = robosignatory.cli:buildsigner
    robosignatory-signtagbuild = robosignatory.cli:tagsigner
    robosignatory-signatomic = robosignatory.cli:atomicsigner
    robosignatory-signmodule = robosignatory.cli:modulesigner

    [robosignatory.signing.helpers]
    echo = robosignatory.utils:EchoHelper
    sigul = robosignatory.utils:SigulHelper
    """,
)
