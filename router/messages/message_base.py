import struct
import ipaddress
from enum import Enum

class BgpMessageType(Enum):
    OPEN = 1
    UPDATE = 2
    NOTIFICATION = 3
    KEEPALIVE = 4
    ROUTE_REFRESH = 5

class BgpMessageBase():
    def __init__(self, msg_type=BgpMessageType.KEEPALIVE):
        self.msg_type=msg_type
    
    """ Returns the length of the BGP message.
        A message with no payload (e.g. KEEPALIVE) will have the same size
        as the header (19 bytes).
    """
    def length(self):
        return 19 + (len(self.payload()) if self.payload() else 0)
    
    """ Returns the header of the BGP message encoded as bytes.
        The header consists of
            - a marker of 16 bytes, filled with 1s
            - the total length of the message
            - the message type
    """
    def header(self):
        print(self.length(), self.msg_type, self.msg_type.value)
        return struct.pack(
            "!16BhB",
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            self.length(),
            self.msg_type.value,
        )
    
    """ Returns the information contained on the BGP message, encoded as bytes."""
    def payload(self):
        pass

    """ Retrieves information from a bytes object and converts it to a BGP
        message type.
        Each message type implements the unpack method and calls `unpack` on
        `BGPMessageBase` to parse the message header."""
    def unpack(self, byte_str):
        length, msg_type = struct.unpack("!hB", byte_str[16:19])
        self.msg_type = BgpMessageType(msg_type)
        self.raw_length = length
    
    """ Converts the BGP message to a bytes object, ready to be transmitted
        over the network. """
    def pack(self):
        byte_arr = bytearray()
        byte_arr.extend(self.header())
        byte_arr.extend(self.payload())
        return bytes(byte_arr)
    
    def __str__(self):
        return f"<BGPMessage type={self.msg_type} length={self.length()}>"


class BgpMessageOpen(BgpMessageBase):
    def __init__(self, ip="192.168.0.1", version=4, hold_time=0, as_num=0):
        super().__init__(msg_type=BgpMessageType.OPEN)
        self.payload_fmt = "!BHHIB"
        self.ip_addr = ipaddress.IPv4Address(ip)
        self.version = version
        self.hold_time = hold_time
        self.as_number = as_num

    def payload(self):
        return struct.pack(
            self.payload_fmt,
            4,
            65033,
            180,
            int(self.ip_addr),
            0
        )

    def unpack(self, byte_str):
        super().unpack(byte_str)
        byte_str = byte_str[19:]
        version, as_num, hold_time, ip_addr, opt_params_size = struct.unpack(self.payload_fmt, byte_str)
        print(version, as_num, hold_time, ip_addr, opt_params_size)

        self.version = version
        self.as_number = as_num
        self.hold_time = hold_time
        self.ip_addr = ipaddress.IPv4Address(ip_addr)

    def __str__(self):
        return f"<BGPMessage type={self.msg_type} length={self.length()} version={self.version} as_number={self.as_number} hold_time={self.hold_time} ip={self.ip_addr}>"


class BgpMessageKeepAlive(BgpMessageBase):
    def __init__(self):
        super().__init__(msg_type=BgpMessageType.KEEPALIVE)


class BgpMessageNotification(BgpMessageBase):
    def __init__(self, major, minor, data):
        super().__init__(msg_type=BgpMessageType.NOTIFICATION)

        self.major_code = major
        self.minor_code = minor
        self.data = data

    def payload(self):
        return struct.pack(
            f"!BB{len(self.data)}s",
            self.major_code,
            self.minor_code,
            self.data
        )

    def unpack(self, byte_str):
        super().unpack(byte_str)
        byte_str = byte_str[19:]
        major, minor = struct.unpack("!BB", byte_str[0:2])
        data = struct.unpack(f"!{self.raw_length - 21}s", byte_str[2:])

        self.major_code = major
        self.minor_code = minor
        self.data = data[0]

    def __str__(self):
        return f"<BGPMessage type={self.msg_type} length={self.length()} error_code={self.major_code} suberror_code={self.minor_code} data={self.data}>"


class BgpMessageUpdate(BgpMessageBase):
    def __init__(self):
        pass