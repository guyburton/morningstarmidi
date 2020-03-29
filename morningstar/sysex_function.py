#!/usr/bin/python
import sys
from morningstar.checksum import add_checksum_footer

can_send = False
try:
    import mido
    can_send = True
except ImportError:
    print("Could not load module mido- run 'pip install mido' if you wish to send midi commands directly")


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
        port = mido.open_output('Morningstar MC6MK2')
        port.send(mido.Message('sysex', data=data_bytes[1:-1]))


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage:")
        print("\t-h input as hex (else decimal)")
        print("\t-s try and send command to device")
        print("\tspace or comma delimited args [function byte 1, function byte 2]")
        exit(0)

    is_hex = '-h' in args
    try_send = '-s' in args
    if is_hex:
        args.remove('-h')
    if try_send:
        args.remove('-s')
    main(args, is_hex, try_send)
