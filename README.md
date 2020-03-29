# YAML Morningstar MC6 II Programmer

This project is a 3rd party programmer tool for the Morningstar MC6 mk II MIDI controller written in Python. It allows you to manage banks and presets as YAML files rather than as pure sysex data. This means you can easily review, edit, and merge changes between banks in a text editor without needing the Morningstar GUI tool or physical device present.

This project is not affiliated with Morningstar in any way and has no support or warranty, official or otherwise.

**This is currently in DEVELOPMENT- ie it does not fully work yet!!!!**

## How to use the tool

I am assuming users will be familiar with Python to some degree. 
The tool takes a custom YAML file and converts to a sysex format which can be imported with the morningstar editor.
 
 
Usage is as follows: 

```
python ~/morningstarmidi/morningstar/yaml_converter.py -h
usage: yaml_converter.py [-h] [-o OUTPUT] [-s SEND] [-d MIDI_DEVICE] file

Generate sysex for Morningstar MC6 mk2

positional arguments:
  file                  yaml bank file

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output as file
  -s, --send            attempt to send directly to device
  -d MIDI_DEVICE, --midi-device MIDI_DEVICE
                        alternate midi device name (default is "Morningstar MC6MK2")
  -b BANK, --bank BANK  export specific bank number
```



# Sysex Documentation

The Morningstar MC6 II is programmed using MIDI sysex commands for which no documentation is made publicly available by Morningstar. 
Some sysex commands such as bank up/down are replicable with MIDI CC messages according to https://morningstar-engineering.github.io/MC6-MKII-Midi-Controller/site/09-midi-implementation/
Other commands such as downloading and uploading patches and banks are not available without sysex. 

Use the below information for whatever purpose you like, remember that since Morningstar do not document this protocol it is subject to change with a firmware update without notice.
If you republish this information it is always nice to receive credit or a link. If you have corrections or improvements, please submit a pull request. If you're building something cool, let me know!

## Bank Sysex Format

All lines start with the following header (all values hex)

`START_BYTE, MANUFACTURER_ID_1, MANUFACTURER_ID_2, MANUFACTURER_ID_3, DEVICE_ID, VERSION_ID`
 
 `F0 00 21 24 03 03` 
 
### Device IDs

MC 6 (presume mk ii) ID 3
MC8 ID 4

All lines have the following footer (see sysex function section for checksum function)

`[CHECKSUM, F7]`

### Bank settings

The first three and last lines of the bank sysex are for the bank settings

1: `02 02 00 00 00 00 00 00 00 00`

2: `01 11 00 00 00 00 00 00 00 00`

3: `01 06 00 00 00 00 00 00 00 00 00 00` + `BANK NAME (24 bytes of ASCII padded with 0)`

Lines 4 - 15 are for 6 x 2 pages of presets A - L respectively

Line 16 - 17 are for the two expression pedal slots

18: `7e 00 1c 00 00 00 00 00 00 00` (toggle states? expr states? bank clear ?)


### Preset settings

`01 07 00 00 00 00 00 00 00 00 01 01 00 00 02 01 01 03 00 00 05 03 02 05 06 00 06 06 03 08 09 00 08 09 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00`

01 07 00 looks like line header

00 preset number 1 - 12

6 bytes of 00 padding

16 lots of 6 bytes (96/0x60 bytes)
```
data1 data2 data3 channel type action toggle
```

Last 2 bytes are a 16 bit field for "toggle mode 0x0800" and "preset blink 0x0400"

Preset Name: 8 bytes (starting from 0x6C)

Toggle Name: 8 bytes (starting from 0x74)

Long name: 24 bytes (starting from 0x7C)

#### Preset Action Types
```
00: No action
01: Press
02: Release
03: Long Press
04: Long Press Release
05: Double Tap
06: Double Tap Release
07: Long Double Tap
08: Long Double Tap Release
09: Release All
```

### Preset MIDI Messages

