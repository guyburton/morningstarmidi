#!/usr/bin/python
import argparse
import os
from typing import List

import yaml

import morningstar.midi
from morningstar.model import NUM_PRESETS, NUM_EXPR_PRESETS, ACTIONS, MESSAGE_TYPES, EXPRESSION_TYPES, \
    Action, Message, Bank
from morningstar.utils import format_data


def parse_expression_message(message_type: str, default_channel: int, config) -> Message:
    message = Message()
    config_value = config[message_type]
    if message_type == 'expression_cc':
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

    if isinstance(config_value, dict) and config_value.get("channel"):
        message.channel = config_value["channel"]
    else:
        message.channel = config.get("channel") or default_channel
    message.message_type = message_type
    return message


def convert_to_bank(bank_config):  # noqa: C901
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

                        action = Action()
                        action.action_type = action_type
                        preset.actions.append(action)

                        for message_type in MESSAGE_TYPES:
                            if message_type in action_config:
                                message = Message().from_dict(message_type, action_config)
                                action.messages.append(message)

                        messages_config = action_config.get("messages")
                        if messages_config:
                            for message_config in messages_config:
                                for message_type in MESSAGE_TYPES:
                                    if message_type in message_config:
                                        message = Message().from_dict(message_type,
                                                                message_config)
                                        if action_config.get("channel"):
                                            message.channel = action_config.get("channel")
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
                                message = parse_expression_message(message_type, 1, message_config)
                                preset.messages.append(message)
    return bank


def main(yaml_file, output_file=None, try_send=False, bank=None) -> List[List[int]]:
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
        morningstar.midi.send(data_bytes)

    return data_bytes


def process_file(inputfilename, outputfilename, args):
    with open(inputfilename, 'r') as inputfile:
        with open(outputfilename, 'w') as outputfile:
            main(inputfile, outputfile, args["send"], args["bank"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate sysex for Morningstar MC6 mk2')
    parser.add_argument('file', type=str,
                        help='yaml bank file')
    parser.add_argument('-o', '--output', type=str,
                        help='output as file')
    parser.add_argument('-s', '--send', action='store_true',
                        help='attempt to send directly to device')
    parser.add_argument('-d', '--midi-device', dest='device', type=str,
                        help='alternate midi device name (default is "Morningstar MC6MK2")')
    parser.add_argument('-b', '--bank', type=int,
                        help='export specific bank number')

    args = vars(parser.parse_args())

    if args["device"]:
        morningstar.midi.device_name = args["device"]

    if os.path.isdir(args["file"]):
        files = os.listdir(args["file"])
        if args["output"] and not os.path.isdir(args["output"]):
            print("Input file is a directory, but output file is not")
            exit(2)

        for inputfilename in files:
            if '.yml' not in inputfilename:
                continue
            outputfilename = inputfilename.replace('.yml', '.syx')

            process_file(
                os.path.join(args["file"], inputfilename),
                os.path.join(args["output"], outputfilename),
                args)
    else:
        process_file(args["file"], args["output"], args)
