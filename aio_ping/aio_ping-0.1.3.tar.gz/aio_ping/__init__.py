#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

"""
    A pure python ping implementation using raw sockets.

    Compatibility:
        OS: Linux, Windows, MacOSX
        Python: 2.6 - 3.5

    Note that due to the usage of RAW sockets root/Administrator
    privileges are requied.

    Derived from ping.c distributed in Linux's netkit. That code is
    copyright (c) 1989 by The Regents of the University of California.
    That code is in turn derived from code written by Mike Muuss of the
    US Army Ballistic Research Laboratory in December, 1983 and
    placed in the public domain. They have my thanks.

    Copyright (c) Matthew Dixon Cowles, <http://www.visi.com/~mdc/>.
    Distributable under the terms of the GNU General Public License
    version 2. Provided with no warranties of any sort.

    website: https://github.com/l4m3rx/python-ping

"""

# TODO Remove any calls to time.sleep
# This would enable extension into larger framework that aren't multi threaded.
import os
import sys
import time
import array
import fcntl
import socket
import struct
import select
import signal
import asyncio
import traceback

if __name__ == '__main__':
    import argparse

class NoAddressFound(RuntimeError):
    pass
class ICMPError(RuntimeError):
    pass

try:
    from _thread import get_ident
except ImportError:
    def get_ident():
        return 0

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time

# ICMP parameters

ICMP_ECHOREPLY = 0  # Echo reply (per RFC792)
ICMP_ECHO = 8  # Echo request (per RFC792)
ICMP_ECHO_IPV6 = 128  # Echo request (per RFC4443)
ICMP_ECHO_IPV6_REPLY = 129  # Echo request (per RFC4443)
ICMP_MAX_RECV = 2048  # Max size of incoming buffer

MAX_SLEEP = 1000


