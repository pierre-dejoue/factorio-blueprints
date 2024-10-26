#!/usr/bin/env python
"""
Module and command line tool to parse map exchange strings from the game Factorio (https://www.factorio.com/)

  With good information from: https://wiki.factorio.com/Map_exchange_string_format

  The binary format of the map exchange data was modified multiple times, and to my knowledge there is no exhaustive
  documentation of the different formats. For that reason this script is limited to the most basic parsing.
"""
__author__ = "Pierre DEJOUE"
__copyright__ = "Copyright (c) 2019 Pierre DEJOUE"
__license__ = "MIT License"
__version__ = "0.1"


import argparse
import base64
import zlib


DEFAULT_OUTPUT_MAP_DATA_FILE = 'out.dat'


def parse_map_exchange_string(map_ex_str: str) -> tuple[bytes, bool]:
    assert len(map_ex_str) >= 6
    assert map_ex_str[0:3] == '>>>'
    assert map_ex_str[-3:] == '<<<'
    map_base64 = map_ex_str[3:-3]
    raw_data = base64.b64decode(map_base64)
    compressed = True
    try:
        map_data = zlib.decompress(raw_data)
    except zlib.error:
        # Uncompressed (the map data wasn't compressed prior to 0.16)
        compressed = False
        map_data = raw_data
    return map_data, compressed


def parse_game_version(map_bytes: bytes) -> str:
    assert len(map_bytes) >= 8
    version_major = (map_bytes[1] << 8) + map_bytes[0]
    version_minor = (map_bytes[3] << 8) + map_bytes[2]
    version_patch = (map_bytes[5] << 8) + map_bytes[4]
    version_dev   = (map_bytes[7] << 8) + map_bytes[6]
    version_str = f'{version_major}.{version_minor}.{version_patch}'
    if version_dev != 0:
        version_str = f'{version_str}.{version_dev}'
    return version_str


def process_map_exchange_string(map_ex_str: str, args: argparse.Namespace):
    map_bytes, compressed = parse_map_exchange_string(map_ex_str)
    version_str = parse_game_version(map_bytes)
    if args.map_version:
        print(version_str)
    else:
        print('Version: ' + version_str)
        print('Compressed: ' + str(compressed))
        out_file = args.out_bin_file
        with open(out_file, 'wb') as f:
            f.write(map_bytes)
            print('Raw data written to file: ' + out_file)


def main():
    result = 0
    parser = argparse.ArgumentParser(description='Parse map exchange strings from the game Factorio (https://www.factorio.com/)')
    parser.add_argument('-s', '--from-string', metavar='EXCHANGE_STRING', dest='map_exchange_string', nargs=1, help='From a map exchange string')
    parser.add_argument('-f', '--from-file', metavar='FILE', dest='map_file', nargs=1, help='From a file with one map exchange string per line')
    parser.add_argument('-o', '--output', metavar='FILE', dest='out_bin_file', nargs=1, default = DEFAULT_OUTPUT_MAP_DATA_FILE, help='Output map exchange data in binary format')
    parser.add_argument('--version', dest='map_version', action='store_true', help='Print out the version of the game that generated the map')
    args = parser.parse_args()

    # Parse maps and map books
    if args.map_exchange_string:
        assert not args.map_file, 'Incompatible options -s and -f'
        process_map_exchange_string(args.map_exchange_string[0], args)
    elif args.map_file:
        assert not args.map_exchange_string, 'Incompatible options -f and -s'
        map_file = args.map_file[0]
        with open(map_file, 'rt', encoding='ascii') as f:
            for map_exchange_string in f:
                process_map_exchange_string(map_exchange_string.strip(), args)

    return result


if __name__ == "__main__":
    main()
