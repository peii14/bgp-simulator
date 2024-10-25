import ipaddress
import struct

from enum import Enum

ATTR_OPTIONAL = 1 << 7
ATTR_TRANSITIVE = 1 << 6
ATTR_PARTIAL = 1 << 5
ATTR_EXTENDED = 1 << 4

class BgpAttributeType(Enum):
        ORIGIN = 1
        AS_PATH = 2
        NEXT_HOP = 3
        MULTI_EXIT_DISC = 4
        LOCAL_PREF = 5
        ATOMIC_AGGREGATE = 6
        AGGREGATOR = 7

class BgpPathAttribute():
    def __init__(self):
        pass

    def frombytes(self, path_attr_bytes):
        flags = int(path_attr_bytes[0])
        attr_type = int(path_attr_bytes[1])

        self.optional = bool(flags & ATTR_OPTIONAL)
        self.transitive = bool(flags & ATTR_TRANSITIVE)
        self.partial = bool(flags & ATTR_PARTIAL)
        self.extended = bool(flags & ATTR_EXTENDED)
        self.flags = flags

        length_idx = 3 if not self.extended else 4

        self.type = BgpAttributeType(attr_type)
        self.length = int(path_attr_bytes[2]) if not self.extended else int(path_attr_bytes[2:4])

        attr_bytes = path_attr_bytes[length_idx:]

        match BgpAttributeType(self.type):
            case BgpAttributeType.ORIGIN:
                self.data = {
                    "origin": int(attr_bytes[0])
                }
            case BgpAttributeType.AS_PATH:
                len_asn, seg_type = struct.unpack("!2B", attr_bytes[:2])
                asn_tuple = struct.unpack(f"!{len_asn}H", attr_bytes[2:])

                asns = []
                asns.extend(asn_tuple)

                self.data = {
                    "length": len_asn,
                    "segment_type": seg_type,
                    "asns": asns,
                }
            case BgpAttributeType.NEXT_HOP:
                self.data = {
                    "ip_addr": ipaddress.IPv4Address(struct.unpack("!I", attr_bytes[0:4])[0])
                }
            case BgpAttributeType.MULTI_EXIT_DISC:
                self.data = {
                    "metric": struct.unpack("!I", attr_bytes[0:4])[0]
                }
            case _:
                self.data = {}
    
    def pack(self) -> bytes:
        header = struct.pack("!3B", self.flags, self.type.value, self.length)
        payload = header

        match BgpAttributeType(self.type):
            case BgpAttributeType.ORIGIN:
                payload += struct.pack("!B", self.data['origin'])
            case BgpAttributeType.AS_PATH:
                packed_asns = bytes(0)
                for _,asn in enumerate(self.data['asns']):
                    packed_asns += struct.pack("!H", asn)

                payload += struct.pack(f"!2B", self.data['length'], self.data['segment_type'])
                payload += packed_asns
            case BgpAttributeType.NEXT_HOP:
                payload += struct.pack("!4s", self.data['ip_addr'].packed)
            case BgpAttributeType.MULTI_EXIT_DISC:
                payload += struct.pack("!I", self.data['metric'])
            case _:
                pass

        return payload

    def __str__(self):
        return f"<BgpAttribute flags={self.flags} type={self.type} length={self.length} data={self.data} />"