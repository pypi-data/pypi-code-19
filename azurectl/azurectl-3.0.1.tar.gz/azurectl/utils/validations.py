# Copyright (c) 2016 SUSE.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import dateutil.parser

# project
from azurectl.azurectl_exceptions import AzureInvalidCommand


class Validations(object):
    SAS_PERMISSION_VALUES = 'dlrw'
    PREFERRED_DATE_FORMAT = 'YYYY-MM-DDThh:mm:ssZ'

    @classmethod
    def validate_min_length(self, field_name, value, min_length):
        if len(value) < min_length:
            raise AzureInvalidCommand(
                '%s is too short. Length must be at least %d characters.' %
                (field_name, min_length))
        return True

    @classmethod
    def validate_max_length(self, field_name, value, max_length):
        if len(value) > max_length:
            raise AzureInvalidCommand(
                '%s is too long. Length must be at most %d characters.' %
                (field_name, max_length))
        return True

    @classmethod
    def validate_sas_permissions(self, field_name, value):
        if not all(char in self.SAS_PERMISSION_VALUES for char in value):
            raise AzureInvalidCommand(
                "%s contains invalid chars. Only '%s' are allowed." %
                (field_name, self.SAS_PERMISSION_VALUES)
            )
        return True

    @classmethod
    def validate_date(self, field_name, value):
        try:
            date = dateutil.parser.parse(value)
        except ValueError:
            raise AzureInvalidCommand(
                '%s is not a valid date. The format should be %s' %
                (field_name, self.PREFERRED_DATE_FORMAT)
            )
        return date

    @classmethod
    def validate_at_least_one_argument_is_set(self, command_args, keys=None):
        if keys is None:
            keys = []
        values = [command_args[key] for key in keys]
        if any(values):
            return True
        else:
            raise AzureInvalidCommand(
                'One of the following arguments must be supplied: %s' %
                ', '.join(keys)
            )
