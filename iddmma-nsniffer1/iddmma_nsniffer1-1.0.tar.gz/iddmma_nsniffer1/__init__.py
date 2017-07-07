#!/usr/bin/env python3
import socket
import struct
#import Textwarp
from textwrap import wrap
print('\t\t@@@@@@@@@@@@@@@@@@@IDDMMA_NSNIFFER v1.0@@@@@@@@@@@@@@@@@@@@\t\t')
print('\t@@@@@@@@@@@@@@@@@Bachelor Degree Final Project@@@@@@@@@@@@@@@@\t')
print('\t@@@@@@@@@@@@@@@@@@@Islamic Azad University@@@@@@@@@@@@@@@@@@@@\t')
print('\t\t@@@@@@@@@@@@@@@@@@@@@@@2017/07/07@@@@@@@@@@@@@@@@@@@@@@@@@\t\t')

TAB_1 = '\t - '
TAB_2 = '\t\t - '
TAB_3 = '\t\t\t - '
TAB_4 = '\t\t\t\t - '

DATA_TAB_1 = '\t   '
DATA_TAB_2 = '\t\t   '
DATA_TAB_3 = '\t\t\t   '
DATA_TAB_4 = '\t\t\t\t   '

def main():
    
	conn=socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.ntohs(3))
	while True:

		raw_data,addr=conn.recvfrom(65536)
		dest_mac,src_mac,eth_proto,data=ethernet_frame(raw_data)
		print('\nEthernet Frame:')
		print(TAB_1+'Destination: {},Source:{},protocol:{}'.format(dest_mac,src_mac,eth_proto))
		if eth_proto==8:
			    (version,header_lenght,ttl,proto,src,target,data)=ipv4_packet(data)
			    print(TAB_1 +'ipv4 packet:')
			    print(TAB_2 +'version:{},header lenght: {},TTL: {}'.format(version,header_lenght,ttl)) 
			    print(TAB_2 +'protocol:{},source: {},target: {}'.format(proto,src,target))
			    if proto ==1:
		 	        (icmp_type,code,checksum,data)=icmp_packet(data)
		 	        print(TAB_1 +'icmp packet:')
		 	        print(TAB_2 +'type:{},code: {},checksum: {}'.format(icmp_type,code,checksum)) 
		 	        print(TAB_2 +'data:')
		 	        print(format_multi_line(DATA_TAB_3,data))
			    elif proto == 6:
		 	        src_port,dest_port,sequence,acknowledgment,flag_urg,flag_ack,flag_psh,flag_rst,flag_syn,flag_fin,data=tcp_segment(data)
		 	        print(TAB_1 + 'tcp Segment:')
		 	        print(TAB_2 + 'Source Port: {}, Destination Port: {}'.format(src_port, dest_port))
		 	        print(TAB_2 + 'Sequence: {}, Acknowledgment: {}'.format(sequence, acknowledgment))
		 	        print(TAB_2 + 'Flags:')
		 	        print(TAB_3 + 'URG: {}, ACK: {}, PSH: {}'.format(flag_urg,flag_ack,flag_psh))
		 	        print(TAB_3 + 'RST: {}, SYN: {}, FIN: {}'.format(flag_rst,flag_syn,flag_fin))
		 	        print(TAB_2 +'data:')
		 	        print(format_multi_line(DATA_TAB_3,data))
			    elif proto == 17:
		 	        src_port,dest_port,lenght,data=udp_segment(data)
		 	        print(TAB_1 + 'UDP Segment:')
		 	        print(TAB_2 + 'Source Port: {}, Destination Port: {}, Length: {}'.format(src_port, dest_port,lenght))
			    else:
		 	        print(TAB_1 + 'Data:')
		 	        print(format_multi_line(DATA_TAB_1, data))

		else:
			print('Data:')
			print(format_multi_line(DATA_TAB_1,data))
	
def ethernet_frame(data):
			dest_mac,src_mac,proto=struct.unpack('! 6s 6s H',data[:14])
			return get_mac_addr(dest_mac),get_mac_addr(src_mac),socket.htons(proto),data[14:]
def get_mac_addr(bytes_addr):
			bytes_str = map('{:02x}'.format,bytes_addr)
			return ':'.join(bytes_str).upper()
def ipv4_packet(data):
			version_header_lenght=data[0]
			version=version_header_lenght>>4
			header_lenght=(version_header_lenght & 15)*4
			ttl,proto,src,target=struct.unpack('! 8x B B 2x 4s 4s', data[:20])
			return version,header_lenght,ttl,proto,ipv4(src),ipv4(target),data[header_lenght:]
def ipv4(addr):
			return '.'.join(map(str,addr))
def icmp_packet(data):
			icmp_type,code,checksum=struct.unpack('! B B H', data[:4])
			return icmp_type,code,checksum,data[4:]
def tcp_segment(data):
			(src_port,dest_port,sequence,acknowledgment,offset_reserved_flags)=struct.unpack('! H H L L H', data[:14])
			offset=(offset_reserved_flags >> 12) *4
			flag_urg=(offset_reserved_flags & 32) >> 5
			flag_ack=(offset_reserved_flags & 16) >> 4
			flag_psh=(offset_reserved_flags & 8) >> 3
			flag_rst=(offset_reserved_flags & 4) >> 2
			flag_syn=(offset_reserved_flags & 2) >> 1
			flag_fin= offset_reserved_flags & 1
			return src_port,dest_port,sequence,acknowledgment,flag_urg,flag_ack,flag_psh,flag_rst,flag_syn,flag_fin,data[offset:]
def udp_segment(data):
			src_port,dest_port,size=struct.unpack('! H H 2x H',data[:8])
			return src_port,dest_port,size,data[8:]
def format_multi_line(prefix,string,size=80):
			size-=len(prefix)
			if isinstance(string,bytes):
				string=''.join(r'\x{:02x}'.format(byte)for byte in string)
				if size %2: 
					size -=1
			return '\n'.join([prefix+line for line in wrap(string,size)])
			
main()
