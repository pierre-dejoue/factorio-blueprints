#!/usr/bin/env python
"""
Command line tool to parse map exchange strings from the game Factorio (https://www.factorio.com/)
"""
__author__ = "Pierre DEJOUE"
__copyright__ = "Copyright (c) 2019 Pierre DEJOUE"
__license__ = "MIT License"
__version__ = "0.1"


import argparse
from factorio_game.exchange_string import maps


DEFAULT_OUTPUT_MAP_DATA_FILE = 'out.dat'


def process_map_exchange_string(map_ex_str: str, args: argparse.Namespace):
    map_bytes, compressed = maps.parse_exchange_string(map_ex_str)
    version_str = maps.parse_game_version(map_bytes)
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
