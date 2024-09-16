import struct

def create_ip_packet(src_ip, dst_ip, payload):
    version = 4
    ihl = 5  # Header length
    total_length = ihl * 4 + len(payload)
    packet_id = 54321  # Random packet ID
    flags = 0
    fragment_offset = 0
    ttl = 64  
    protocol = 6  # TCP
    checksum = 0 
    src_ip = ip_to_bytes(src_ip)
    dst_ip = ip_to_bytes(dst_ip)

    # Assemble the packet
    ip_header = struct.pack('!BBHHHBBH4s4s',
                            (version << 4) + ihl,
                            0,  # Type of Service
                            total_length,
                            packet_id,
                            (flags << 13) + fragment_offset,
                            ttl,
                            protocol,
                            checksum,
                            src_ip,
                            dst_ip)
    return ip_header + payload

def ip_to_bytes(ip):
    """Convert an IPv4 address string to bytes."""
    return bytes(map(int, ip.split('.')))

def parse_ip_packet(packet):
    """Parse an IPv4 packet and return the source IP, destination IP, and payload."""
    ip_header = packet[:20]
    iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
    src_ip = '.'.join(map(str, iph[8]))
    dst_ip = '.'.join(map(str, iph[9]))
    payload = packet[20:]
    return src_ip, dst_ip, payload