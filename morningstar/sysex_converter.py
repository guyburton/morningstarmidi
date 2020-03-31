import argparse
import os

import yaml

from morningstar.model import Bank, NUM_PRESETS
from morningstar.utils import parse_bytes, parse_string


def read_preset(preset, data_bytes):
    preset.name = parse_string(data_bytes[-40:-32])
    preset.toggle_name = parse_string(data_bytes[-32:-24])
    preset.long_name = parse_string(data_bytes[-24:])
    pass


def process_file(input_filename):
    with open(input_filename, 'r') as input_file:
        bank = None
        count = 0
        for line in input_file:
            data_bytes = parse_bytes(line)

            if data_bytes == Bank.header1:
                if count != 0:
                    print("Unexpected bank header 1 on line " + str(count))
                count = 1
                continue
            if data_bytes == Bank.header2:
                if count != 1:
                    print("Unexpected bank header 2 in state " + str(count) + ". Assuming start of bank...")
                count = 2
                continue

            # discard sysex header and footer
            data_bytes = data_bytes[1:-2]
            count += 1
            if count == 3:
                name = parse_string(data_bytes[-24:])
                bank = Bank(name)
            elif 4 <= count <= 3 + NUM_PRESETS:
                read_preset(bank.presets[count - 4], data_bytes)

        return yaml.dump(bank.to_dict())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate sysex for Morningstar MC6 mk2')
    parser.add_argument('file', type=str,
                        help='sysex file')
    parser.add_argument('-o', '--output', type=str,
                        help='output as file')

    args = vars(parser.parse_args())

    if os.path.isdir(args["file"]):
        files = os.listdir(args["file"])
        if args["output"] and not os.path.isdir(args["output"]):
            print("Input file is a directory, but output file is not")
            exit(2)

        for inputfilename in files:
            if '.yml' not in inputfilename:
                continue

            output_filename = inputfilename.replace('.yml', '.syx')

            output = process_file(os.path.join(args["file"], inputfilename))
            with open(os.path.join(args["output"], output_filename), 'w') as outputfile:
                outputfile.write(output)
    else:
        print(process_file(args["file"]))
