# Copyright (c) 2016 MXCHIP Limited, All Rights Reserved
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
# either express or implied.
import subprocess
import sys
import os

# if windows
if sys.platform == 'win32':
    # if not register
    if subprocess.Popen('reg query "HKEY_CLASSES_ROOT\directory\shell\mico_cube" /s', stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait() == 1:
        os.system('mico-cube.reg')
