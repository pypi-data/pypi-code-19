# Copyright 2017 Alex Hadi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import click
import os
import pyshark
import re


@click.command()
@click.option("-f", "-pcap", required=True, type=str, help="PCAP File that is used throughout the checker.")
@click.option("-o", "-output", type=str, help="Specify path for txt file.")
@click.option("-l", "-layers", default=None, type=str, multiple=True, help="Record packets containing certain layers.")
@click.option("-p", "-ports", default=None, type=int, multiple=True, help="Record packets with only certain ports.")
@click.option("-t", "-tls", default=None, is_flag=True, help="Print only packets that have TLS (or SSL) encryption.")
@click.option("-v", "-verbose", default=False, is_flag=True, help="Print to screen. Otherwise, print to file.")
def cli(pcap, layers, ports, output, tls, verbose):
    """
    Author: Alex Hadi\n
    Created using Python 2.7.13 and Click.\n
    Python-based PCAP parser.
    Checks ports, layers, and TLS (or SSL) version of packets.
    """

    # Must be PCAP file extension.
    if not (os.path.exists(pcap) and pcap.endswith(".pcap")):
        click.echo("An invalid pcap path was entered!")
        quit()

    # output_path set
    if output is None:
        output_path = os.getcwd() + "\\pcap_report.txt"
    else:
        if not output.endswith(".txt"):
            output_path = None
            click.echo("The output path must end in .txt!")
            quit()
        else:
            output_path = output

    # save_file set and existing path checked
    if verbose:
        save_file = None
    else:
        check_existing_file(output_path)
        try:
            save_file = open(output_path, "a")
        except IOError:
            save_file = None
            click.echo("The save file could not be opened!")
            quit()

    CheckPCAP(layers, pcap, ports, save_file, output_path, tls, verbose)

    if not verbose:
        save_file.close()


def check_existing_file(output_path):
    """
    Checks to see if existing file needs to be deleted.
    :param output_path: Path to check to see if file already exists.
    :return: Return to same function if user provides invalid input.
    """

    if os.path.isfile(output_path):
        # Make input case insensitive.
        delete_file = raw_input("Would you like to delete the existing file? (Y/N)\n").upper()
        if delete_file == "Y":
            try:
                os.remove(output_path)
            except OSError:
                click.echo("The existing file could not be deleted!")
                quit()
        elif delete_file == "N":
            click.echo("The program cannot save the output!")
            quit()
        else:
            # For invalid input.
            check_existing_file(output_path)


class CheckPCAP:
    def __init__(self, layers, pcap, ports, save_file, output_path, tls, verbose_output):
        """
        Initializes class CheckPCAP.
        :param layers: Layers user specified.
        :param pcap: PCAP file.
        :param ports: Ports user specified.
        :param save_file: File to save output to.
        :param output_path: Path to output file.
        :param tls: If true, display packets that contain SSL layer.
        :param verbose_output: True (output to screen) or false (save to file).
        """

        # Variables
        self.layers = layers
        self.pcap = pcap
        self.ports = ports
        self.save_file = save_file
        self.output_path = output_path
        self.tls = tls
        self.verbose_output = verbose_output

        # Methods
        self.iterate_over_packets()

    def iterate_over_packets(self):
        """
        Iterate over each packet in the PCAP file.
        """

        pcap = pyshark.FileCapture(self.pcap)
        for packet in pcap:
            # Number and layers set.
            number = packet.number
            packet_layers = packet.layers

            # Source and destination ports set (either TCP or UDP)
            if "tcp" in packet:
                src_port = int(packet.tcp.srcport)
                dst_port = int(packet.tcp.dstport)
            elif "udp" in packet:
                src_port = int(packet.udp.srcport)
                dst_port = int(packet.udp.dstport)
            else:
                src_port = None
                dst_port = None

            # TLS (or SSL) Encryption option
            if "ssl" in packet and self.tls:
                # Regex to find TLS (or SSL) version.
                ssl_version = re.findall(r'Version:\s(.*)', str(packet.ssl))

                # If TLS (or SSL) version is not specified in packet.
                if not ssl_version:
                    ssl_version = "TLS Version N/A"
                else:
                    ssl_version = str(ssl_version[0]).strip(r"\r")

                self.record_packet(number, src_port, dst_port, packet_layers, ssl_version=ssl_version)
                continue

            # Ports option
            if self.ports:
                for p in self.ports:
                    # Either src or dst port is matched.
                    if p == (src_port or dst_port):
                        self.record_packet(number, src_port, dst_port, packet_layers)
                        continue

            # Layers option
            if self.layers:
                for s in self.layers:
                    try:
                        # Try to access attribute to see if layer exists.
                        getattr(packet, str(s))
                        self.record_packet(number, src_port, dst_port, packet_layers)
                        break
                    except AttributeError:
                        pass
                continue

    def record_packet(self, number, src_port, dst_port, packet_layers, ssl_version=None):
        """
        Result is recorded to the screen or written to a file.
        :param number: Packet number
        :param src_port: Source port (int)
        :param dst_port: Destination port (int)
        :param packet_layers: List of layers specified by user.
        :param ssl_version: TLS (or SSL) version (optional param)
        """

        # Same string except "\n" added for save_file.write(). ssl_version is dependent on -t flag.
        if self.verbose_output:
            click.echo("Packet {0} : {1} --> {2} : Layers: {3} {ssl}"
                       .format(number, src_port, dst_port, packet_layers,
                               ssl=": " + ssl_version if ssl_version is not None else ""))
        else:
            self.save_file.write("Packet {0} : {1} --> {2} : Layers: {3} {ssl}\n"
                                 .format(number, src_port, dst_port, packet_layers,
                                         ssl=": " + ssl_version if ssl_version is not None else ""))
