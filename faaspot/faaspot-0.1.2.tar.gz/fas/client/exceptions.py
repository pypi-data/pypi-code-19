########
# Copyright (c) 2017 Faaspot Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.


class FaaspotException(Exception):

    def __init__(self, message, reason=None, server_traceback=None,
                 status_code=-1, error_code=None):
        super(FaaspotException, self).__init__(message)
        self.status_code = status_code
        self.reason = reason
        self.error_code = error_code
        self.server_traceback = server_traceback

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.status_code != -1:
            reason = ' ({0})'.format(self.reason) if self.reason else ''
            return '{0}{1}: {2}'.format(self.status_code, reason, self.message)
        return self.message


class FaaspotClientError(FaaspotException):
    pass


class IllegalExecutionParametersError(FaaspotClientError):
    """
    Raised when an attempt to execute a workflow with wrong/missing parameters
    has been made.
    """
    ERROR_CODE = 'illegal_execution_parameters_error'
