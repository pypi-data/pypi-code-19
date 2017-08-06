from setuptools import setup, find_packages

setup(
    name='leanote-deployer-git',
    version='0.1.0',
    description="Deploy leanote's blog to git pages",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    author='hehanlin',
    url='https://github.com/hehanlin/leanote_deployer_git',
    author_email='china.hehanlin@gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=False,
    zip_safe=True,
)