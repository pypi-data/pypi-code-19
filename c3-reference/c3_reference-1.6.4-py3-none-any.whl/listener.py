#!/bin/env python
"""Simulates the traffic of one or more listeners or beacons."""

import argparse
import asyncio
import os
import random
import struct

from binascii import unhexlify

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

# Configuration
DK0_INTERVAL = 7200
DK1_INTERVAL = 86400
PERCENT_DROPPED_PACKETS = 10
AVG_BEACON_DISTANCE = 3  # Meters

parser = argparse.ArgumentParser(
    description='Start a stub listener providing secbeacon packets')
parser.add_argument('--server', '-s', default="127.0.0.1",
                    help="Address to direct reports")
parser.add_argument('--port', '-p', type=int, default=9999,
                    help="UDP Port of auth_server")
parser.add_argument('--verbose', '-v', action='store_true',
                    help="Dump contents of each packet sent")
parser.add_argument('--num-beacons', '-nb', type=int, default=1,
                    help="Number of secure beacons to simulate")
parser.add_argument('--num-ibeacons', '-ib', type=int, default=1,
                    help="Number of non-secure ibeacons to simulate")
parser.add_argument('--num-listeners', '-nl', type=int, default=1,
                    help="Number of unique listeners to simulate")
parser.add_argument('--master-key', '-key', default=('c3' * 16),
                    help="Key from which to derive beacon keys")

args = parser.parse_args()


def hdlc_frame(buf):
    o_buf = bytearray()
    o_buf.append(0x7e)
    for byte in buf:
        if byte == 0x7e or byte == 0x7d:
            o_buf.append(0x7d)
            o_buf.append(byte & ~(1 << 5))
        else:
            o_buf.append(byte)
    o_buf.append(0x7e)
    return o_buf


class IBeacon:
    def __init__(self, uuid: bytes = None, major: int = None,
                 minor: int = None) -> None:
        if not uuid:
            uuid = os.urandom(16)
        self.uuid = uuid

        if not major:
            major = random.randint(0, 2 ** 16-1)
        self.major = major

        if not minor:
            minor = random.randint(0, 2 ** 16-1)
        self.minor = minor

    def generate_report(self) -> bytes:
        count = random.randint(0, 255)
        distance = random.randint(
            0, AVG_BEACON_DISTANCE * 200)
        variance = random.randint(
            1, 20)
        return struct.pack(
            "!16sHHHHH", self.uuid, self.major, self.minor,
            count, distance, variance)


class IBeaconSwarm:
    transport = None  # type: asyncio.DatagramTransport

    def __init__(self, num: int) -> None:
        self.children = []  # type: list[IBeacon]
        for unused in range(num):
            self.children.append(IBeacon())

    async def task(self, transport: asyncio.DatagramTransport) -> None:
        self.transport = transport
        await asyncio.sleep(random.random())
        counter = 0  # type: int
        while True:
            self.send_packet(LISTENERS[counter])
            await asyncio.sleep(5 / len(LISTENERS))
            counter = (counter + 1) % len(LISTENERS)

    def send_packet(self, l_id: bytes) -> None:
        buf = b'\x01'  # Version and Packet Type
        data = b''
        random.shuffle(self.children)
        num_rpts = random.randint(0, len(self.children))
        if num_rpts == 0:
            return
        for rpt in [
                b.generate_report() for b in self.children[:num_rpts]]:
            data += rpt
        rpt_len = len(data) // num_rpts
        buf += struct.pack("B", rpt_len)
        buf += struct.pack("B{}s".format(len(l_id)), len(l_id), l_id)
        buf += data
        self.transport.write(hdlc_frame(buf))


