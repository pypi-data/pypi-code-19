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
# -*- coding: utf-8 -*-
#!/usr/bin/env python


import evdev
import utils

rfidcodes = {2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8', 10: u'9', 11: u'0'}


def init_divice(device, debug=False):
    try:
        device = evdev.InputDevice('/dev/input/event' + str(device))
        utils.debug_print('Device file found', debug)
        return device
    except:
        utils.debug_print('No Device file found', debug)
        return None


def read_rfid_reader(device_id, debug=False):
    print('Read RFID form USB Card Reader')
    rfid_code = ''    
    card_reader_device = init_divice(device_id, debug)
    if card_reader_device is not None:
        card_reader_device.grab()
        for event in card_reader_device.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                # Nur beim Key_Down
                if event.value == 1:
                    if event.code == 28:
                        break
                    else:
                        rfid_code += rfidcodes[event.code]
        card_reader_device.ungrab()
    return rfid_code


def list_devices(debug=False):
    """
    List all connectet devices and wirte the importen information in a list
    :param debug: if True print debug msg
    :return: return a list of all usb devices
    """
    device_list = list()
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    if len(devices) == 0:
        utils.debug_print('No Devices found', debug)
        return list()
    for device in devices:
        utils.debug_print(str(device.fn) + ' ' + device.name + ' ' + str(device.phys), debug)
        device_list.append(
            {
                'fn': device.fn,
                'name': device.name,
                'phys': device.phys
            }
        )
    return device_list


def read(device_id, debug=False):
    """Read from the card Reader

    :param debug: if True print debug msg
    :return:  return the reading UUID
    """
    rfid_code = read_rfid_reader(device_id, debug)
    rfid_uuid = utils.rfid_code_to_uuid(rfid_code, debug)
    utils.debug_print('RFID as UUID: ' + rfid_uuid, debug)
    return rfid_uuid
