
can_send = False
device_name = 'Morningstar MC6MK2'
try:
    import mido

    can_send = True
    ports = mido.get_output_names()
    if device_name not in ports:
        print("Available ports: " + ", ".join(ports))

except ImportError:
    print("Could not load module mido- run 'pip install mido' if you wish to send midi commands directly")


def send(data_bytes):
    if can_send:
        port = mido.open_output(device_name)
        # do we need to send a command first to start upload?
        port.send(mido.Message('sysex', data=data_bytes[1:-1]))
