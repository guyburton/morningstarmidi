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
                with connect(hostname, port) as client:
                    client_port = client
                    print('Connected to proxy server on port ' + str(port))
                    for message in client:
                        print("Proxying message from MC6: " + str(message))
                        virtual_port.send(message)
            except Exception as e:
                client_port = None
                print("Caught exception: " + str(e))
                time.sleep(1)


if __name__ == "__main__":
    main()