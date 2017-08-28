#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import setuptools

setuptools.setup(
    name="abcplus",
    version="0.1.0",
    author="Greg Hill",
    author_email="jimbobhickville@gmail.com",
    description="An amplified version of abc for Abstract Base Classes plus more",
    url="https://www.github.com/jimbobhickville/abcplus",
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    install_requires=[],
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ],
    scripts=[
    ],
)
