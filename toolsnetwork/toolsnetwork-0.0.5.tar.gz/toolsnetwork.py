import struct
import socket
import textwrap
import binascii

# Returns The destination mac in byte Format
def eth_d_mac(data):d_mac,xxx,yyy=struct.unpack('! 6s 6s H',data[:14]);return d_mac
# Returns The source mac in byte Format
def eth_s_mac(data):
    xxx,s_mac,yyy=struct.unpack('! 6s 6s H',data[:14])
    return s_mac
#Returns The Higher Protocol OR Type of higher data encapsulation
def eth_type(data):
    xxx,yyy,etype=struct.unpack('! 6s 6s H',data[:14])
    return socket.htons(etype)
#Formatting into Standard mac address format 
def f_mac(baddr):
    saddr=map('{:02x}'.format,baddr);
    maddr=':'.join(saddr).upper()
    return maddr
#Returns data present in etherent frame
def eth_data(data):
    return data[14:];
#Returns Source IP of IPv4 Packet
def net4_s_ip(data):
    xxx,yyy,sip,zzz = struct.unpack('! 8x B B 2x 4s 4s',data[:20])
    return sip;
#Returns Destination IP of IPv4 Packet
def net4_d_ip(data):
    xxx,yyy,zzz,dip = struct.unpack('! 8x B B 2x 4s 4s',data[:20])
    return dip;
#Returns IPv4 Packet's Time To Live
def net4_ttl(data):
    ttl,xxx,yyy,zzz = struct.unpack('! 8x B B 2x 4s 4s',data[:20])
    return ttl;
#Returns IPv4 Transport Layer Protocol
def net4_prot(data):
    xxx,ptcl,yyy,zzz = struct.unpack('! 8x B B 2x 4s 4s',data[:20])
    return ptcl
#Returns IPv4 Header Length
def net4_ihl(data):
    tdata=data[0]
    ihl=(tdata & 15)*4
    return ihl
#Retuns IPv4 Data after header
def net4_data(data):
    ihl=net4_ihl(data)
    return data[ihl:]
#Version of IPv4 and IPv6 Packet
def net_ver(data):
    tdata=data[0]
    ver=tdata>>4
    return ver
#Returns IPv6 Packet's Traffic Class (NC)
def net6_t_class(data):
    temp_t_class = data[1]
    t_class = (temp_t_class >> 4) & 255
    return t_class
#Returns IPv6 PAcket's Flow Control (NC)
def net6_f_ctrl(data):
    temp_f_ctrl = data[3]
    f_ctrl = temp_f_ctrl & 4294963200
    return f_ctrl
#Returns Pay load length of IPv6 Packet (NC)
def net6_p_len(data):
    p_len= struct.unpack('! 4x H ',data[:6])
    return p_len
#Returns Nex Header (Transport Layer header Type) in IPv6 Packet (NC)
def net6_n_header(data):
    xxx,n_header = struct.unpack('! 4x H B',data[:7])
    return n_header
#Returns Hop Limit of IPv6 Packet (NC)
def net6_h_limit(data):
    xxx,yyy,h_limit =  struct.unpack('! 4x H B B',data[:8])
    return h_limit
#Returns IPv6 Source Address (NC)
def net6_s_ip(data):
    xxx,yyy,zzz,sip = struct.unpack('! 4x H B B 16s',data[:24])
    return get_ipv6(sip)
#Returns IPv6 Destination Address(NC)
def net6_d_ip(data):
    www,xxx,yyy,zzz,dip = struct.unpack('! 4x H B B 16s 16s',data[:40])
    return get_ipv6(dip)
#Returns IPv6 Data after Header(NC)
def net6_data(data):
    return data[40:]
#Formatting into Standard IPv4 (Dotted Decimal) Format(NC)
def get_ipv4(ip):
    return'.'.join(map(str,ip))
#Formatting into Standard IPv6 (Hexa Decimal) format (NC)
def get_ipv6(ip):
    return socket.inet_ntop(socket.AF_INET6, ip)
#Returns ICMP Type (NC)
def icmp_type(data):
    itype = struct.unpack('! B',data[:1])
    return icmp_type
