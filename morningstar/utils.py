from typing import List

SYSEX_DEVICE_VERSION = 0x03
SYSEX_DEVICE_ID = 0x03
SYSEX_MANUFACTURER_ID1 = 0x00
SYSEX_MANUFACTURER_ID2 = 0x21
SYSEX_MANUFACTURER_ID3 = 0x24
SYSEX_START_PACKET = 0xF0
STANDARD_HEADER = (SYSEX_START_PACKET,
                   SYSEX_MANUFACTURER_ID1,
                   SYSEX_MANUFACTURER_ID2,
                   SYSEX_MANUFACTURER_ID3,
                   SYSEX_DEVICE_ID,
                   SYSEX_DEVICE_VERSION)

from morningstar.checksum import add_checksum_footer


def format_data_line(data: List[int]) -> str:
    return " ".join(["{:02x}".format(b).upper() for b in data])


def format_data(data_lines: List[List[int]]) -> str:
    return '\n'.join([format_data_line(d) for d in data_lines])


def sysex_line(data: List[int]) -> List[int]:
    return add_checksum_footer(list(STANDARD_HEADER) + data)


def sysex_text(text: str, field_length: int) -> List[int]:
    data = []
    for i in range(0, field_length):
        if text and i < len(text):
            data.append(ord(text[i]))
        else:
            data.append(ord(' '))
    return data


def parse_string(data_bytes: List[int]) -> str:
    return ''.join([chr(b) for b in data_bytes]);


def parse_bytes(text: str) -> List[int]:
    data = text.split(" ")
    return [int(b, 16) for b in data]