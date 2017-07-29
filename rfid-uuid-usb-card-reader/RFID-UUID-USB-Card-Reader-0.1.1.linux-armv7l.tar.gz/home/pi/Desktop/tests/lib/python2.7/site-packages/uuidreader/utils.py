# -*- coding: utf-8 -*-
#!/usr/bin/env python

################################################################################
# Copyright (c) 2017 Peter Steensen. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
# 
#   2. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in
#      the documentation and/or other materials provided with the
#      distribution.
# 
#   3. Neither the name of author nor the names of its contributors may
#      be used to endorse or promote products derived from this software
#      without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
################################################################################

import uuid
import datetime


def debug_print(msg, debug=False):
    if debug:
        timestamp = '<%Y-%m-%d %H:%M:%S>'.format(datetime.datetime.now())
        print(timestamp + ' ' + msg)


def rfid_code_to_uuid(rfid_code, debug=False):
    '''
    Convert the RFID Code to a UUID in the format
    6ba7b810-9dad-11d1-80b4-00c04fd430c8

    :param rfid_code:
    :param debug:
    :return:
    '''

    debug_print('Convert RFID Code to UUID', debug)
    rfid_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(rfid_code)))
    debug_print(str(rfid_code) + ' -> ' + rfid_uuid, debug)
    return rfid_uuid

