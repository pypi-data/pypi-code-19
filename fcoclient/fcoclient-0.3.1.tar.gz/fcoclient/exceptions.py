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

"""
Exceptions that are raised by fcoclient library during operation.
"""


class ResourceError(Exception):
    """
    Base exception for resource retrieval.
    """

    def __init__(self, conditions, msg):
        """
        Construct ResourceError exception.

        Args:
            conditions (:obj:`dict`): Conditions that were used when querying
                for resource(s).
            msg (:obj:`str`): Message explaining reason for exception.
        """
        super(ResourceError, self).__init__(msg)

        self.conditions = conditions
        """dict: Filter condition used when exception was raised."""


class NoSuchResourceError(ResourceError):
    """
    This exception is raised if requested resource does not exist.
    """

    def __init__(self, conditions):
        """
        Construct NoSuchResourceError exception.

        Args:
            conditions (:obj:`dict`): Conditions that were used when querying
                for resource.
        """
        msg = "No resource matches {}".format(conditions)
        super(NoSuchResourceError, self).__init__(conditions, msg)


class NonUniqueResourceError(ResourceError):
    """
    This exception is raised if resource is not matched uniquely.
    """

    def __init__(self, conditions):
        """
        Construct NonUniqueResourceError exception.

        Args:
            conditions (:obj:`dict`): Conditions that were used when
                retrieving resource.
        """
        msg = "More than one resource matches {}".format(conditions)
        super(NonUniqueResourceError, self).__init__(conditions, msg)


class APICallError(Exception):
    """
    This exception is raised on http client errors.
    """

    def __init__(self, request):
        super(APICallError, self).__init__(request.text)


class InvalidConfigError(Exception):
    """
    This exception is raised on broken config file.
    """
