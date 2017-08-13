# Copyright (c) 2017 XLAB d.o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from fcoclient import utils
from fcoclient.exceptions import InvalidConfigError


class Config(dict):

    valid_keys = {"url", "username", "customer", "password", "verify"}

    def __init__(self, **data):
        invalid = [k for k in data.keys() if k not in self.valid_keys]
        if len(invalid) != 0:
            err = "Invalid settings key(s) found: {}", ",".join(invalid)
            raise InvalidConfigError(err)

        # TODO: Fix this as soon as possible!!!
        data["verify"] = False
        super(Config, self).__init__(data)

    def save(self, path):
        with open(path, "w") as f:
            utils.output_json(self, f)

    # Construction helper
    @staticmethod
    def load_from_file(path):
        err = None

        try:
            with open(path) as f:
                data = json.load(f)
        except IOError:
            err = "File {} is missing. Try running configure command."
        except ValueError:
            err = "File {} is not valid JSON"

        if err is not None:
            raise InvalidConfigError(err.format(path))

        return Config(**data)
