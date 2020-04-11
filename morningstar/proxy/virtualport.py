import argparse
import sys
import time

import mido
from mido.sockets import connect

"""
This is a utility to create a local virtual MIDI port which will forward
sysex data across the network to a running proxy server
"""


def main(hostname='localhost', port=8081):
    device_name = 'Morningstar MC6MK2 proxy'
    client_port = None

    def virtual_message(message):
        if client_port:
            print("Proxying message to MC6: " + str(message))
            client_port.send(message)
        else:
            print("No network connection to proxy message to " + str(message))

    with mido.open_ioport(device_name, virtual=True, callback=virtual_message) as virtual_port:
        print("Created virtual port '" + device_name + "'")
        while True:
            try:
                print("Connecting to " + hostname + ":" + str(port))
                with connect(hostname, port) as client:
                    client_port = client
                    print('Connected to proxy server')
                    for message in client:
                        print("Proxying message from MC6: " + str(message))
                        virtual_port.send(message)
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception as e:
                client_port = None
                print("Caught exception: " + str(e))
                time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start virtual midi port proxying commands to network')
    parser.add_argument('hostname', type=str, default='localhost',
                        help='hostname to connect to')
    parser.add_argument('port', type=int, default=8081,
                        help='TCP port number to connect to')
    args = vars(parser.parse_args())
    main(args["hostname"], args["port"])
