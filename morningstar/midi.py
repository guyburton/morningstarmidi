
can_send = False
device_name = 'Morningstar MC6MK2'
try:
    import mido

    can_send = True
    ports = mido.get_output_names()
    print("Available ports: " + ", ".join(ports) + " (default is '" + device_name + "')")
    if len(ports) == 1:
        device_name = ports[0]
    else:
        for port in ports:
            if port.startswith(device_name):
                device_name = port

except ImportError:
    print("Could not load module mido- run 'pip install mido' if you wish to send midi commands directly")


def send(data_bytes):
    if can_send:
        port = mido.open_output(device_name)
        # do we need to send a command first to start upload?
        port.send(mido.Message('sysex', data=data_bytes[1:-1]))


if __name__ == "__main__":
    pass  # don't need to do anything since we print during module import
