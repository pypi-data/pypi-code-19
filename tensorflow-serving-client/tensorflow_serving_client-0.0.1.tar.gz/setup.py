from setuptools import setup
from setuptools.command.install import install


class BuildPackageProtos(install):
    def run(self):
        install.run(self)
        from grpc.tools import command
        command.build_package_protos('')


setup(
    name='tensorflow_serving_client',
    version='0.0.1',
    description='Python client for tensorflow serving',
    author='Triage Technologies Inc.',
    license='MIT',
    packages=[
        'tensorflow_serving_client',
        'tensorflow_serving_client.protos',
    ],
    scripts=[
        'bin/tensorflow_serving_client',
    ],
    setup_requires=[
        'cython',
    ],
    install_requires=[
        'grpcio',
        'grpcio-tools',
        'tensorflow',
        'Pillow',
        'keras',
    ],
    cmdclass={
        'install': BuildPackageProtos,
        'develop': BuildPackageProtos,
    },
)
