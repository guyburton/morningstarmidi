
can_send = False
device_name = 'Morningstar MC6MK2'
try:
    import mido

    can_send = True
    ports = mido.get_output_names()
    if len(ports) == 1:
        device_name = ports[0]
    else:
        for port_name in ports:
            if port_name.startswith(device_name):
                device_name = port_name

    print("Available ports: " + ", ".join(ports) + " (picked '" + device_name + "')")

except ImportError:
    print("Could not load module mido- run 'pip install mido' if you wish to send midi commands directly")


def send(data_bytes):
    if can_send:
        with mido.open_ioport(device_name) as device_port:
            device_port.send(mido.Message('sysex', data=data_bytes[1:-1]))


if __name__ == "__main__":
    pass  # don't need to do anything since we print during module import