class Beacon:
    transport = None  # type: asyncio.DatagramTransport

    def __init__(self, beacon_id: bytes = None) -> None:
        if beacon_id is None:
            self._id = bytes(
                [random.randint(0, 255) for i in range(6)])
        else:
            self._id = beacon_id
        cmac = CMAC.new(unhexlify(args.master_key), ciphermod=AES)
        cmac.update(self.id)
        self.key = cmac.digest()
        self.clock = random.randint(0, 2**10-1)
        self.dk = random.randint(0, 2**32-1)
        self.iterate()

    @property
    def id(self) -> bytes:
        return self._id

    async def task(self, transport: asyncio.DatagramTransport) -> None:
        self.transport = transport
        await asyncio.sleep(random.random())
        while True:
            # Update beacon state
            self.iterate()
            if random.randint(1, 100) > PERCENT_DROPPED_PACKETS:
                self.send_packet()
            await asyncio.sleep(1)

    def iterate(self) -> None:
        self.clock += 1
        if self.clock % DK0_INTERVAL == 0:
            self.evolve_dk(0)
        if self.clock % DK1_INTERVAL == 0:
            self.evolve_dk(1)
        self.nonce = os.urandom(16)
        self.flags = random.choice([0, 1])

    def dump(self, buf: bytes, l_id: bytes, payload: bytes,
             tag: bytes, distance: float, variance: float) -> None:
        print("""
Packet: {0}
\tListener ID: {1}
\tBeacon ID: {2}
\tNonce: {3}
\tPayload: {4}
\t\tClock: {5}
\t\tDK: {6:08x}
\t\tFlags: {7:02x}
\tTag: {8}
\tDistance: {9}m
\tVariance: {10}""".format(buf.hex(), l_id.hex(), self.id.hex(),
                           self.nonce.hex(), payload.hex(),
                           self.clock, self.dk,
                           self.flags,
                           tag.hex(), (distance / 100.0), (variance / 100.0)))

    def evolve_dk(self, num: int) -> None:
        # Evolve the DK. Same algo as the "beacon", but we know we'll
        # be masking the unknown bits, so shift in zeros
        high, low = self.dk >> 16, self.dk & 0x0000ffff
        if num == 0:
            low = (low << 1) & 0xffff
        if num == 1:
            high = high << 1 & 0xffff
        self.dk = (high << 16) | low & 0xffff

    def send_packet(self) -> None:
        # Generate Enciphered Payload and MAC tag
        msg = struct.pack("<IIB", self.clock, self.dk, self.flags)
        cipher = AES.new(self.key, AES.MODE_EAX, self.nonce,
                         mac_len=4)
        cipher.update(self.id)
        ciphertext, tag = cipher.encrypt_and_digest(msg)
        # Generate Header
        buf = b'\x02'  # Version and Packet Type
        msg_len = len(self.id + self.nonce + ciphertext + tag)
        buf += struct.pack("B", msg_len)
        l_id = random.choice(LISTENERS)
        buf += struct.pack("B{}s".format(len(l_id)), len(l_id), l_id)
        # Append Report
        distance = random.randint(0, AVG_BEACON_DISTANCE * 200)
        variance = random.randint(1, 20)
        buf += struct.pack("<6s 16s 9s 4s H H", self.id, self.nonce,
                           ciphertext, tag, distance, variance)
        if args.verbose:
            self.dump(buf, l_id, ciphertext, tag, distance, variance)
        self.transport.write(hdlc_frame(buf))


class ListenerProtocol:
    transport = None  # type: asyncio.DatagramTransport

    def eof_received(self):
        print('Authserver closed connection.')
        print("Stopping Tasks.")
        for task in asyncio.Task.all_tasks():
            task.cancel()

    def connection_made(self, transport):
        self.transport = transport
        print('Starting beacons')
        loop = asyncio.get_event_loop()
        for beacon in [Beacon() for i in range(args.num_beacons)]:
            loop.create_task(beacon.task(transport))
        ibeacons = IBeaconSwarm(args.num_ibeacons)
        loop.create_task(ibeacons.task(transport))

    def data_received(self, data: bytes):
        pass

    def error_received(self, exc: Exception) -> None:
        print('Error received:', exc)

    def connection_lost(self, exc: Exception) -> None:
        print('closing transport', exc)


LISTENERS = [os.urandom(6) for i in range(args.num_listeners)]


def main():
    random.seed(os.urandom(16))

    loop = asyncio.get_event_loop()
    loop.create_task(loop.create_connection(
        ListenerProtocol, host=args.server, port=args.port))

    try:
        print("Simulating {} beacons; Sending reports to {}:{}".format(
            args.num_beacons, args.server, args.port))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping Tasks.")
        for task in asyncio.Task.all_tasks():
            task.cancel()
        loop.run_until_complete(asyncio.sleep(0.1))


if __name__ == '__main__':
    main()
