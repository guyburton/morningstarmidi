from typing import List

from morningstar.utils import sysex_line, sysex_text

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

    def letter(self):
        return chr(self.id + ord('A'))

    def to_dict(self):
        data = {
            "name": self.name,
            "toggle_name": self.toggle_name,
            "long_name": self.long_name,
            "toggle_mode": self.toggle_mode,
            "blink_mode": self.blink_mode,
            "actions": []
        }

        return data


class ExpressionPreset:

    def __init__(self, id: int):
        self.id = id
        self.name = " EXPRN"
        self.long_name = ""
        self.toggle_name = " EXPRN"
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

    def to_dict(self):
        data = {
            "name": self.name,
            "toggle_name": self.toggle_name,
            "long_name": self.long_name,
            "actions": []
        }
        return data


class Bank:
    # it's not really clear what these do yet -potentially just 'bank upload'?
    header1 = sysex_line([0x02, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    header2 = sysex_line([0x01, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    def __init__(self, name):
        self.presets = []
        self.expression_presets = []
        for i in range(0, NUM_PRESETS):
            self.presets.append(Preset(i))
        for i in range(0, NUM_EXPR_PRESETS):
            self.expression_presets.append(ExpressionPreset(i))
        self.name = name

    def to_sysex(self) -> List[List[int]]:
        lines = [self.header1, self.header2]
        lines.append(sysex_line([0x01, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00] +
                                sysex_text(self.name, 24)))

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

    def to_dict(self):
        builder = {
            "name": self.name,
            "presets": {}
        }
        for preset in self.presets:
            builder["presets"][preset.letter()] = preset.to_dict()
        for i, preset in enumerate(self.expression_presets):
            builder["presets"]['expression' + str(i + 1)] = preset.to_dict()
        return builder


