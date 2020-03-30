#!/usr/bin/python
import sys
from typing import List


def main(argv):
    databytes1 = []
    for arg in argv:
        for f in arg.split(","):
            y = int(f, 16)
            databytes1.append(y)
    databytes = databytes1

    if len(databytes) != 14:
        print("Warning- expected 14 bytes, found " + str(len(databytes)))

    print("{:02x}".format(checksum).upper())


def checksum(bytes: List[int]) -> int:
    x = 0
    for y in bytes:
        if type(y) is not int:
            raise Exception("Bad data input to checksum: " + str(bytes))
        x ^= y
    return x & 127


def add_checksum_footer(bytes: List[int]) -> List[int]:
    bytes.append(checksum(bytes))
    bytes.append(0xF7)
    return bytes


if __name__ == "__main__":
    main(sys.argv[1:])