#Returns ICMP Code (NC)
def icmp_code(data):
    xxx,icode= struct.unpack('! B B',data[:2])
    return icode
#Returns ICMP Check Sum(NC)
def icmp_c_sum(data):
    xxx,yyy,ichecksum = struct.unpack('! B B H',data[:4])
    return ichecksum
#Return ICMP Data (NC)
def icmp_data(data):
    return data[4:]
#Returns UDP Segment's Source Port(NC)
def udp_s_port(data):
    s_port = struct.unpack('! H', data[:2])
    return s_port
#Returns UDP Segment's Destination Port(NC)
def udp_d_port(data):
    xxx,d_port = struct.unpack('! H H', data[:4])
    return d_port
#Returns UDP Segment's Length
def udp_len(data):
    xxx,yyy,ulen = struct.unpack('! H H H', data[:6])
    return ulen
#Returns UDP Segment's Check Sum
def udp_c_sum(data):
    xx,yyy,zzz, c_sum = struct.unpack('! H H H H', data[:8])
    return c_sum
#Returns UDP Segment's Data
def udp_seg(data):
    return data[8:]
#Returs TCP Source Port Number
def tcp_s_port(data):
    s_port = struct.unpack('! H', data[:2])
    return s_port
#Returs Destination Port Number
def tcp_d_port(data):
    xxx, d_port = struct.unpack('! H H', data[:4])
    return d_port
#Returs TCP Sequence Number
def tcp_seq_num(data):
    xxx, yyy, seq_num = struct.unpack('! H H L', data[:8])
    return seq_num
#Returs TCP Acknowledge Number
def tcp_seq_num(data):
    xxx, yyy,zzz,ack_num = struct.unpack('! H H L', data[:12])
    return ack_num
#Returns TCP offset and flags
def tcp_offset_flag(data):
    www,xxx,yyy,zzz, off_flag = struct.unpack('! H H L L H', data[:14])
    return off_flag
#Returns TCP offset Address of Data
def tcp_offset(data):
    offset_flag=tcp_offset_flag(data)
    offset = (offset_flag >> 12) * 4
    return offset
#Returns TCP Segment's NS Flag
def tcp_n_flag(data):
    offset_flag=tcp_offset_flag(data)
    n_flag = (offset_flag & 256) >> 8
    return n_flag
#Returns TCP Segment's CWR Flag
def tcp_c_flag(data):
    offset_flag=tcp_offset_flag(data)
    c_flag = (offset_flag & 128) >> 7
    return c_flag
#Returns TCP Segment's ECN flag
def tcp_e_flag(data):
    offset_flag=tcp_offset_flag(data)
    e_flag = (offset_flag & 64) >> 6
    return e_flag
#Returns TCP Segment's Urgent Flag
def tcp_u_flag(data):
    offset_flag=tcp_offset_flag(data)
    u_flag = (offset_flag & 32) >> 5
    return u_flag
#Returns TCP Segment's Acknowledgement Flag
def tcp_a_flag(data):
    offset_flag=tcp_offset_flag(data)
    a_flag = (offset_flag & 16) >> 4
    return a_flag
#Returns TCP Segment's Push Flag
def tcp_p_flag(data):
    offset_flag=tcp_offset_flag(data)
    p_flag = (offset_flag & 8) >> 3
    return p_flag
#Returns TCP Segment's Reset Flag
def tcp_r_flag(data):
    offset_flag=tcp_offset_flag(data)
    r_flag = (off_resv_flags & 4) >> 2
    return s_port, d_port, seq, ack, u_flag,a_flag, p_flag, r_flag, s_flag, f_flag, data[offset:]
#Returns TCP Segment's Synchronize Flag
def tcp_s_flag(data):
    offset_flag=tcp_offset_flag(data)
    s_flag = (offset_flag & 2) >> 1
    return s_flag
#Returns TCP Segment's Finisish Flag
def tcp_f_flag(data):
    offset_flag=tcp_offset_flag(data)
    f_flag = (offset_flag & 1)
    return f_flag
#Returns TCP Segment's Offset
def tcp_s_port(data):
    offset = tcp_offset(data)
    return data[offset:]