class MStats2(object):

    def __init__(self):
        self._this_ip = '0.0.0.0'
        self.reset()

    def reset(self):
        self._timing_list = []
        self._packets_sent = 0
        self._packets_rcvd = 0

        self._reset_statistics()

    @property
    def thisIP(self):
        return self._this_ip

    @thisIP.setter
    def thisIP(self, value):
        self._this_ip = value

    @property
    def pktsSent(self):
        return self._packets_sent

    @property
    def pktsRcvd(self):
        return self._packets_rcvd

    @property
    def pktsLost(self):
        return self._packets_sent - self._packets_rcvd

    @property
    def minTime(self):
        return min(self._timing_list) if self._timing_list else None

    @property
    def maxTime(self):
        return max(self._timing_list) if self._timing_list else None

    @property
    def totTime(self):
        if self._total_time is None:
            self._total_time = sum(self._timing_list)
        return self._total_time

    def _get_mean_time(self):
        if self._mean_time is None:
            if len(self._timing_list) > 0:
                self._mean_time = self.totTime / len(self._timing_list)
        return self._mean_time
    mean_time = property(_get_mean_time)
    avrgTime = property(_get_mean_time)

    @property
    def median_time(self):
        if self._median_time is None:
            self._median_time = self._calc_median_time()
        return self._median_time

    @property
    def pstdev_time(self):
        """Returns the 'Population Standard Deviation' of the set."""
        if self._pstdev_time is None:
            self._pstdev_time = self._calc_pstdev_time()
        return self._pstdev_time

    @property
    def fracLoss(self):
        if self._frac_loss is None:
            if self.pktsSent > 0:
                self._frac_loss = self.pktsLost / self.pktsSent
        return self._frac_loss

    def packet_sent(self, n=1):
        self._packets_sent += n

    def packet_received(self, n=1):
        self._packets_rcvd += n

    def record_time(self, value):
        self._timing_list.append(value)
        self._reset_statistics()

    def _reset_statistics(self):
        self._total_time = None
        self._mean_time = None
        self._median_time = None
        self._pstdev_time = None
        self._frac_loss = None

    def _calc_median_time(self):
        n = len(self._timing_list)
        if n == 0:
            return None
        if n & 1 == 1:  # Odd number of samples? Return the middle.
            return sorted(self._timing_list)[n // 2]
        # Even number of samples? Return the mean of the two middle samples.
        else:
            halfn = n // 2
            return sum(sorted(self._timing_list)[halfn - 1:halfn + 1]) / 2

    def _calc_sum_square_time(self):
        mean = self.mean_time
        return sum(((t - mean)**2 for t in self._timing_list))

    def _calc_pstdev_time(self):
        pvar = self._calc_sum_square_time() / len(self._timing_list)
        return pvar**0.5


def _checksum(source_string):
    """
    A port of the functionality of in_cksum() from ping.c
    Ideally this would act on the string as a series of 16-bit ints (host
    packed), but this works.
    Network data is big-endian, hosts are typically little-endian
    """
    if (len(source_string) % 2):
        source_string += "\x00"
    converted = array.array("H", source_string)
    if sys.byteorder == "big":
        converted.bytewap()
    val = sum(converted)

    val &= 0xffffffff  # Truncate val to 32 bits (a variance from ping.c, which
    # uses signed ints, but overflow is unlikely in ping)

    val = (val >> 16) + (val & 0xffff)  # Add high 16 bits to low 16 bits
    val += (val >> 16)  # Add carry from above (if any)
    answer = ~val & 0xffff  # Invert and truncate to 16 bits
    answer = socket.htons(answer)

    return answer

_next_id = 1

class Ping(object):
    def __init__(self, destIP=None, hostname=None, interval=1, numDataBytes=64,
            stats=None, ipv6=False, verbose=True, sourceIP=None,
            sourceIntf=None, loop=None, count=3, timeout=5):
        self.destIP = destIP
        self.hostname = hostname
        self.interval = interval
        self.count = count
        self.timeout = timeout
        self.numDataBytes = numDataBytes
        self.stats = stats
        self.ipv6 = ipv6
        self.verbose = verbose
        self.sourceIP = sourceIP
        self.sourceIntf = sourceIntf

        if loop is None:
            loop = asyncio.get_event_loop()
        self.loop = loop

        self.socket = None

    def close(self):
        if self.socket is not None:
            self.loop.remove_reader(self.socket.fileno())
            self.socket.close()
            self.socket = None

    async def init(self, hostname=None):
        if hostname is None:
            hostname = self.hostname
        else:
            self.destIP = None

        self.close()

        self.seqNumber = 0
        self.startTime = default_timer()
        self.queue = asyncio.Queue(loop=self.loop)

        global _next_id
        self.ID = _next_id
        _next_id += 1

        if self.destIP is None:
            if hostname is None:
                raise RuntimeError("You need to set either hostname or destIP")
            for info in (await self.loop.getaddrinfo(hostname, None)):
                if info[0] == socket.AF_INET6:
                    if self.ipv6 is False:
                        continue
                    self.ipv6 = True
                elif info[0] == socket.AF_INET:
                    if self.ipv6 is True:
                        continue
                    self.ipv6 = False
                else:
                    continue
                self.destIP = info[4][0]
                break
            else:
                raise NoAddressFound(hostname)

        if self.ipv6:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_RAW,
                socket.getprotobyname("ipv6-icmp"))
            self.socket.setsockopt(socket.IPPROTO_IPV6,
                socket.IPV6_RECVHOPLIMIT, 1)
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                socket.getprotobyname("icmp"))

        if self.sourceIP is not None:
            self.socket.bind((self.sourceIP, 0))

        if self.sourceIntf is not None:
            try:
                SO_BINDTODEVICE = socket.SO_BINDTODEVICE
            except AttributeError:
                SO_BINDTODEVICE = 25
            self.socket.setsockopt(socket.SOL_SOCKET, SO_BINDTODEVICE,
                (self.sourceIntf + '\0').encode('utf-8'))

        # Don't block on the socket
        flag = fcntl.fcntl(self.socket.fileno(), fcntl.F_GETFL)
        fcntl.fcntl(self.socket.fileno(), fcntl.F_SETFL, (flag | os.O_NONBLOCK))

        self.loop.add_reader(self.socket.fileno(), self._receive)

    async def single(self, timeout=None):
        """
        Fire off a single ping.
        Returns the answer's delay (in ms).
        """
        self._send()

        recv = self.queue.get()
        if timeout is None or timeout > self.timeout:
            timeout = self.interval
        if timeout is None or timeout > self.delay:
            timeout = self.interval

        if timeout is not None:
            recv = asyncio.wait_for(recv, timeout, loop=self.loop)

        recv = await recv
        if isinstance(recv,Exception):
            raise recv
        recvTime, dataSize, iphSrcIP, icmpSeqNumber, iphTTL = recv

        delay = recvTime - self.startTime - icmpSeqNumber * self.interval
        await self.pinged(recvTime=recvTime, delay=delay,
            host=self.resolve_host(iphSrcIP), seqNum=icmpSeqNumber,
            ttl=iphTTL, size=dataSize)

        if self.interval > 0:
            delay = self.seqNumber * self.interval - (recvTime - self.startTime)
        else:
            delay = None
        return delay, (recvTime, dataSize, iphSrcIP, icmpSeqNumber, iphTTL)

    async def pinged(self, recvTime,delay,host,seqNum,ttl,size):
        """Hook to catch a successful ping"""
        pass

    async def looped(self):
        """
        Send .count ping to .destIP with the given delay and timeout.

        To continuously attempt ping requests, set .count to zero.
        """

        assert self.interval > 0

        while not self.count or self.stats.pktsRcvd < self.count:
            now = default_timer()
            delay1 = self.seqNumber * self.interval - (now - self.startTime)
            while (not self.count or self.seqNumber < self.count) and delay1 <= 0:
                self._send()
                delay1 += self.interval
            if self.count and self.seqNumber >= self.count:
                delay1 = None
            if self.timeout is not None:
                delay2 = self.startTime+self.timeout - now
                if delay2 < 0:
                    break
                if delay1 is None or delay1 > delay2:
                    delay1 = delay2
            try:
                recv = self.queue.get()
                if delay1 is not None:
                    recv = asyncio.wait_for(recv, delay1,
                        loop=self.loop)
                recv = await recv
                if isinstance(recv,Exception): # error
                    if isinstance(recv,ICMPError):
                        print("ICMP Error: %s/%s" % recv.args)
                        continue
                    else:
                        raise
                recvTime, dataSize, iphSrcIP, icmpSeqNumber, iphTTL = recv
                delay = recvTime - self.startTime - icmpSeqNumber * self.interval
                await self.pinged(recvTime=recvTime, delay=delay,
                    host=self.resolve_host(iphSrcIP), seqNum=icmpSeqNumber,
                    ttl=iphTTL, size=dataSize)

            except asyncio.TimeoutError:
                pass

        return self.stats.pktsRcvd

    def resolve_host(self, iphSrcIP):
        return iphSrcIP


    def _send(self):
        """
        Send one ping to the given >destIP<.
        """

        # Header is type (8), code (8), checksum (16), id (16), sequence (16)
        # (numDataBytes - 8) - Remove header size from packet size
        myChecksum = 0

        # Make a dummy heder with a 0 checksum.
        if self.ipv6:
            header = struct.pack(
                "!BbHHh", ICMP_ECHO_IPV6, 0, myChecksum, self.ID, self.seqNumber
            )
        else:
            header = struct.pack(
                "!BBHHH", ICMP_ECHO, 0, myChecksum, self.ID, self.seqNumber
            )

        padBytes = []
        startVal = 0x42
        # because of the string/byte changes in python 2/3 we have
        # to build the data differnely for different version
        # or it will make packets with unexpected size.
        if sys.version[:1] == '2':
            _bytes = struct.calcsize("d")
            data = ((numDataBytes - 8) - _bytes) * "Q"
            data = struct.pack("d", default_timer()) + data
        else:
            for i in range(startVal, startVal + (self.numDataBytes - 8)):
                padBytes += [(i & 0xff)]  # Keep chars in the 0-255 range
            # data = bytes(padBytes)
            data = bytearray(padBytes)

        # Calculate the checksum on the data and the dummy header.
        myChecksum = _checksum(header + data)  # Checksum is in network order

        # Now that we have the right checksum, we put that in. It's just easier
        # to make up a new header than to stuff it into the dummy.
        if self.ipv6:
            header = struct.pack(
                "!BbHHh", ICMP_ECHO_IPV6, 0, myChecksum, self.ID, self.seqNumber
            )
        else:
            header = struct.pack(
                "!BBHHH", ICMP_ECHO, 0, myChecksum, self.ID, self.seqNumber
            )

        packet = header + data

        self.socket.sendto(packet, (self.destIP, 0))  # Port number is irrelevant
        if self.stats is not None:
            self.stats.packet_sent()
        self.seqNumber += 1


    def _receive(self):
        """
        Receive the ping from the socket. Timeout = in ms
        """

        try:
            timeReceived = default_timer()

            iphSrcIP = 0
            iphDestIP = 0
            if self.ipv6:
                recPacket, ancdata, flags, addr = self.socket.recvmsg(ICMP_MAX_RECV)
                iphSrcIP = addr[0]
                iphTTL = 0
                if len(ancdata) == 1:
                    cmsg_level, cmsg_type, cmsg_data = ancdata[0]
                    a = array.array("i")
                    a.frombytes(cmsg_data)
                    iphTTL = a[0]
            else:
                recPacket, addr = self.socket.recvfrom(ICMP_MAX_RECV)
                ipHeader = recPacket[:20]
                iphVersion, iphTypeOfSvc, iphLength, iphID, iphFlags, iphTTL, \
                    iphProtocol, iphChecksum, iphSrcIP, iphDestIP = struct.unpack(
                        "!BBHHHBBHII", ipHeader)
                iphSrcIP = socket.inet_ntop(socket.AF_INET,
                    struct.pack("!I", iphSrcIP))


            if self.ipv6:
                icmpHeader = recPacket[0:8]
            else:
                icmpHeader = recPacket[20:28]

            icmpType, icmpCode, icmpChecksum, icmpPacketID, icmpSeqNumber \
                = struct.unpack("!BBHHH", icmpHeader)

            # We shouldn't see our own packets, but ...
            if icmpType not in (ICMP_ECHO, ICMP_ECHO_IPV6):

                # "Real" reply?
                if icmpType in (ICMP_ECHOREPLY, ICMP_ECHO_IPV6_REPLY) and \
                        icmpPacketID == self.ID:
                    dataSize = len(recPacket) - 28
                    if self.stats is not None:
                        self.stats.packet_received()
                        delay = timeReceived - self.startTime - icmpSeqNumber * self.interval
                        self.stats.record_time(delay)
                    self.queue.put_nowait((timeReceived, (dataSize + 8), iphSrcIP, \
                        icmpSeqNumber, iphTTL))
                else:
                    # TODO improve error reporting. XXX: need to re-use the
                    # socket, otherwise we won't get host-unreachable errors.
                    self.queue.put_nowait(ICMPError(icmpType,icmpCode))

        except BaseException as exc:
            self.loop.stop()
            raise

    def print_stats(self):
        """
        Show stats when pings are done
        """
        myStats = self.stats
        if myStats is None:
            return

        print("\n----%s PYTHON PING Statistics----" % (myStats.thisIP))

        print("%d packets transmitted, %d packets received, %0.1f%% packet loss"
            % (myStats.pktsSent, myStats.pktsRcvd, 100.0 * myStats.fracLoss))

        if myStats.pktsRcvd > 0:
            print("round-trip (ms)  min/avg/max = %0.1f/%0.1f/%0.1f" % (
                myStats.minTime*1000, myStats.avrgTime*1000, myStats.maxTime*1000
            ))
            print('                 median/pstddev = %0.2f/%0.2f' % (
                myStats.median_time*1000, myStats.pstdev_time*1000
            ))

        print('')
        return

    def _signal_handler(self, signum, frame):
        """ Handle exit via signals """
        self.print_stats()
        print("(Terminated with signal %d)" % signum)
        sys.exit(0)

    def add_signal_handler(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        if hasattr(signal, "SIGBREAK"):  # Handle Ctrl-Break /Windows/
            signal.signal(signal.SIGBREAK, self._signal_handler)


class Verbose(object):
    """A mix-in class to print a message when each ping os received"""
    async def pinged(self, **kw):
        await super().pinged(**kw)
        print("%d bytes from %s: icmp_seq=%d ttl=%d time=%.2f ms" % (
            kw['size'], kw['host'], kw['seqNum'], kw['ttl'], kw['delay']*1000))

class VerbosePing(Verbose,Ping):
    pass

"""Shortcut methods, not async"""

def single_ping(timeout=3, **av):
    ping = Ping(**av)
    ping.loop.run_until_complete(ping.init())
    res = ping.loop.run_until_complete(asyncio.wait_for(timeout, ping.single(), ping.loop))
    ping.close()
    return res

def _pathfind_ping(destIP, hostname, timeout, mySeqNumber, numDataBytes,
                   **kw):
    single_ping(destIP, hostname, timeout, mySeqNumber, numDataBytes,
                verbose=False, **kw)
    time.sleep(0.5)


def ping(hostname, verbose=True, stats=False, handle_signals=None, count=3, **kw):
    """
    Send @count ping to @destIP with the given @timeout, and display
    the result.

    To continuously attempt ping requests, set @count to zero.

    Installs a signal handler if @count is zero.
    Override this by setting @handle_signals.

    Returns the ping statistics object if @stats is true. Otherwise,
    the result is True if there was at least one valid echo.
    """
    if 'stats' not in kw:
        kw['stats'] = MStats2()
    ping = (VerbosePing if verbose else Ping)(verbose=verbose, count=count, **kw)
    if handle_signals is None:
        handle_signals = (not count)
    if handle_signals:
        ping.add_signal_handler()
    try:
        ping.loop.run_until_complete(ping.init(hostname))
    except socket.gaierror as e:
        print("%s: %s" % (hostname,str(e)))
        return
    except Exception as e:
        traceback.print_exc()
        return
    res = ping.loop.run_until_complete(ping.looped())
    if verbose:
        ping.print_stats()
    ping.close()

    if stats:
        return stats
    return res