```
00: Empty
01: Program Change
02: Control Change
03: Note On
04: Note off
05: Real time
06: SysEx
07: Midi Clock
08: PC Scroll Up
09: PC Scroll Down
10: Device Bank Up
11: Device Bank Down
12: Device Bank Change Mode
13: Device Set Bank
14: Device Toggle Page
15: Device Toggle Preset
16: Device Set Midi thru
17: Device Select Expression Pedal message
18: Device Looper Mode
19: Strymon Bank Up
20: Strymon Bank Down
21: AxeFX Tuner
23: Delay
24: Midi Clock Tap
```

### Expression Settings

Example

`01 08 00 00 00 00 00 00 00 00 01 01 02 03 00 03 02 05 06 00 00 06 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00`

Preset Name: 8 bytes (starting from 0x6C)

Toggle Name: 8 bytes (starting from 0x74)

Long name: 24 bytes (starting from 0x7C)

#### Expression Action Types

```
0: Empty
1: Expression CC
2: CC Toe Down
3: CC Heel Down
4: Toe Down Toggle Channel
5: Toe Down Toggle CC
```


## Sysex Commands

The format of a 'command' to the MC6 looks like this (values in hex).

### Header 6 bytes
`[START_BYTE, MANUFACTURER_ID_1, MANUFACTURER_ID_2, MANUFACTURER_ID_3, DEVICE_ID, VERSION_ID]`

### Footer 2 bytes 
`[CHECKSUM, F7]`

#### Checksum function:

Accumulate a bitwise XOR for each byte in the first 14 bytes of the message, remove most significant (8th) bit. (Python example in repository)

### Message Body 8 bytes
Default all values to 0
`[FUNCTION_BYTE_1, FUNCTION_BYTE_2, ?, ?, BANK, PRESET, EXPRESSION, ?]`


## Preconstucted function packets

`F0 00 21 24 00 00 00 10 00 00 00 00 00 00 65 F7`  Bank Up (0 16)

`F0 00 21 24 00 00 00 11 00 00 00 00 00 00 64 F7`  Bank Down (0 17)

`F0 00 21 24 00 00 00 12 00 00 00 00 00 00 67 F7`  Copy Bank (0 18)

`F0 00 21 24 00 00 00 13 00 00 00 00 00 00 66 F7`  Paste Bank (0 19)

`F0 00 21 24 00 00 00 14 00 00 00 00 00 00 61 F7`  Copy Preset (0 20)

`F0 00 21 24 00 00 00 15 00 00 00 00 00 00 60 F7`  Paste Preset (0 21)

`F0 00 21 24 00 00 00 16 00 00 00 00 00 00 63 F7`  Copy Expression Preset (0 22)

`F0 00 21 24 00 00 00 17 00 00 00 00 00 00 62 F7`  Paste Expression Preset (0 23)

`F0 00 21 24 00 00 00 20 00 00 00 00 00 00 55 F7`  Toggle Editor Mode (0 32)

`F0 00 21 24 00 00 00 21 00 00 00 00 00 00 54 F7`  Toggle Page (0 33)

`F0 00 21 24 00 00 00 22 00 00 00 00 00 00 57 F7`  Toggle Preset (0 34)

`F0 00 21 24 00 00 10 01 00 00 00 00 00 00 64 F7`  Dump All (16 1)

`F0 00 21 24 00 00 10 02 00 00 00 00 00 00 67 F7`  Dump Bank (16 2)

`F0 00 21 24 00 00 03 00 00 00 00 00 00 00 76 F7`  Send Next (3 0 BANK NUMBER, PRESET NUMBER, IS EXPRESSION) (3 23 also appears to do something)

`F0 00 21 24 00 00 03 00 01 01 00 00 00 00 76 F7`

`F0 00 21 24 00 00 03 00 01 02 00 00 00 00 75 F7`

`F0 00 21 24 00 00 03 00 01 03 00 00 00 00 74 F7`

`F0 00 21 24 00 00 00 7D 00 00 00 00 00 00 08 F7`  Ping (0 125)

`F0 00 21 24 00 00 00 7F 00 00 00 00 00 00 0A F7`  Acknowledge (0 127)



