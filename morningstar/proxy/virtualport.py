import time

import mido
from mido.sockets import connect

"""
This is a utility to create a local virtual MIDI port which will forward
sysex data across the network to a running proxy server
"""


def main(hostname='localhost', port=8081):
    device_name = 'Morningstar MC6MK2 proxy'
    with mido.open_ioport(device_name, virtual=True) as virtual_port:
        print("Created virtual port '" + device_name + "'")
        while True:
            try:
                with connect(hostname, port) as client_port:
                    print('Connected to proxy server')
                    while True:
                        for message in virtual_port.iter_pending():
                            print("Proxying message to MC6: " + str(message))
                            client_port.send(message)
                        for message in client_port.iter_pending():
                            print("Proxying message from MC6: " + str(message))
                            virtual_port.send(message)
                        time.sleep(0)
            except Exception as e:
                print("Caught exception: " + str(e))
                time.sleep(0)


if __name__ == "__main__":
    main()