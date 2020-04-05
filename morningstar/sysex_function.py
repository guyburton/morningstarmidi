#!/usr/bin/python
import argparse
import sys

import morningstar.midi
from morningstar.checksum import add_checksum_footer


def main(argv, input_is_hex, try_send):
    data_bytes = [0xF0, 0x00, 0x21, 0x24, 0x00, 0x00]
    for i in range(0, 8):
        if i < len(argv):
            data_bytes.append(int(argv[i], 16 if input_is_hex else 10))
        else:
            data_bytes.append(0)

    add_checksum_footer(data_bytes)

    print(" ".join(["{:02x}".format(b) for b in data_bytes]).upper())

    if try_send:
        morningstar.midi.send(data_bytes)


if __name__ == "__main__":
    args = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Generate sysex for Morningstar MC6 mk2')
    parser.add_argument('-s', '--send', action='store_true',
                        help='attempt to send directly to device')
    parser.add_argument('-x', '--hex', action='store_true',
                        help='input as hex (rather than decimal)')
    parser.add_argument('-d', '--midi-device', dest='device', type=str,
                        help='alternate midi device name (default is "Morningstar MC6MK2")')
    parser.add_argument('data', type=str, nargs='*', help='space or comma delimited args [function byte 1, function byte 2]')

    args = vars(parser.parse_args())

    is_hex = args['hex']
    try_send = args['send']
    if args["device"]:
        morningstar.midi.device_name = args["device"]

    main(args["data"], is_hex, try_send)
