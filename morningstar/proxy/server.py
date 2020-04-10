import time

import mido
from mido.sockets import PortServer

"""
This is a network server which will forward sysex messages from a TCP socket to the MC6
"""


def main(device_name, port=8081):
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

    with mido.open_ioport(device_name) as device:
        with PortServer('localhost', port) as server:
            print("Listening on port " + str(port))
            while True:
                try:
                    client = server.accept()
                    print('Accepted connection from ' + str(client))
                    while True:
                        for message in client.iter_pending():
                            print("Proxying message from network to device: " + str(message))
                            device.send(message)
                        for message in device.iter_pending():
                            print("Proxying message from device to network: " + str(message))
                            client.send(message)
                    time.sleep(0)
                except Exception as e:
                    print("Caught exception: " + str(e))
                    time.sleep(0)



if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
