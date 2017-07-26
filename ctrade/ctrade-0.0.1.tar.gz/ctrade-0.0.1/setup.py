# setup.py
# Description: Setup for CryptoTrade.
# Created by Matthew Sedam on 7/26/2017.
#
# Copyright 2017 Matthew Sedam.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup

setup(name="ctrade",
      version="0.0.1",
      description="CryptoTrade is a cryptocurrency trading program.",
      url="https://github.com/matthewsedam/cryptotrade",
      author="Matthew Sedam",
      author_email="sedammatthew@gmail.com",
      license="Apache",
      packages=["ctrade"],
      zip_safe=False)
