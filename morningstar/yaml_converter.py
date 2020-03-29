#!/usr/bin/python
import sys
import yaml
import argparse

from morningstar.checksum import add_checksum_footer
from typing import List

SYSEX_DEVICE_VERSION = 0x03
SYSEX_DEVICE_ID = 0x03
SYSEX_MANUFACTURER_ID1 = 0x00
SYSEX_MANUFACTURER_ID2 = 0x21
SYSEX_MANUFACTURER_ID3 = 0x24
SYSEX_START_PACKET = 0xF0
STANDARD_HEADER = (SYSEX_START_PACKET,
                   SYSEX_MANUFACTURER_ID1,
                   SYSEX_MANUFACTURER_ID2,
                   SYSEX_MANUFACTURER_ID3,
                   SYSEX_DEVICE_ID,
                   SYSEX_DEVICE_VERSION)
NUM_PRESETS = 12  # for MC 6
NUM_EXPR_PRESETS = 2

DEFAULT_MESSAGE = (0x00, 0x00, 0x00, 0x00, 0x00, 0x00)

ACTIONS = [
    "no_action",
    "press",
    "release",
    "long_press",
    "long_press_release",
    "double_tap",
    "double_tap_release",
    "long_double_tap",
    "long_double_tap_release",
    "release_all",
]

MESSAGE_TYPES = [
    "empty",
    "program_change",
    "control_change",
    "note_on",
    "note_off",
    "real_time",
    "sysex",
    "midi_clock",
    "pc_scroll_up",
    "pc_scroll_down",
    "device_bank_up",
    "device_bank_down",
    "device_bank_change_mode",
    "device_set_bank",
    "device_toggle_page",
    "device_toggle_preset",
    "device_set_midi_thru",
    "device_select_expression_pedal_message",
    "device_looper_mode",
    "strymon_bank_up",
    "strymon_bank_down",
    "axefx_tuner",
    "delay",
    "midi_clock_tap",
]

expression_types = [
    "empty",
    "expression_cc",
    "cc_toe_down",
    "cc_heel_down",
    "toe_down_toggle_channel",
    "toe_down_toggle_cc",
]

can_send = False
try:
    import mido

    can_send = True
except ImportError:
    print("Could not load module mido- run 'pip install mido' if you wish to send midi commands directly")


def sysex_line(*data):
    return add_checksum_footer(list(STANDARD_HEADER) + list(data) if data is not List[int] else data)


def sysex_text(config_object, field_name: str, field_length: int, default_value=None) -> List[int]:
    data = []
    for i in range(0, field_length):
        if field_name in config_object and i < len(config_object[field_name]):
            data.append(ord(config_object[field_name][i]))
        else:
            data.append(ord(default_value[i]) if default_value and i < len(default_value) else ord(' '))
    return data


def sysex_preset(preset_config, preset_number: int):
    data = [0x01, 0x07, 0x00, preset_number, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

    messages = [list(DEFAULT_MESSAGE) * 16]

    message_count = 0
    if "actions" in preset_config:
        for action in preset_config.actions:
            if not action.type:
                raise Exception("Action does not have a action type: " + str(action))

            action_type = ACTIONS.index(action.type)

            for message in action.messages:
                data1 = 0
                data2 = 0
                data3 = 0
                channel = 0
                message_type = MESSAGE_TYPES.index(message)
                messages[message] = [data1, data2, data3, channel, message_type, action_type]
                message_count += 1
                if message_count >= 16:
                    raise Exception("More than 16 messages assigned to action: " + str(action))

    for m in messages:
        data += m

    data += [0x00, 0x00]

    data += sysex_text(preset_config, "name", 8, " EMPTY")
    data += sysex_text(preset_config, "toggle_name", 8, " EMPTY")
    data += sysex_text(preset_config, "long_name", 24)
    return sysex_line(*data)


def sysex_expr_preset(expression_preset_number: int) -> List[int]:
    return sysex_line(0x01, 0x08, 0x00, expression_preset_number, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20,
                      0x45, 0x58, 0x50, 0x52, 0x4e, 0x20, 0x20, 0x20, 0x45, 0x58, 0x50, 0x52, 0x4e, 0x20, 0x20, 0x20,
                      0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20,
                      0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20)


def convert_to_sysex(config):
    lines = []
    # it's not really clear what these do yet -potentially just 'bank upload'?
    lines.append(sysex_line(0x02, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))
    lines.append(sysex_line(0x01, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))
    lines.append(sysex_line(0x01, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            *sysex_text(config, "name", 24)))

    for i in range(0, NUM_PRESETS):
        preset_letter = chr(i + 65)
        preset_config = {}
        if "presets" in config and preset_letter in config.presets:
            preset_config = config.presets[preset_letter]
        lines.append(sysex_preset(preset_config, i))

    for i in range(0, NUM_EXPR_PRESETS):
        lines.append(sysex_expr_preset(i))

    lines.append(sysex_line(0x7E, 0x00, 0x13, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 00))

    return lines


def format_data_line(data):
    return " ".join(["{:02x}".format(b).upper() for b in data])


def format_data(data_lines):
    return '\n'.join([format_data_line(d) for d in data_lines])


def main(yaml_file, output_file, try_send, bank):
    config = yaml.full_load(yaml_file)
    print(config)

    data_bytes = convert_to_sysex(config)
    formatted_data = format_data(data_bytes)
    print(formatted_data)

    if output_file:
        output_file.write(formatted_data)

    if try_send:
        port = mido.open_output('Morningstar MC6MK2')
        # do we need to send a command first to start upload?
        for b in data_bytes:
            port.send(mido.Message('sysex', data=b[1:-1]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate sysex for Morningstar MC6 mk2')
    parser.add_argument('file', type=argparse.FileType('r'),
                        help='yaml bank file')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        help='output as file')
    parser.add_argument('-s', '--send', action='store_true',
                        help='attempt to send directly to device')
    parser.add_argument('-d', '--midi-device', type=str,
                        help='alternate midi device name (default is "Morningstar MC6MK2")')
    parser.add_argument('-b', '--bank', type=int,
                        help='export specific bank number')

    args = vars(parser.parse_args())

    main(args["file"], args["output"], args["send"], args["bank"])
