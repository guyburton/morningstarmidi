# Morningstar MC6 II Programmer

The Morningstar MC6 II is programmed using MIDI sysex commands for which no documentation exists. I am mainly interested in the preset and bank sysex formats, but will document all that I come to understand here. Some sysex commands such as bank up/down are replicable with MIDI CC messages according to https://morningstar-engineering.github.io/MC6-MKII-Midi-Controller/site/09-midi-implementation/
Other commands such as downloading and uploading patches and banks are not available without sysex. 

Use the below information for whatever purpose you like, remember that since Morningstar do not document this protocol it is subject to change with a firmware update without notice.
If you republish this information it is always nice to receive credit or a link. If you have corrections or improvements, please submit a pull request. If you're building something cool, let me know!

## Bank Sysex Format

All lines start with the following header (all values hex)

`START_BYTE, MANUFACTURER_ID_1, MANUFACTURER_ID_2, MANUFACTURER_ID_3, DEVICE_ID, VERSION_ID`
 
 `F0 00 21 24 03 03` 

All lines have the following footer (see below for checksum function)

`[CHECKSUM, F7]`


### Bank settings
The first three and last lines of the bank sysex are for the bank settings

1: `02 02 00 00 00 00 00 00 00 00`

2: `01 11 00 00 00 00 00 00 00 00`

3: `01 06 00 00 00 00 00 00 00 00 00 00` `BANK NAME (24 bytes of ASCII)`

Lines 4 - 15 are for 6 x 2 pages of presets A - L respectively

Line 16 - 17 are for the two expression pedal slots

18: `7e 00 1c 00 00 00 00 00 00 00` (toggle states? expr states?)


### Preset settings

`01 07 00 00 00 00 00 00 00 00 01 01 00 00 02 01 01 03 00 00 05 03 02 05 06 00 06 06 03 08 09 00 08 09 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00`

Preset Name: 8 bytes (starting from 0x6C)

Toggle Name: 8 bytes (starting from 0x74)

Long name: 24 bytes (starting from 0x7C)

### Expression Settings

Example

`01 08 00 00 00 00 00 00 00 00 01 01 02 03 00 03 02 05 06 00 00 06 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00`

Preset Name: 8 bytes (starting from 0x6C)

Toggle Name: 8 bytes (starting from 0x74)

Long name: 24 bytes (starting from 0x7C)


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

`F0 00 21 24 00 00 00 7D 00 00 00 00 00 00 08 F7`  Ping (0 125)



