#!/usr/bin/python
import sys


def main(argv):
    databytes = parseArgs(argv)

    if len(databytes) != 14:
        print("Warning- expected 14 bytes, found " + str(len(databytes)))

    print("{:02x}".format(checksum).upper())


def parseArgs(argv):
    databytes = []
    for arg in argv:
        for f in arg.split(","):
            y = int(f, 16)
            databytes.append(y)
    return databytes


def checksum(bytes):
    x = 0
    for y in bytes:
        x ^= y
    return x & 127


if __name__ == "__main__":
    main(sys.argv[1:])
