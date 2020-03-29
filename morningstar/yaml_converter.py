#!/usr/bin/python
import argparse
from typing import List, Dict

import yaml
from math import floor

from morningstar.checksum import add_checksum_footer

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
    "realtime",
    "sysex",
    "midi_clock",
    "pc_scroll_up",
    "pc_scroll_down",
    "device_bank_up",
    "device_bank_down",
    "device_bank_change_mode",
    "device_set_bank",
    "device_toggle_page",
    "device_set_toggle",
    "device_set_midi_thru",
    "device_select_expression_pedal_message",
    "device_looper_mode",
    "strymon_bank_up",
    "strymon_bank_down",
    "axefx_tuner",
    "toggle_preset",
    "delay",
    "midi_clock_tap",
]

EXPRESSION_TYPES = [
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


def format_data_line(data):
    return " ".join(["{:02x}".format(b).upper() for b in data])


def format_data(data_lines):
    return '\n'.join([format_data_line(d) for d in data_lines])


def sysex_line(data: List[int]) -> List[int]:
    return add_checksum_footer(list(STANDARD_HEADER) + data)


def sysex_text(text: str, field_length: int):
    data = []
    for i in range(0, field_length):
        if text and i < len(text):
            data.append(ord(text[i]))
        else:
            data.append(ord(' '))
    return data


class Action:

    def __init__(self, action_type):
        self.action_type = action_type
        self.messages = []

    def id(self):
        return ACTIONS.index(self.action_type)


class Message:

    def __init__(self):
        self.channel = 1
        self.message_type = MESSAGE_TYPES[0]
        self.data1 = 0
        self.data2 = 0
        self.data3 = 0
        self.toggle_mode = 1

    def id(self):
        return MESSAGE_TYPES.index(self.message_type) if self.message_type in MESSAGE_TYPES else \
            EXPRESSION_TYPES.index(self.message_type)


class Preset:

    def __init__(self, id):
        self.id = id
        self.name = " EMPTY"
        self.long_name = ""
        self.toggle_name = " EMPTY"
        self.toggle_mode = False
        self.blink_mode = False
        self.actions = []

    def to_sysex(self) -> List[int]:
        data = [0x01, 0x07, 0x00, self.id, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        message_count = 0
        for action in self.actions:
            for message in action.messages:
                # this bit makes no sense but seems to work!?
                if message.toggle_mode == "both":
                    action_byte = action.id() * 2 + 32
                elif message.toggle_mode == 2:
                    action_byte = (action.id() * 2 + 1)
                else:
                    action_byte = action.id() * 2

                data += [message.id(), message.data1, message.data2, message.data3, action_byte, message.channel - 1]
                message_count += 1

        if message_count >= 16:
            raise Exception("More than 16 messages specified for preset: " + str(self))

        for i in range(message_count, 16):
            data += [0, 0, 0, 0, 0, 0]

        bit_field = 0
        if self.toggle_mode:
            bit_field |= 0x08
        if self.blink_mode:
            bit_field |= 0x04

        data += [bit_field, 0x00]

        data += sysex_text(self.name, 8)
        data += sysex_text(self.toggle_name, 8)
        data += sysex_text(self.long_name, 24)
        return sysex_line(data)


class ExpressionPreset:

    def __init__(self, id: int):
        self.id = id
        self.name = " EMPTY"
        self.long_name = ""
        self.toggle_name = " EMPTY"
        self.messages = []

    def to_sysex(self) -> List[int]:
        data = [0x01, 0x08, 0x00, self.id, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        message_count = 0
        for message in self.messages:
            data += [message.id(), message.data1, message.data2, message.data3, 0, message.channel - 1]
            message_count += 1

        if message_count >= 16:
            raise Exception("More than 16 messages specified for preset: " + str(self))

        for i in range(message_count, 16):
            data += [0, 0, 0, 0, 0, 0]

        data += [0, 0]

        data += sysex_text(self.name, 8)
        data += sysex_text(self.toggle_name, 8)
        data += sysex_text(self.long_name, 24)
        return sysex_line(data)


class Bank:

    def __init__(self, name):
        self.presets = []
        self.expression_presets = []
        for i in range(0, NUM_PRESETS):
            self.presets.append(Preset(i))
        for i in range(0, NUM_EXPR_PRESETS):
            self.expression_presets.append(ExpressionPreset(i))
        self.name = name

    def to_sysex(self) -> List[List[int]]:
        lines = []
        # it's not really clear what these do yet -potentially just 'bank upload'?
        lines.append(sysex_line([0x02, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
        lines.append(sysex_line([0x01, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
        lines.append(sysex_line([0x01, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00] + sysex_text(self.name, 24)))

        for preset in self.presets:
            lines.append(preset.to_sysex())

        for preset in self.expression_presets:
            lines.append(preset.to_sysex())

        batch_checksum = 240
        for line in lines:
            batch_checksum ^= line[-2]
        batch_checksum &= 127

        lines.append(sysex_line([0x7E, 0x00, batch_checksum, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 00]))
        return lines


def parse_message(message_type: str, default_channel: int, config):
    message = Message()
    config_value = config[message_type]
    if message_type == 'control_change':
        message.data1 = config_value.get('number') or 0
        message.data2 = config_value.get('value') or 0
    elif message_type in ['note_on', 'note_off']:
        message.data1 = config_value.get('number') or 0
        message.data2 = config_value.get('velocity') or 0
    elif message_type == 'sysex':
        message.data1 = config_value[0] if len(config_value) > 0 else 0
        message.data2 = config_value[1] if len(config_value) > 1 else 0
        message.data3 = config_value[2] if len(config_value) > 2 else 0
    elif message_type == 'realtime':
        message.data1 = ['nothing', 'start', 'stop', 'continue'].index(config_value)
    elif message_type == 'midi_clock':
        message.data1 = floor(config_value.get('bpm') / 100)
        message.data2 = config_value.get('bpm') - (100 * message.data1)
        message.data3 = config_value.get("tap_menu") or 0
    elif message_type == 'midi_clock_tap':
        pass
    elif message_type == 'pc_scroll_up':
        message.data1 = (config_value.get('slot') - 1) + 16 if config_value.get("increment") else 0
        message.data2 = config_value.get('lower_limit') or 0
        message.data3 = config_value.get('upper_limit') or 0
        pass
    elif message_type == 'expression_cc':
        message.data1 = config_value.get('cc_number') or 0
        message.data2 = config_value.get('cc_min_value') or 0
        message.data3 = config_value.get('cc_max_value') or 0
    elif message_type in ['cc_toe_down', 'cc_heel_down']:
        message.data1 = config_value.get('cc_number') or 0
        message.data2 = config_value.get('cc_value') or 0
    elif message_type == 'toe_down_toggle_channel':
        message.data1 = (config_value.get('number') - 1) or 0
        message.data2 = (config_value.get('channel1') - 1) or 0
        message.data3 = (config_value.get('channel2') - 1) or 0
    elif message_type == 'toe_down_toggle_cc':
        message.data1 = (config_value.get('number') - 1) or 0
        message.data2 = config_value.get('cc_number1') or 0
        message.data3 = config_value.get('cc_number2') or 0
    else:
        message.data1 = config.get(message_type)
    message.channel = config.get("channel") or (isinstance(config_value, dict) and config_value.get("channel")) or default_channel
    message.toggle_mode = config.get("toggle_position") or 1
    message.message_type = message_type
    return message


def convert_to_bank(bank_config):
    bank = Bank(bank_config.get("name"))
    presets_config = bank_config.get("presets")
    if presets_config:
        for i in range(0, NUM_PRESETS):
            preset_letter = chr(i + 65)
            if preset_letter in presets_config:
                preset_config = presets_config.get(preset_letter)
                preset = bank.presets[i]
                preset.name = preset_config.get("name")
                preset.toggle_name = preset_config.get("toggle_name")
                preset.long_name = preset_config.get("long_name")
                if "toggle_mode" in preset_config:
                    preset.toggle_mode = preset_config.get("toggle_mode")
                if "blink_mode" in preset_config:
                    preset.blink_mode = preset_config.get("blink_mode")
                messages_config = preset_config.get("actions")
                if messages_config:
                    for action_config in messages_config:
                        action_type = action_config.get("type")
                        if not action_type:
                            raise Exception("Action does not have a action type: " + str(action_config))
                        if action_type not in ACTIONS:
                            raise Exception("Unknown action type: " + action_type)

                        action = Action(action_type)
                        preset.actions.append(action)

                        for message_type in MESSAGE_TYPES:
                            if message_type in action_config:
                                message = parse_message(message_type, 1, action_config)
                                action.messages.append(message)

                        messages_config = action_config.get("messages")
                        if messages_config:
                            for message_config in messages_config:
                                for message_type in MESSAGE_TYPES:
                                    if message_type in message_config:
                                        message = parse_message(message_type, action_config.get("channel") or 1, message_config)
                                        action.messages.append(message)

        for i in range(0, NUM_EXPR_PRESETS):
            expression_name = 'expression' + str(i + 1)
            if expression_name in presets_config:
                preset_config = presets_config.get(expression_name)
                preset = bank.expression_presets[i]
                preset.name = preset_config.get("name")
                preset.toggle_name = preset_config.get("toggle_name")
                preset.long_name = preset_config.get("long_name")
                messages_config = preset_config.get("messages")
                if messages_config:
                    for message_config in messages_config:
                        for message_type in EXPRESSION_TYPES:
                            if message_type in message_config:
                                message = parse_message(message_type, 1, message_config)
                                preset.messages.append(message)
    return bank


def main(yaml_file, output_file, try_send, bank):
    config = yaml.full_load(yaml_file)
    print(config)
    bank = convert_to_bank(config["bank"])
    data_bytes = bank.to_sysex()
    formatted_data = format_data(data_bytes)
    print(formatted_data)

    if output_file:
        output_file.write(formatted_data)
        output_file.write("\n")

    if try_send:
        port = mido.open_output('Morningstar MC6MK2')
        # do we need to send a command first to start upload?
        for b in data_bytes:
            port.send(mido.Message('sysex', data=b[1:-1]))

    return data_bytes


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
