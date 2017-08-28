# Copyright 2017 Adler Medrado
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


import argparse

from correios.client import Correios
from correios.models.user import User, Service


def get_tracking_codes(service, quantity):
    olist_user = User("Your Company's Name", "Your Company's CNPJ")
    client = Correios("Your Correio's username", "Your correio's password")
    tracking_codes = client.request_tracking_codes(olist_user, Service.get(service), quantity=quantity)
    print(tracking_codes)


def main():
    parser = argparse.ArgumentParser(description="Track a package at Correios SRO Web Service")
    parser.add_argument("-u", "--username", required=True)
    parser.add_argument("-p", "--password", required=True)
    parser.add_argument("-n", "--name", required=True)
    parser.add_argument("-c", "--cnpj", required=True)
    parser.add_argument("trackings", nargs="+")
    args = parser.parse_args()

    print(args)

if __name__ == '__main__':
    main()

