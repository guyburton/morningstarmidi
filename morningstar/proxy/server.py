import argparse
import sys
import time

import mido
from mido.sockets import PortServer

"""
This is a network server which will forward sysex messages from a TCP socket to the MC6
"""


def main(device_name, port):
    port_names = mido.get_output_names()
    print("Available ports: " + ", ".join(port_names))

    if device_name and device_name not in port_names:
        raise Exception("Requested device name '" + device_name + "' is not available")

    if len(port_names) == 1:
        device_name = port_names[0]
        print("Using only available port: " + device_name)

    for port_name in port_names:
        if port_name.startswith('Morningstar MC6MK2'):
            print("Using " + port_name)
            device_name = port_name
            break

    if not device_name:
        print("Found multiple ports but none matching default name. Please specify which port name to forward to.")

    client = None

    def device_message(message):
        if client:
            print("Proxying message from device to network: " + str(message))
            client.send(message)
        else:
            print("No network clients connected for " + str(message))

    with PortServer('0.0.0.0', port) as server:
        print("Listening on port " + str(port))
        while True:
            try:
                client = server.accept()
                print('Accepted connection from ' + str(client))
                with mido.open_ioport(device_name, callback=device_message) as device:
                    for message in client:
                        print("Proxying message from network to device: " + str(message))
                        device.send(message)
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception as e:
                client = None
                print("Caught exception: " + str(e))
                time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start network server to proxy MIDI to another device')
    parser.add_argument('port', type=int, help='TCP port number')
    parser.add_argument('-d', '--midi-device', dest='device', type=str, default=None,
                        help='alternate midi device name '
                             '(default is "Morningstar MC6MK2" or any solitary connected device)')
    args = vars(parser.parse_args())
    main(args["device"], args["port"])
