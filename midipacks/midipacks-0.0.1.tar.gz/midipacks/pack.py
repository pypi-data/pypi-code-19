import json

from mido import Message, open_ioport


def encode_message(obj):
  serialized = json.dumps(obj)
  return Message('sysex', data=serialized.encode('utf-8'))


def get_port():
  return open_ioport(name='MIDIPACK-IO', virtual=True)
