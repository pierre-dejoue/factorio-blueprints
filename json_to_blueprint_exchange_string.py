#!/usr/bin/env python
"""
Generate a blueprint exchange string for the game Factorio from a JSON file
"""
__author__ = "Pierre DEJOUE"
__copyright__ = "Copyright (c) 2019 Pierre DEJOUE"
__license__ = "MIT License"
__version__ = "0.1"


import argparse
import configparser
import json
import os
import sys
from factorio_game.exchange_string import blueprints


CONFIG_FILE = 'config.ini'
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


try:
    config = configparser.ConfigParser()
    config.read(os.path.join(SCRIPT_PATH, CONFIG_FILE))
    EXCHANGE_STRINGS_VERSION = config.getint('blueprints', 'version', fallback = blueprints.DEFAULT_EXCHANGE_STRINGS_VERSION)
    DB_PATH = config.get('blueprints-db', 'location')
except configparser.Error as err:
    print('Error parsing ' + CONFIG_FILE + ': ' + str(err))
    sys.exit(-1)


def main():
    parser = argparse.ArgumentParser(description='Generate a blueprint exchange string for the game Factorio from a JSON file')
    parser.add_argument('filename', metavar='FILE', help='Blueprint file in the JSON format')
    args = parser.parse_args()

    with open(args.filename, 'rt', encoding='ascii') as f:
        blueprint_json_str = f.read()
        blueprint_obj = json.loads(blueprint_json_str)
        print(blueprints.generate_exchange_string_from_json_object(blueprint_obj, EXCHANGE_STRINGS_VERSION))


if __name__ == "__main__":
    main()
