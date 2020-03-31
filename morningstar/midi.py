
can_send = False
device_name = 'Morningstar MC6MK2'
try:
    import mido

    can_send = True
except ImportError:
    print("Could not load module mido- run 'pip install mido' if you wish to send midi commands directly")


def send(data_bytes):
    if can_send:
        port = mido.open_output(device_name)
        # do we need to send a command first to start upload?
        for b in data_bytes:
            port.send(mido.Message('sysex', data_bytes=b[1:-1]))
