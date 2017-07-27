import smbus
import subprocess
import sys
import os

_bus_id = 1
_device_addr = 0x18
_chip_enable_reg = 0x00
_i2c_bus = None

CFG_FILE_PATH = os.path.dirname(os.path.realpath(__file__)) + "/setup.cfg"

def _set_write_to_speaker_enabled(address, enable):
    
    global _i2c_bus

    if enable:
        print("Enabling write to pi-topSPEAKER (" + str(address) + ")")
    else:
        print("Disabling write to pi-topSPEAKER (" + str(address) + ")")

    try:
        _i2c_bus = smbus.SMBus(_bus_id)
        value = 0x01 if enable else 0x00
        _i2c_bus.write_byte_data(address, _chip_enable_reg, value)
    except:
        print("Failed to write to pi-topSPEAKER")
        return False
    
    return True


def _parse_playback_mode_file(mode):

    print("Writing config data to pi-topSPEAKER")

    try:
        index = 0
        with open(CFG_FILE_PATH) as file_data:
            for line in file_data:
                if (line[0] == "W") or (line[0].lower() == mode):
                    array = line.split()
                    if len(array) < 4:
                        print("Error parsing line " + str(index) + " - exiting...")
                        sys.exit(0)
                    else:
                        # Write all values from 4th to the end of the line

                        if len(array) > 3:
                            values = [int(i,16) for i in array[3:]]
                            _i2c_bus.write_i2c_block_data(_device_addr, int(array[2],16), values)
                        else:
                            _i2c_bus.write_byte_data(_device_addr, int(array[2],16), int(array[3],16))
                index = index + 1

        return True

    except:
        print("Failed to write configuration data to pi-topSPEAKER")
        return False

def set_audio_output_hdmi():
    
    print("Setting audio output to HDMI...")

    try:
        interface = None

        mixer_output = subprocess.check_output(['amixer', 'cget', 'numid=3']).splitlines()

        for line in mixer_output:
            if ': values=' in line:
                prefix, interface = line.split('=')
                break

        if interface != '2' and interface != None:
            print("Audio not configured to HDMI - updating...")
            with open(os.devnull, 'w') as FNULL:
                subprocess.call(['amixer', 'cset', 'numid=3', '2'], stdout=FNULL)
            subprocess.call(['sudo', '/etc/init.d/alsa-utils', 'restart'])

        print("OK")
        return True

    except:
        print("There was an error setting audio output to HDMI!")
        return False

def enable(mode):

    print("Initialising speaker (mode " + mode + ")")

    if not os.path.exists(CFG_FILE_PATH):
        print("Error: playback configuration file does not exist")
        return None

    if mode is "l" or str(mode) == "71":
        mode="l"
        address = 0x71
    elif mode is "r" or str(mode) == "72":
        mode="r"
        address = 0x72
    elif mode is "m" or str(mode) == "73":
        mode="m"
        address = 0x73
    else:
        print("Mode not recognised")
        return False

    if _set_write_to_speaker_enabled(address, True) == False:
        print("Error enabling write to pi-topSPEAKER")
        return False

    if _parse_playback_mode_file(mode) == False:
        print("Error parsing and writing mode file to pi-topSPEAKER")
        return False

    if _set_write_to_speaker_enabled(address, False) == False:
        print("Error disabling write to pi-topSPEAKER")
        return False

    return True